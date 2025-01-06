import unittest
from typing import List, Tuple

from metasequoia_java import ast
from metasequoia_java.ast import TreeKind, constants
from metasequoia_java.grammar.parans_result import ParensResult
from metasequoia_java.grammar.parser import JavaParser, JavaSyntaxError
from metasequoia_java.lexical import LexicalFSM
from metasequoia_java.lexical import TokenKind


class LexicalTest(unittest.TestCase):
    """测试用例"""

    @staticmethod
    def _lexical_parse(script: str) -> List[Tuple[TokenKind, str]]:
        lexical_fsm = LexicalFSM(script)
        token_list = []
        while token := lexical_fsm.lex():
            if token.kind == TokenKind.EOF:
                break
            token_list.append((token.kind, token.source))
        return token_list

    def test_identifier(self):
        self.assertEqual(ast.IdentifierTree(kind=TreeKind.IDENTIFIER, name="abc", source="abc",
                                            start_pos=0, end_pos=3),
                         JavaParser(LexicalFSM("abc")).ident())
        with self.assertRaises(JavaSyntaxError):
            JavaParser(LexicalFSM("public")).ident()
        with self.assertRaises(JavaSyntaxError):
            JavaParser(LexicalFSM("null")).ident()

    def test_type_identifier(self):
        self.assertEqual(ast.IdentifierTree(kind=TreeKind.IDENTIFIER, name="abc", source="abc",
                                            start_pos=0, end_pos=3),
                         JavaParser(LexicalFSM("abc")).type_name())
        with self.assertRaises(JavaSyntaxError):
            JavaParser(LexicalFSM("public")).type_name()
        with self.assertRaises(JavaSyntaxError):
            JavaParser(LexicalFSM("permits")).type_name()

    def test_literal(self):
        # 整型
        self.assertEqual(
            ast.IntLiteralTree(kind=TreeKind.INT_LITERAL, style=constants.IntegerStyle.DEC, value=1, source="1",
                               start_pos=0, end_pos=1),
            JavaParser(LexicalFSM("1")).literal())
        self.assertEqual(
            ast.IntLiteralTree(kind=TreeKind.INT_LITERAL, style=constants.IntegerStyle.OCT, value=8, source="010",
                               start_pos=0, end_pos=3),
            JavaParser(LexicalFSM("010")).literal())
        self.assertEqual(
            ast.IntLiteralTree(kind=TreeKind.INT_LITERAL, style=constants.IntegerStyle.HEX, value=255, source="0xFF",
                               start_pos=0, end_pos=4),
            JavaParser(LexicalFSM("0xFF")).literal())

        # 长整型
        self.assertEqual(
            ast.LongLiteralTree(kind=TreeKind.LONG_LITERAL, style=constants.IntegerStyle.DEC, value=1, source="1L",
                                start_pos=0, end_pos=2),
            JavaParser(LexicalFSM("1L")).literal())
        self.assertEqual(
            ast.LongLiteralTree(kind=TreeKind.LONG_LITERAL, style=constants.IntegerStyle.OCT, value=8, source="010L",
                                start_pos=0, end_pos=4),
            JavaParser(LexicalFSM("010L")).literal())
        self.assertEqual(
            ast.LongLiteralTree(kind=TreeKind.LONG_LITERAL, style=constants.IntegerStyle.HEX, value=255, source="0xFFL",
                                start_pos=0, end_pos=5),
            JavaParser(LexicalFSM("0xFFL")).literal())

        # 单精度浮点数
        self.assertEqual(ast.FloatLiteralTree(kind=TreeKind.FLOAT_LITERAL, value=1.0, source="1.0f",
                                              start_pos=0, end_pos=4),
                         JavaParser(LexicalFSM("1.0f")).literal())

        # 双精度浮点数
        self.assertEqual(ast.DoubleLiteralTree(kind=TreeKind.DOUBLE_LITERAL, value=1.0, source="1.0",
                                               start_pos=0, end_pos=3),
                         JavaParser(LexicalFSM("1.0")).literal())

        # 布尔值
        self.assertEqual(ast.TrueLiteralTree(kind=TreeKind.BOOLEAN_LITERAL, source="true", start_pos=0, end_pos=4),
                         JavaParser(LexicalFSM("true")).literal())
        self.assertEqual(ast.FalseLiteralTree(kind=TreeKind.BOOLEAN_LITERAL, source="false", start_pos=0, end_pos=5),
                         JavaParser(LexicalFSM("false")).literal())

        # 字符字面值
        self.assertEqual(ast.CharacterLiteralTree(kind=TreeKind.CHAR_LITERAL, value="a", source="'a'",
                                                  start_pos=0, end_pos=3),
                         JavaParser(LexicalFSM("'a'")).literal())

        # 字符串字面值
        self.assertEqual(
            ast.StringLiteralTree(kind=TreeKind.STRING_LITERAL, style=constants.StringStyle.TEXT_BLOCK, value="a",
                                  source="\"\"\"a\"\"\"", start_pos=0, end_pos=7),
            JavaParser(LexicalFSM("\"\"\"a\"\"\"")).literal())
        self.assertEqual(
            ast.StringLiteralTree(kind=TreeKind.STRING_LITERAL, style=constants.StringStyle.STRING, value="a",
                                  source="\"a\"", start_pos=0, end_pos=3),
            JavaParser(LexicalFSM("\"a\"")).literal())

        # 空值字面值
        self.assertEqual(ast.NullLiteralTree(kind=TreeKind.NULL_LITERAL, source="null", start_pos=0, end_pos=4),
                         JavaParser(LexicalFSM("null")).literal())

    def test_qualident(self):
        res = JavaParser(LexicalFSM("abc.def")).qualident(False)
        self.assertIsInstance(res, ast.MemberSelectTree)
        self.assertEqual(TreeKind.MEMBER_SELECT, res.kind)
        self.assertEqual("abc.def", res.source)
        self.assertEqual(0, res.start_pos)
        self.assertEqual(7, res.end_pos)
        self.assertEqual(TreeKind.IDENTIFIER, res.expression.kind)
        self.assertEqual("abc", res.expression.source)
        self.assertEqual(0, res.expression.start_pos)
        self.assertEqual(3, res.expression.end_pos)
        self.assertEqual(TreeKind.IDENTIFIER, res.identifier.kind)
        self.assertEqual("def", res.identifier.source)
        self.assertEqual(4, res.identifier.start_pos)
        self.assertEqual(7, res.identifier.end_pos)

    def test_peek_token(self):
        self.assertTrue(JavaParser(LexicalFSM("1 + 2")).peek_token(0, TokenKind.PLUS))
        self.assertTrue(JavaParser(LexicalFSM("1 + 2")).peek_token(0, TokenKind.PLUS, TokenKind.INT_DEC_LITERAL))
        self.assertTrue(JavaParser(LexicalFSM("1 + 2")).peek_token(0, TokenKind.PLUS, TokenKind.INT_DEC_LITERAL,
                                                                   TokenKind.EOF))

    def test_skip_annotation(self):
        self.assertEqual(4, JavaParser(LexicalFSM("@abc(de) xxx")).skip_annotation(0))
        self.assertEqual(1, JavaParser(LexicalFSM("@interface xxx")).skip_annotation(0))

    def test_analyze_parens(self):
        self.assertEqual(ParensResult.PARENS, JavaParser(LexicalFSM("(1 + 2)")).analyze_parens())
        self.assertEqual(ParensResult.CAST, JavaParser(LexicalFSM("(int)")).analyze_parens())
        self.assertEqual(ParensResult.IMPLICIT_LAMBDA, JavaParser(LexicalFSM("(a, b)")).analyze_parens())
        self.assertEqual(ParensResult.PARENS, JavaParser(LexicalFSM("(i % 2 == 0)")).analyze_parens())
        self.assertEqual(ParensResult.EXPLICIT_LAMBDA, JavaParser(LexicalFSM("(Integer i)")).analyze_parens())
        self.assertEqual(ParensResult.CAST, JavaParser(LexicalFSM("(String) b")).analyze_parens())

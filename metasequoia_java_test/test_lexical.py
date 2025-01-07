"""
词法解析器单元测试
"""

import unittest
from typing import List, Tuple

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

    def _assert_equal(self, script: str, answer: List[Tuple[TokenKind, str]]):
        tokens = self._lexical_parse(script)
        self.assertEqual(answer, tokens)

    def _assert_raise(self, script: str):
        with self.assertRaises(Exception):
            self._lexical_parse(script)

    def testcase_basic_mark(self):
        """测试基础元素终结符的解析场景"""
        # IDENTIFIER
        self._assert_equal("abc", [
            (TokenKind.IDENTIFIER, "abc"),
        ])

        # BRACE_OPEN + BRACE_CLOSE
        self._assert_equal("{abc}", [
            (TokenKind.LBRACE, "{"),
            (TokenKind.IDENTIFIER, "abc"),
            (TokenKind.RBRACE, "}"),
        ])

        # SQUARE_OPEN + SQUARE_CLOSE
        self._assert_equal("[abc]", [
            (TokenKind.LBRACKET, "["),
            (TokenKind.IDENTIFIER, "abc"),
            (TokenKind.RBRACKET, "]"),
        ])

        # SQUARE_OPEN + SQUARE_CLOSE
        self._assert_equal("(abc)", [
            (TokenKind.LPAREN, "("),
            (TokenKind.IDENTIFIER, "abc"),
            (TokenKind.RPAREN, ")"),
        ])

        # ANGLE_OPEN + ANGLE_CLOSE
        self._assert_equal("<abc>", [
            (TokenKind.LT, "<"),
            (TokenKind.IDENTIFIER, "abc"),
            (TokenKind.GT, ">"),
        ])

        # DOT
        self._assert_equal("abc.def", [
            (TokenKind.IDENTIFIER, "abc"),
            (TokenKind.DOT, "."),
            (TokenKind.IDENTIFIER, "def"),
        ])

        # SEMICOLON
        self._assert_equal("abc;", [
            (TokenKind.IDENTIFIER, "abc"),
            (TokenKind.SEMI, ";"),
        ])

        # COLON
        self._assert_equal("abc:", [
            (TokenKind.IDENTIFIER, "abc"),
            (TokenKind.COLON, ":"),
        ])

        # COMMA
        self._assert_equal("abc,def", [
            (TokenKind.IDENTIFIER, "abc"),
            (TokenKind.COMMA, ","),
            (TokenKind.IDENTIFIER, "def"),
        ])

        # AT
        self._assert_equal("@(abc)", [
            (TokenKind.MONKEYS_AT, "@"),
            (TokenKind.LPAREN, "("),
            (TokenKind.IDENTIFIER, "abc"),
            (TokenKind.RPAREN, ")"),
        ])

    def test_literal(self):
        """测试字面值的解析场景"""

        # INT_DEC_LITERAL
        self._assert_equal("10", [
            (TokenKind.INT_DEC_LITERAL, "10"),
        ])

        # LIT_LONG
        self._assert_equal("0L", [
            (TokenKind.LONG_DEC_LITERAL, "0L"),
        ])
        self._assert_equal("10L", [
            (TokenKind.LONG_DEC_LITERAL, "10L"),
        ])

        # 八进制整型
        self._assert_equal("012", [
            (TokenKind.INT_OCT_LITERAL, "012"),
        ])
        # 八进制长整型
        self._assert_equal("012L", [
            (TokenKind.LONG_OCT_LITERAL, "012L"),
        ])

        # 十六进制整型
        self._assert_equal("0x0A", [
            (TokenKind.INT_HEX_LITERAL, "0x0A"),
        ])
        self._assert_equal("0X0a", [
            (TokenKind.INT_HEX_LITERAL, "0X0a"),
        ])
        # 十六进制长整型
        self._assert_equal("0x0AL", [
            (TokenKind.LONG_HEX_LITERAL, "0x0AL"),
        ])

        # FLOAT_LITERAL
        self._assert_equal("3.14f", [
            (TokenKind.FLOAT_LITERAL, "3.14f"),
        ])
        self._assert_equal(".14f", [
            (TokenKind.FLOAT_LITERAL, ".14f"),
        ])
        self._assert_equal("3.f", [
            (TokenKind.FLOAT_LITERAL, "3.f"),
        ])
        self._assert_equal("0.5f", [
            (TokenKind.FLOAT_LITERAL, "0.5f"),
        ])

        # DOUBLE_LITERAL
        self._assert_equal("3.14", [
            (TokenKind.DOUBLE_LITERAL, "3.14"),
        ])
        self._assert_equal(".14", [
            (TokenKind.DOUBLE_LITERAL, ".14"),
        ])
        self._assert_equal("3.", [
            (TokenKind.DOUBLE_LITERAL, "3."),
        ])
        self._assert_equal("3.14d", [
            (TokenKind.DOUBLE_LITERAL, "3.14d"),
        ])
        self._assert_equal(".14d", [
            (TokenKind.DOUBLE_LITERAL, ".14d"),
        ])
        self._assert_equal("3.d", [
            (TokenKind.DOUBLE_LITERAL, "3.d"),
        ])

        # DOUBLE_LITERAL（科学记数法）
        self._assert_equal("3.14e1", [
            (TokenKind.DOUBLE_LITERAL, "3.14e1"),
        ])
        self._assert_equal("3.14e-1", [
            (TokenKind.DOUBLE_LITERAL, "3.14e-1"),
        ])
        self._assert_equal(".14e-1", [
            (TokenKind.DOUBLE_LITERAL, ".14e-1"),
        ])
        self._assert_equal("3.e-4", [
            (TokenKind.DOUBLE_LITERAL, "3.e-4"),
        ])

        # CHAR_LITERAL
        self._assert_equal("'A'", [
            (TokenKind.CHAR_LITERAL, "'A'"),
        ])
        self._assert_equal(r"'\''", [
            (TokenKind.CHAR_LITERAL, r"'\''"),
        ])

        # STRING_LITERAL
        self._assert_equal("\"Hello, World!\"", [
            (TokenKind.STRING_LITERAL, "\"Hello, World!\""),
        ])
        self._assert_equal("\"Hello, \\\"World\\\"!\"", [
            (TokenKind.STRING_LITERAL, "\"Hello, \\\"World\\\"!\""),
        ])

        # LIT_TRUE
        self._assert_equal("true", [
            (TokenKind.TRUE, "true"),
        ])

        # LIT_FALSE
        self._assert_equal("false", [
            (TokenKind.FALSE, "false"),
        ])

        # LIT_NULL
        self._assert_equal("null", [
            (TokenKind.NULL, "null"),
        ])

    def test_keyword(self):
        """测试关键字"""
        self._assert_equal("abstract", [
            (TokenKind.ABSTRACT, "abstract"),
        ])
        self._assert_equal("assert", [
            (TokenKind.ASSERT, "assert"),
        ])
        self._assert_equal("boolean", [
            (TokenKind.BOOLEAN, "boolean"),
        ])
        self._assert_equal("break", [
            (TokenKind.BREAK, "break"),
        ])
        self._assert_equal("byte", [
            (TokenKind.BYTE, "byte"),
        ])
        self._assert_equal("case", [
            (TokenKind.CASE, "case"),
        ])
        self._assert_equal("catch", [
            (TokenKind.CATCH, "catch"),
        ])
        self._assert_equal("char", [
            (TokenKind.CHAR, "char"),
        ])
        self._assert_equal("class", [
            (TokenKind.CLASS, "class"),
        ])
        self._assert_equal("continue", [
            (TokenKind.CONTINUE, "continue"),
        ])
        self._assert_equal("default", [
            (TokenKind.DEFAULT, "default"),
        ])
        self._assert_equal("do", [
            (TokenKind.DO, "do"),
        ])
        self._assert_equal("double", [
            (TokenKind.DOUBLE, "double"),
        ])
        self._assert_equal("else", [
            (TokenKind.ELSE, "else"),
        ])
        self._assert_equal("enum", [
            (TokenKind.ENUM, "enum"),
        ])
        self._assert_equal("extends", [
            (TokenKind.EXTENDS, "extends"),
        ])
        self._assert_equal("final", [
            (TokenKind.FINAL, "final"),
        ])
        self._assert_equal("finally", [
            (TokenKind.FINALLY, "finally"),
        ])
        self._assert_equal("float", [
            (TokenKind.FLOAT, "float"),
        ])
        self._assert_equal("for", [
            (TokenKind.FOR, "for"),
        ])
        self._assert_equal("if", [
            (TokenKind.IF, "if"),
        ])
        self._assert_equal("implements", [
            (TokenKind.IMPLEMENTS, "implements"),
        ])
        self._assert_equal("import", [
            (TokenKind.IMPORT, "import"),
        ])
        self._assert_equal("int", [
            (TokenKind.INT, "int"),
        ])
        self._assert_equal("interface", [
            (TokenKind.INTERFACE, "interface"),
        ])
        self._assert_equal("instanceof", [
            (TokenKind.INSTANCEOF, "instanceof"),
        ])
        self._assert_equal("long", [
            (TokenKind.LONG, "long"),
        ])
        self._assert_equal("native", [
            (TokenKind.NATIVE, "native"),
        ])
        self._assert_equal("new", [
            (TokenKind.NEW, "new"),
        ])
        self._assert_equal("package", [
            (TokenKind.PACKAGE, "package"),
        ])
        self._assert_equal("private", [
            (TokenKind.PRIVATE, "private"),
        ])
        self._assert_equal("protected", [
            (TokenKind.PROTECTED, "protected"),
        ])
        self._assert_equal("public", [
            (TokenKind.PUBLIC, "public"),
        ])
        self._assert_equal("return", [
            (TokenKind.RETURN, "return"),
        ])
        self._assert_equal("short", [
            (TokenKind.SHORT, "short"),
        ])
        self._assert_equal("static", [
            (TokenKind.STATIC, "static"),
        ])
        self._assert_equal("strictfp", [
            (TokenKind.STRICTFP, "strictfp"),
        ])
        self._assert_equal("super", [
            (TokenKind.SUPER, "super"),
        ])
        self._assert_equal("switch", [
            (TokenKind.SWITCH, "switch"),
        ])
        self._assert_equal("synchronized", [
            (TokenKind.SYNCHRONIZED, "synchronized"),
        ])
        self._assert_equal("this", [
            (TokenKind.THIS, "this"),
        ])
        self._assert_equal("throw", [
            (TokenKind.THROW, "throw"),
        ])
        self._assert_equal("throws", [
            (TokenKind.THROWS, "throws"),
        ])
        self._assert_equal("transient", [
            (TokenKind.TRANSIENT, "transient"),
        ])
        self._assert_equal("try", [
            (TokenKind.TRY, "try"),
        ])
        self._assert_equal("void", [
            (TokenKind.VOID, "void"),
        ])
        self._assert_equal("volatile", [
            (TokenKind.VOLATILE, "volatile"),
        ])
        self._assert_equal("while", [
            (TokenKind.WHILE, "while"),
        ])
        self._assert_equal("goto", [
            (TokenKind.GOTO, "goto"),
        ])
        self._assert_equal("const", [
            (TokenKind.CONST, "const"),
        ])
        self._assert_equal("_", [
            (TokenKind.UNDERSCORE, "_"),
        ])

    def test_operator(self):
        """测试运算符"""
        self._assert_equal("->", [(TokenKind.ARROW, "->")])
        self._assert_equal("...", [(TokenKind.ELLIPSIS, "...")])
        self._assert_equal("&=", [(TokenKind.AMP_EQ, "&=")])
        self._assert_equal("|=", [(TokenKind.BAR_EQ, "|=")])
        self._assert_equal("^=", [(TokenKind.CARET_EQ, "^=")])
        self._assert_equal("<<=", [(TokenKind.LT_LT_EQ, "<<=")])
        self._assert_equal(">>=", [(TokenKind.GT_GT_EQ, ">>=")])
        self._assert_equal(">>>=", [(TokenKind.GT_GT_GT_EQ, ">>>=")])

        # OP_CAL_ADD
        self._assert_equal("1+2", [
            (TokenKind.INT_DEC_LITERAL, "1"),
            (TokenKind.PLUS, "+"),
            (TokenKind.INT_DEC_LITERAL, "2"),
        ])

        # OP_CAL_SUB
        self._assert_equal("1-2", [
            (TokenKind.INT_DEC_LITERAL, "1"),
            (TokenKind.SUB, "-"),
            (TokenKind.INT_DEC_LITERAL, "2"),
        ])

        # OP_CAL_MULT
        self._assert_equal("1*2", [
            (TokenKind.INT_DEC_LITERAL, "1"),
            (TokenKind.STAR, "*"),
            (TokenKind.INT_DEC_LITERAL, "2"),
        ])

        # OP_CAL_DIV
        self._assert_equal("1/2", [
            (TokenKind.INT_DEC_LITERAL, "1"),
            (TokenKind.SLASH, "/"),
            (TokenKind.INT_DEC_LITERAL, "2"),
        ])

        # OP_CAL_MOD
        self._assert_equal("1%2", [
            (TokenKind.INT_DEC_LITERAL, "1"),
            (TokenKind.PERCENT, "%"),
            (TokenKind.INT_DEC_LITERAL, "2"),
        ])

        # OP_EQ
        self._assert_equal("1==2", [
            (TokenKind.INT_DEC_LITERAL, "1"),
            (TokenKind.EQ_EQ, "=="),
            (TokenKind.INT_DEC_LITERAL, "2"),
        ])

        # OP_NEQ
        self._assert_equal("1!=2", [
            (TokenKind.INT_DEC_LITERAL, "1"),
            (TokenKind.BANG_EQ, "!="),
            (TokenKind.INT_DEC_LITERAL, "2"),
        ])

        # OP_LTE
        self._assert_equal("1<=2", [
            (TokenKind.INT_DEC_LITERAL, "1"),
            (TokenKind.LT_EQ, "<="),
            (TokenKind.INT_DEC_LITERAL, "2"),
        ])

        # OP_GTE
        self._assert_equal("1>=2", [
            (TokenKind.INT_DEC_LITERAL, "1"),
            (TokenKind.GT_EQ, ">="),
            (TokenKind.INT_DEC_LITERAL, "2"),
        ])

        # OP_LOG_AND
        self._assert_equal("1&&2", [
            (TokenKind.INT_DEC_LITERAL, "1"),
            (TokenKind.AMP_AMP, "&&"),
            (TokenKind.INT_DEC_LITERAL, "2"),
        ])

        # OP_LOG_OR
        self._assert_equal("1||2", [
            (TokenKind.INT_DEC_LITERAL, "1"),
            (TokenKind.BAR_BAR, "||"),
            (TokenKind.INT_DEC_LITERAL, "2"),
        ])

        # OP_LOG_NOT
        self._assert_equal("!2", [
            (TokenKind.BANG, "!"),
            (TokenKind.INT_DEC_LITERAL, "2"),
        ])

        # OP_ASS_EQ
        self._assert_equal("1=2", [
            (TokenKind.INT_DEC_LITERAL, "1"),
            (TokenKind.EQ, "="),
            (TokenKind.INT_DEC_LITERAL, "2"),
        ])

        # OP_ASS_ADD
        self._assert_equal("1+=2", [
            (TokenKind.INT_DEC_LITERAL, "1"),
            (TokenKind.PLUS_EQ, "+="),
            (TokenKind.INT_DEC_LITERAL, "2"),
        ])

        # OP_ASS_SUB
        self._assert_equal("1-=2", [
            (TokenKind.INT_DEC_LITERAL, "1"),
            (TokenKind.SUB_EQ, "-="),
            (TokenKind.INT_DEC_LITERAL, "2"),
        ])

        # OP_ASS_MULT
        self._assert_equal("1*=2", [
            (TokenKind.INT_DEC_LITERAL, "1"),
            (TokenKind.STAR_EQ, "*="),
            (TokenKind.INT_DEC_LITERAL, "2"),
        ])

        # OP_ASS_DIV
        self._assert_equal("1/=2", [
            (TokenKind.INT_DEC_LITERAL, "1"),
            (TokenKind.SLASH_EQ, "/="),
            (TokenKind.INT_DEC_LITERAL, "2"),
        ])

        # OP_ASS_MOD
        self._assert_equal("1%=2", [
            (TokenKind.INT_DEC_LITERAL, "1"),
            (TokenKind.PERCENT_EQ, "%="),
            (TokenKind.INT_DEC_LITERAL, "2"),
        ])

        # OP_ADD_ADD
        self._assert_equal("1++", [
            (TokenKind.INT_DEC_LITERAL, "1"),
            (TokenKind.PLUS_PLUS, "++"),
        ])

        # OP_SUB_SUB
        self._assert_equal("1--", [
            (TokenKind.INT_DEC_LITERAL, "1"),
            (TokenKind.SUB_SUB, "--"),
        ])

        # OP_BIT_AND
        self._assert_equal("1&2", [
            (TokenKind.INT_DEC_LITERAL, "1"),
            (TokenKind.AMP, "&"),
            (TokenKind.INT_DEC_LITERAL, "2"),
        ])

        # OP_BIT_OR
        self._assert_equal("1|2", [
            (TokenKind.INT_DEC_LITERAL, "1"),
            (TokenKind.BAR, "|"),
            (TokenKind.INT_DEC_LITERAL, "2"),
        ])

        # OP_BIT_XOR
        self._assert_equal("1^2", [
            (TokenKind.INT_DEC_LITERAL, "1"),
            (TokenKind.CARET, "^"),
            (TokenKind.INT_DEC_LITERAL, "2"),
        ])

        # OP_BIT_NOT
        self._assert_equal("~2", [
            (TokenKind.TILDE, "~"),
            (TokenKind.INT_DEC_LITERAL, "2"),
        ])

        # OP_BIT_LSHIFT
        self._assert_equal("1<<2", [
            (TokenKind.INT_DEC_LITERAL, "1"),
            (TokenKind.LT_LT, "<<"),
            (TokenKind.INT_DEC_LITERAL, "2"),
        ])

        # OP_BIT_RSHIFT
        self._assert_equal("1>>2", [
            (TokenKind.INT_DEC_LITERAL, "1"),
            (TokenKind.GT_GT, ">>"),
            (TokenKind.INT_DEC_LITERAL, "2"),
        ])

        # OP_BIT_UNSIGNED_RSHIFT
        self._assert_equal("1>>>2", [
            (TokenKind.INT_DEC_LITERAL, "1"),
            (TokenKind.GT_GT_GT, ">>>"),
            (TokenKind.INT_DEC_LITERAL, "2"),
        ])

    def test_comment(self):
        """测试注释"""
        # 单行注释
        self._assert_equal("1//xxx\n2", [
            (TokenKind.INT_DEC_LITERAL, "1"),
            (TokenKind.INT_DEC_LITERAL, "2"),
        ])
        self._assert_equal("1 // xxx\n    2", [
            (TokenKind.INT_DEC_LITERAL, "1"),
            (TokenKind.INT_DEC_LITERAL, "2"),
        ])

        # 多行注释
        self._assert_equal("1/* xxx */\n2", [
            (TokenKind.INT_DEC_LITERAL, "1"),
            (TokenKind.INT_DEC_LITERAL, "2"),
        ])
        self._assert_equal("1 /* xxx */ \n2", [
            (TokenKind.INT_DEC_LITERAL, "1"),
            (TokenKind.INT_DEC_LITERAL, "2"),
        ])
        self._assert_equal("1 /** xxx **/ \n2", [
            (TokenKind.INT_DEC_LITERAL, "1"),
            (TokenKind.INT_DEC_LITERAL, "2"),
        ])

    def test_space(self):
        """测试各个位置的空格处理逻辑"""

        self._assert_equal("abc def", [
            (TokenKind.IDENTIFIER, "abc"),
            (TokenKind.IDENTIFIER, "def"),
        ])

        self._assert_equal("abc. def", [
            (TokenKind.IDENTIFIER, "abc"),
            (TokenKind.DOT, "."),
            (TokenKind.IDENTIFIER, "def"),
        ])

        self._assert_equal("abc . def", [
            (TokenKind.IDENTIFIER, "abc"),
            (TokenKind.DOT, "."),
            (TokenKind.IDENTIFIER, "def"),
        ])

        self._assert_equal("abc , def", [
            (TokenKind.IDENTIFIER, "abc"),
            (TokenKind.COMMA, ","),
            (TokenKind.IDENTIFIER, "def"),
        ])

        self._assert_equal("1 + 2", [
            (TokenKind.INT_DEC_LITERAL, "1"),
            (TokenKind.PLUS, "+"),
            (TokenKind.INT_DEC_LITERAL, "2"),
        ])

    def test_combine(self):
        """测试组合关系"""
        self._assert_equal("i+1", [
            (TokenKind.IDENTIFIER, "i"),
            (TokenKind.PLUS, "+"),
            (TokenKind.INT_DEC_LITERAL, "1"),
        ])

    def test_text_block(self):
        """测试 TextBlock"""
        self._assert_equal("\"\"\"abc\"\"\"", [
            (TokenKind.TEXT_BLOCK, "\"\"\"abc\"\"\""),
        ])

"""
测试：类声明语句解析
"""


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



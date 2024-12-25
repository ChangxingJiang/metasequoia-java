from typing import Optional

from metasequoia_java.grammar import ast
from metasequoia_java.ast.kind import TreeKind
from metasequoia_java.grammar.constants import INT_LITERAL_STYLE_HASH
from metasequoia_java.grammar.constants import LONG_LITERAL_STYLE_HASH
from metasequoia_java.grammar.constants import StringStyle
from metasequoia_java.lexical import LexicalFSM
from metasequoia_java.lexical import Token
from metasequoia_java.lexical import TokenKind


class JavaSyntaxError(Exception):
    """Java 语法错误"""


class JavaParser:
    def __init__(self, lexer: LexicalFSM):
        self._lexer = lexer
        self._token: Optional[Token] = None
        self._next_token()

    def _next_token(self):
        self._token = self._lexer.lex()

    # ------------------------------ Chapter 3 : Lexical Structure ------------------------------

    def identifier(self) -> str:
        """解析 Identifier 元素

        Identifier:
          IdentifierChars but not a ReservedKeyword or BooleanLiteral or NullLiteral
        """
        if self._token.kind != TokenKind.IDENTIFIER:
            raise JavaSyntaxError(f"{self._token.source} 不能作为 Identifier")
        value = self._token.name
        self._next_token()
        return value

    def type_identifier(self) -> str:
        """解析 TypeIdentifier 元素

        TypeIdentifier:
          Identifier but not permits, record, sealed, var, or yield
        """
        if self._token.kind != TokenKind.IDENTIFIER:
            raise JavaSyntaxError(f"{self._token.source} 不能作为 TypeIdentifier")
        if self._token.name in {"permits", "record", "sealed", "var", "yield"}:
            raise JavaSyntaxError(f"{self._token.name} 不能作为 TypeIdentifier")
        value = self._token.name
        self._next_token()
        return value

    def unqualified_method_identifier(self) -> str:
        """解析 UnqualifiedMethodIdentifier 元素

        UnqualifiedMethodIdentifier:
          Identifier but not yield
        """
        if self._token.kind != TokenKind.IDENTIFIER:
            raise JavaSyntaxError(f"{self._token.source} 不能作为 UnqualifiedMethodIdentifier")
        if self._token.name in {"yield"}:
            raise JavaSyntaxError(f"{self._token.name} 不能作为 UnqualifiedMethodIdentifier")
        value = self._token.name
        self._next_token()
        return value

    def literal(self) -> ast.LiteralTree:
        """解析 Literal 元素

        Literal:
          IntegerLiteral
          FloatingPointLiteral
          BooleanLiteral
          CharacterLiteral
          StringLiteral
          TextBlock
          NullLiteral
        """
        if self._token.kind in {TokenKind.INT_OCT_LITERAL, TokenKind.INT_DEC_LITERAL, TokenKind.INT_HEX_LITERAL}:
            return ast.IntLiteralTree(
                kind=TreeKind.INT_LITERAL,
                style=INT_LITERAL_STYLE_HASH[self._token.kind],
                value=self._token.int_value(),
                source=self._token.source
            )
        if self._token.kind in {TokenKind.LONG_OCT_LITERAL, TokenKind.LONG_DEC_LITERAL, TokenKind.LONG_HEX_LITERAL}:
            return ast.LongLiteralTree(
                kind=TreeKind.LONG_LITERAL,
                style=LONG_LITERAL_STYLE_HASH[self._token.kind],
                value=self._token.int_value(),
                source=self._token.source
            )
        if self._token.kind == TokenKind.FLOAT_LITERAL:
            return ast.FloatLiteralTree(
                kind=TreeKind.FLOAT_LITERAL,
                value=self._token.float_value(),
                source=self._token.source
            )
        if self._token.kind == TokenKind.DOUBLE_LITERAL:
            return ast.DoubleLiteralTree(
                kind=TreeKind.DOUBLE_LITERAL,
                value=self._token.float_value(),
                source=self._token.source
            )
        if self._token.kind == TokenKind.TRUE:
            return ast.TrueLiteralTree(
                kind=TreeKind.BOOLEAN_LITERAL,
                source=self._token.source
            )
        if self._token.kind == TokenKind.FALSE:
            return ast.FalseLiteralTree(
                kind=TreeKind.BOOLEAN_LITERAL,
                source=self._token.source
            )
        if self._token.kind == TokenKind.CHAR_LITERAL:
            return ast.CharacterLiteralTree(
                kind=TreeKind.CHAR_LITERAL,
                value=self._token.char_value(),
                source=self._token.source
            )
        if self._token.kind == TokenKind.STRING_LITERAL:
            return ast.StringLiteralTree(
                kind=TreeKind.STRING_LITERAL,
                style=StringStyle.STRING,
                value=self._token.string_value(),
                source=self._token.source
            )
        if self._token.kind == TokenKind.TEXT_BLOCK:
            return ast.StringLiteralTree(
                kind=TreeKind.STRING_LITERAL,
                style=StringStyle.TEXT_BLOCK,
                value=self._token.string_value(),
                source=self._token.source
            )
        if self._token.kind == TokenKind.NULL:
            return ast.NullLiteralTree(
                kind=TreeKind.NULL_LITERAL,
                source=self._token.source
            )
        raise JavaSyntaxError(f"{self._token.source} 不是字面值")

"""
Token 类型到原生类型的 TypeKind 的映射
"""

from metasequoia_java.ast import TypeKind
from metasequoia_java.lexical import TokenKind

__all__ = [
    "TOKEN_TO_TYPE_KIND",
]

TOKEN_TO_TYPE_KIND = {
    TokenKind.BYTE: TypeKind.BYTE,
    TokenKind.SHORT: TypeKind.SHORT,
    TokenKind.CHAR: TypeKind.CHAR,
    TokenKind.INT: TypeKind.INT,
    TokenKind.LONG: TypeKind.LONG,
    TokenKind.FLOAT: TypeKind.FLOAT,
    TokenKind.DOUBLE: TypeKind.DOUBLE,
    TokenKind.BOOLEAN: TypeKind.BOOLEAN,
}

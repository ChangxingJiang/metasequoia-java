"""
Token 类型到修饰符枚举值的映射
"""

from metasequoia_java.ast import Modifier
from metasequoia_java.lexical import TokenKind

__all__ = [
    "TOKEN_TO_MODIFIER",
]

TOKEN_TO_MODIFIER = {
    TokenKind.PRIVATE: Modifier.PRIVATE,
    TokenKind.PROTECTED: Modifier.PROTECTED,
    TokenKind.PUBLIC: Modifier.PUBLIC,
    TokenKind.STATIC: Modifier.STATIC,
    TokenKind.TRANSIENT: Modifier.TRANSIENT,
    TokenKind.FINAL: Modifier.FINAL,
    TokenKind.ABSTRACT: Modifier.ABSTRACT,
    TokenKind.NATIVE: Modifier.NATIVE,
    TokenKind.VOLATILE: Modifier.VOLATILE,
    TokenKind.SYNCHRONIZED: Modifier.SYNCHRONIZED,
    TokenKind.STRICTFP: Modifier.STRICTFP,
    TokenKind.DEFAULT: Modifier.DEFAULT
}

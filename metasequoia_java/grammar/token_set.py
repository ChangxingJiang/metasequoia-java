"""
Token 类型的集合
"""

from metasequoia_java.lexical import TokenKind

__all__ = [
    "LAX_IDENTIFIER"
]

# 所有类似标识符的 Token 类型的集合（Accepts all identifier-like tokens）
LAX_IDENTIFIER = TokenKind.IDENTIFIER | TokenKind.UNDERSCORE | TokenKind.ASSERT | TokenKind.ENUM

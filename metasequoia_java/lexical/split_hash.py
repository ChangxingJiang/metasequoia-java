"""
拆分 Token 后结果的映射关系
"""

from metasequoia_java.lexical.token_kind import TokenKind

__all__ = [
    "SPLIT_HASH"
]

SPLIT_HASH = {
    TokenKind.GT_GT: (TokenKind.GT, TokenKind.GT),
    TokenKind.GT_EQ: (TokenKind.GT, TokenKind.EQ),
    TokenKind.GT_GT_EQ: (TokenKind.GT, TokenKind.GT_EQ),
    TokenKind.GT_GT_GT: (TokenKind.GT, TokenKind.GT_GT),
    TokenKind.GT_GT_GT_EQ: (TokenKind.GT, TokenKind.GT_GT_EQ),
}

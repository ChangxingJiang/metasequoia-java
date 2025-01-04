"""
一元表达式运算符 Token 到 TreeKind 的映射关系
"""

from metasequoia_java.ast import TreeKind
from metasequoia_java.lexical import TokenKind

__all__ = [
    "UNARY_OPERATOR_TO_TREE_KIND"
]

# 一元表达式运算符 Token 到 TreeKind 的映射关系
UNARY_OPERATOR_TO_TREE_KIND = {
    TokenKind.PLUS: TreeKind.UNARY_PLUS,  # + a
    TokenKind.SUB: TreeKind.UNARY_MINUS,  # - a
    TokenKind.BANG: TreeKind.LOGICAL_COMPLEMENT,  # ! a
    TokenKind.TILDE: TreeKind.BITWISE_COMPLEMENT,  # ~ a
    TokenKind.PLUS_PLUS: TreeKind.PREFIX_INCREMENT,  # ++ a
    TokenKind.SUB_SUB: TreeKind.PREFIX_DECREMENT,  # -- a
}

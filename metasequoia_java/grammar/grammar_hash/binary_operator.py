"""
二元表达式运算符 Token 到 TreeKind 的映射关系
"""

from metasequoia_java.ast import TreeKind
from metasequoia_java.lexical import TokenKind

__all__ = [
    "BINARY_OPERATOR_TO_TREE_KIND"
]

# 二元表达式运算符 Token 到 TreeKind 的映射关系
BINARY_OPERATOR_TO_TREE_KIND = {
    TokenKind.BAR_BAR: TreeKind.CONDITIONAL_OR,  # ||
    TokenKind.AMP_AMP: TreeKind.CONDITIONAL_AND,  # &&
    TokenKind.BAR: TreeKind.OR,  # |
    TokenKind.CARET: TreeKind.XOR,  # ^
    TokenKind.AMP: TreeKind.AND,  # &
    TokenKind.EQ_EQ: TreeKind.EQUAL_TO,  # ==
    TokenKind.BANG_EQ: TreeKind.NOT_EQUAL_TO,  # !=
    TokenKind.LT: TreeKind.LESS_THAN,  # <
    TokenKind.GT: TreeKind.GREATER_THAN,  # >
    TokenKind.LT_EQ: TreeKind.LESS_THAN_EQUAL,  # <=
    TokenKind.GT_EQ: TreeKind.GREATER_THAN_EQUAL,  # >=
    TokenKind.LT_LT: TreeKind.LEFT_SHIFT,  # <<
    TokenKind.GT_GT: TreeKind.RIGHT_SHIFT,  # >>
    TokenKind.GT_GT_GT: TreeKind.UNSIGNED_RIGHT_SHIFT,  # >>>
    TokenKind.PLUS: TreeKind.PLUS,  # +
    TokenKind.SUB: TreeKind.MINUS,  # -
    TokenKind.STAR: TreeKind.MULTIPLY,  # *
    TokenKind.SLASH: TreeKind.DIVIDE,  # /
    TokenKind.PERCENT: TreeKind.REMAINDER,  # %
}

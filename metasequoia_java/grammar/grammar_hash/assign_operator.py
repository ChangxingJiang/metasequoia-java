"""
赋值运算符 Token 到 TreeKind 的映射关系
"""

from metasequoia_java.ast import TreeKind
from metasequoia_java.lexical import TokenKind

__all__ = [
    "ASSIGN_OPERATOR_TO_TREE_KIND"
]

# 赋值运算符 Token 到 TreeKind 的映射关系
ASSIGN_OPERATOR_TO_TREE_KIND = {
    TokenKind.PLUS_EQ: TreeKind.PLUS_ASSIGNMENT,  # +=
    TokenKind.SUB_EQ: TreeKind.MINUS_ASSIGNMENT,  # -=
    TokenKind.STAR_EQ: TreeKind.MULTIPLY_ASSIGNMENT,  # *=
    TokenKind.SLASH_EQ: TreeKind.DIVIDE_ASSIGNMENT,  # /=
    TokenKind.AMP_EQ: TreeKind.AND_ASSIGNMENT,  # $=
    TokenKind.BAR_EQ: TreeKind.OR_ASSIGNMENT,  # |=
    TokenKind.CARET_EQ: TreeKind.XOR_ASSIGNMENT,  # ^=
    TokenKind.PERCENT_EQ: TreeKind.REMAINDER_ASSIGNMENT,  # ^=
    TokenKind.LT_LT_EQ: TreeKind.LEFT_SHIFT_ASSIGNMENT,  # <<=
    TokenKind.GT_GT_EQ: TreeKind.RIGHT_SHIFT_ASSIGNMENT,  # >>=
    TokenKind.GT_GT_GT_EQ: TreeKind.UNSIGNED_RIGHT_SHIFT_ASSIGNMENT  # >>>=
}

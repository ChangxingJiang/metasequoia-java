"""
Token 到运算符优先级的映射
"""

from metasequoia_java.grammar.grammar_enum.operator_precedence import OperatorPrecedence
from metasequoia_java.lexical import TokenKind

__all__ = [
    "TOKEN_TO_OPERATOR_PRECEDENCE"
]

# Token 到运算符优先级的映射
TOKEN_TO_OPERATOR_PRECEDENCE = {
    TokenKind.BAR_BAR: OperatorPrecedence.OR_PREC,  # ||
    TokenKind.AMP_AMP: OperatorPrecedence.AND_PREC,  # &&
    TokenKind.BAR: OperatorPrecedence.BIT_OR_PREC,  # |
    TokenKind.CARET: OperatorPrecedence.BIT_XOR_PREC,  # ^
    TokenKind.AMP: OperatorPrecedence.BIT_AND_PREC,  # &
    TokenKind.EQ_EQ: OperatorPrecedence.EQ_PREC,  # ==
    TokenKind.BANG_EQ: OperatorPrecedence.EQ_PREC,  # !=
    TokenKind.LT: OperatorPrecedence.ORD_PREC,  # <
    TokenKind.GT: OperatorPrecedence.ORD_PREC,  # >
    TokenKind.LT_EQ: OperatorPrecedence.ORD_PREC,  # <=
    TokenKind.GT_EQ: OperatorPrecedence.ORD_PREC,  # >=
    TokenKind.LT_LT: OperatorPrecedence.SHIFT_PREC,  # <<
    TokenKind.GT_GT: OperatorPrecedence.SHIFT_PREC,  # >>
    TokenKind.GT_GT_GT: OperatorPrecedence.SHIFT_PREC,  # >>>
    TokenKind.PLUS: OperatorPrecedence.ADD_PREC,  # +
    TokenKind.SUB: OperatorPrecedence.ADD_PREC,  # -
    TokenKind.STAR: OperatorPrecedence.MUL_PREC,  # *
    TokenKind.SLASH: OperatorPrecedence.MUL_PREC,  # /
    TokenKind.PERCENT: OperatorPrecedence.MUL_PREC,  # %
}

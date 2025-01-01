"""
运算符优先级
"""

import enum

__all__ = [
    "OperatorPrecedence"
]


class OperatorPrecedence(enum.IntEnum):
    """运算符优先级"""

    NOT_EXPRESSION = -1  # 不是表达式
    NO_PREC = 0  # no enclosing expression
    ASSIGN_PREC = 1
    ASSIGN_OP_PREC = 2
    COND_PREC = 3
    OR_PREC = 4
    AND_PREC = 5
    BIT_OR_PREC = 6
    BIT_XOR_PREC = 7
    BIT_AND_PREC = 8
    EQ_PREC = 9
    ORD_PREC = 10
    SHIFT_PREC = 11
    ADD_PREC = 12
    MUL_PREC = 13
    PREFIX_PREC = 14
    POSTFIX_PREC = 15
    PREC_COUNT = 16

"""
括号表达式中的元素含义的枚举类
"""

import enum

__all__ = [
    "ParensResult"
]


class ParensResult(enum.Enum):
    """括号表达式中的元素含义的枚举类"""
    CAST = enum.auto()  # 强制类型转换
    EXPLICIT_LAMBDA = enum.auto()  # 显式 lambda 表达式
    IMPLICIT_LAMBDA = enum.auto()  # 隐式 lambda 表达式
    PARENS = enum.auto()  # 括号表达式

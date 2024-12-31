"""
解析语法元素的解析模式
"""

import enum

__all__ = [
    "ParserMode"
]


class ParserMode(enum.IntFlag):
    """解析语法元素的解析模式"""

    NULL = 0
    EXPR = enum.auto()  # 表达式
    TYPE = enum.auto()  # 类型
    NO_PARAMS = enum.auto()  # 没有参数的类型
    TYPE_ARG = enum.auto()  # 类型实参
    DIAMOND = enum.auto()
    NO_LAMBDA = enum.auto()  # 不允许 lambda 表达式

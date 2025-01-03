"""
模式类型的枚举类

从 Java 17 开始，Java 引入了模式匹配（pattern matching）的概念到 switch 语句和表达式中，这允许 case 标签后跟的不仅仅是简单的常量表达式，
还可以是更复杂的模式。这里的“模式”可以包含类型检查和变量绑定，使你可以更简洁地处理不同类型的对象。
"""

import enum

__all__ = [
    "PatternResult"
]


class PatternResult(enum.Enum):
    """模式类型的枚举类"""

    EXPRESSION = enum.auto()
    PATTERN = enum.auto()

"""
枚举类中的元素类型
"""

import enum

__all__ = [
    "EnumeratorEstimate"
]


class EnumeratorEstimate(enum.IntEnum):
    """枚举类中的元素类型"""

    UNKNOWN = 0  # 未知元素
    ENUMERATOR = 1  # 枚举值
    MEMBER = 2  # 其他成员

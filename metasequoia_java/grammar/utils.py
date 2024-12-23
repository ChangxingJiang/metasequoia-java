"""工具函数"""

from metasequoia_java.grammar.constants import IntegerStyle

__all__ = [
    "change_int_to_string"
]


def change_int_to_string(value: int, style: IntegerStyle):
    """根据进制样式，将整数转换为字符串"""
    if style == IntegerStyle.DEC:
        return f"{value}"

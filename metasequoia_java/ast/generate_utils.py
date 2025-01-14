"""
代码生成工具函数
"""

import enum
from typing import List, Optional

from metasequoia_java.ast.base import Tree
from metasequoia_java.ast.constants import IntegerStyle

__all__ = [
    "Separator",
    "generate_tree_list",
    "generate_enum_list",
    "change_int_to_string",
]


class Separator(enum.Enum):
    """代码生成的分隔符"""

    COMMA = ","
    SPACE = " "
    SEMI = " "
    AMP = "&"


def generate_tree_list(elems: Optional[List[Tree]], sep: Separator) -> str:
    """将抽象语法树节点的列表生成代码"""
    if elems is None:
        return ""
    return sep.value.join(elem.generate() for elem in elems)


def generate_enum_list(elems: Optional[List[enum.Enum]], sep: Separator) -> str:
    """将枚举值的列表生成代码"""
    if elems is None:
        return ""
    return sep.value.join(elem.value for elem in elems)


def change_int_to_string(value: int, style: IntegerStyle):
    """根据进制样式，将整数转换为字符串"""
    if style == IntegerStyle.DEC:
        return f"{value}"
    if style == IntegerStyle.OCT:
        return f"0{oct(value)[2:]}"
    if style == IntegerStyle.HEX:
        return f"0x{hex(value)[2:]}"

"""
代码生成工具函数
"""

import enum
from typing import List

from metasequoia_java.ast.base import Tree

__all__ = [
    "Separator",
    "generate_tree_list",
    "generate_enum_list",
]


class Separator(enum.Enum):
    """代码生成的分隔符"""

    COMMA = ","
    SPACE = " "
    SEMI = " "


def generate_tree_list(elems: List[Tree], sep: Separator):
    """将抽象语法树节点的列表生成代码"""
    return sep.value.join(elem.generate() for elem in elems)


def generate_enum_list(elems: List[enum.Enum], sep: Separator):
    """将枚举值的列表生成代码"""
    return sep.value.join(elem.value for elem in elems)

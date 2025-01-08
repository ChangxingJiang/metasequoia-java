"""
抽象语法树打印到控制台
"""

import dataclasses
from typing import Any, Optional

from metasequoia_java.ast.base import Tree

__all__ = [
    "dump"
]


def dump(root: Tree, last_name: Optional[str] = None, ident: int = 0) -> None:
    """将抽象语法树打印到控制台"""
    class_name = root.__class__.__name__
    kind_name = root.kind.name

    attr_name_list = []  # 属性字段
    child_name_list = []  # 子节点字段名
    for field in dataclasses.fields(root):
        # 忽略基类中包含的属性
        if field.name in {"kind", "start_pos", "end_pos", "source"}:
            continue

        value = getattr(root, field.name)

        # 如果属性值为空则忽略
        if value is None:
            continue

        if analyze_value_type(value):
            child_name_list.append(field.name)
        else:
            attr_name_list.append(field.name)

    attr_list = []
    for name in attr_name_list:
        value = getattr(root, name)
        attr_list.append(f"{name}={value}")
    if attr_list:
        attr_text = ": " + ", ".join(attr_list)
    else:
        attr_text = ""

    ident_text = " " * ident
    last_text = f"{last_name}: " if last_name is not None else ""
    print(f"{ident_text}{last_text}{class_name}({kind_name}){attr_text}")

    for name in child_name_list:
        value = getattr(root, name)
        if isinstance(value, list):
            print(f"{ident_text}  {name}:")
            for item in value:
                dump(item, None, ident + 4)
        else:
            dump(value, name, ident + 2)


def analyze_value_type(value: Any) -> bool:
    """分析节点属性类型，如果是子节点则返回 True，否则返回 False"""
    if isinstance(value, Tree):
        return True
    if isinstance(value, list):
        for item in value:
            if isinstance(item, Tree):
                return True
    return False

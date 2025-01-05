"""
抽象语法树信息分析函数
"""

from typing import Optional

from metasequoia_java.ast.base import Tree
from metasequoia_java.ast.node import AnnotatedTypeTree, ArrayTypeTree, WildcardTree

__all__ = [
    "inner_most_type"
]


def inner_most_type(type_node: Tree, skip_annotations: bool):
    """返回类型树的最内层类型"""
    last_annotated_type: Optional[Tree] = None
    current: Tree = type_node
    while True:
        if isinstance(current, ArrayTypeTree):
            current = current.expression
        elif isinstance(current, WildcardTree):
            current = current.bound
        elif isinstance(current, AnnotatedTypeTree):
            last_annotated_type = current
            current = current.underlying_type
        else:
            break
    if not skip_annotations and last_annotated_type is not None:
        return last_annotated_type
    return current

"""
抽象语法树的抽象节点
"""

import abc
import dataclasses
from typing import Optional

from metasequoia_java.ast.kind import TreeKind

__all__ = [
    "Tree"
]


@dataclasses.dataclass(slots=True)
class Tree(abc.ABC):
    """抽象语法树节点的抽象基类

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/Tree.java
    Common interface for all nodes in an abstract syntax tree.
    """

    kind: TreeKind = dataclasses.field(kw_only=True)  # 节点类型
    source: Optional[str] = dataclasses.field(kw_only=True)  # 原始代码

    @property
    def is_literal(self) -> bool:
        return False

    @abc.abstractmethod
    def generate(self) -> str:
        """生成当前节点元素的标准格式代码"""

"""
抽象语法树的抽象基类节点
"""

import abc
import dataclasses
from typing import Optional

from metasequoia_java.ast.kind import TreeKind

__all__ = [
    "Tree",  # 抽象语法树节点的抽象基类
    "ExpressionTree",  # 各类表达式节点的抽象基类
    "StatementTree",  # 各类语句节点的抽象基类
    "DirectiveTree",  # 模块中所有指令的超类型【JDK 9+】
    "PatternTree",  # 【JDK 16+】
    "CaseLabelTree",  # 【JDK 21+】
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


@dataclasses.dataclass(slots=True)
class ExpressionTree(Tree, abc.ABC):
    """各类表达式节点的抽象基类

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/ExpressionTree.java
    A tree node used as the base class for the different types of expressions.
    """


@dataclasses.dataclass(slots=True)
class StatementTree(Tree, abc.ABC):
    """各类语句节点的抽象基类

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/StatementTree.java
    A tree node used as the base class for the different kinds of statements.
    """


@dataclasses.dataclass(slots=True)
class DirectiveTree(Tree, abc.ABC):
    """模块中所有指令的超类型【JDK 9+】

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/DirectiveTree.java
    A super-type for all the directives in a ModuleTree.
    """


@dataclasses.dataclass(slots=True)
class PatternTree(Tree, abc.ABC):
    """【JDK 16+】TODO 名称待整理

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/PatternTree.java
    A tree node used as the base class for the different kinds of patterns.
    """


@dataclasses.dataclass(slots=True)
class CaseLabelTree(Tree, abc.ABC):
    """TODO 名称待整理

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/CaseLabelTree.java
    A marker interface for Trees that may be used as CaseTree labels.
    """

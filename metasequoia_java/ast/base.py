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
    start_pos: Optional[int] = dataclasses.field(kw_only=True)  # 在原始代码中的开始位置，当且仅当当前节点没有对应代码时为 None
    end_pos: Optional[int] = dataclasses.field(kw_only=True)  # 在原始代码中的结束位置，当且仅当当前节点没有对应代码时为 None
    source: Optional[str] = dataclasses.field(kw_only=True)  # 原始代码，当且仅当当前节点没有对应代码时为 None

    @staticmethod
    def mock() -> "Tree":
        return MockTree(
            kind=TreeKind.MOCK,
            start_pos=None,
            end_pos=None,
            source=None
        )

    @property
    def is_literal(self) -> bool:
        return False

    @abc.abstractmethod
    def generate(self) -> str:
        """生成当前节点元素的标准格式代码"""


@dataclasses.dataclass(slots=True)
class MockTree(Tree):
    """模拟节点"""

    def generate(self) -> str:
        return "MockNode"


@dataclasses.dataclass(slots=True)
class ExpressionTree(Tree, abc.ABC):
    """各类表达式节点的抽象基类

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/ExpressionTree.java
    A tree node used as the base class for the different types of expressions.
    """

    @staticmethod
    def mock() -> "ExpressionTree":
        return MockExpressionTree(
            kind=TreeKind.MOCK,
            start_pos=None,
            end_pos=None,
            source=None
        )


@dataclasses.dataclass(slots=True)
class MockExpressionTree(ExpressionTree):
    """模拟节点"""

    def generate(self) -> str:
        return "MockExpressionNode"


@dataclasses.dataclass(slots=True)
class StatementTree(Tree, abc.ABC):
    """各类语句节点的抽象基类

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/StatementTree.java
    A tree node used as the base class for the different kinds of statements.
    """

    @staticmethod
    def mock() -> "StatementTree":
        return MockStatement(start_pos=None, end_pos=None, source=None)


@dataclasses.dataclass(slots=True)
class MockStatement(StatementTree):
    """模拟 Statement 节点"""

    def generate(self) -> str:
        return "<MockStatement>"


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

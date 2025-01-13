"""
方法上下文
"""

from typing import List

from metasequoia_java import ast
from metasequoia_java.project.context.class_context import ClassContext
from metasequoia_java.project.context.file_context import FileContext
from metasequoia_java.project.context.project_context import ProjectContext
from metasequoia_java.project.name_space import NameSpace, SimpleNameSpace

__all__ = [
    "MethodContext"
]


class MethodContext:
    """方法上下文"""

    def __init__(self,
                 project_context: ProjectContext,
                 file_context: FileContext,
                 class_context: ClassContext,
                 method_name: str,
                 method_node: ast.Method):
        self.project_context = project_context
        self.file_context = file_context
        self.class_context = class_context
        self.method_name = method_name
        self.method_node = method_node

        self._simple_name_space = (SimpleNameSpace.create_by_method_params(method_node)
                                   + SimpleNameSpace.create_by_method_body(method_node))

    @staticmethod
    def create_by_method_name(class_context: ClassContext, method_name: str) -> "MethodContext":
        return MethodContext(
            project_context=class_context.project_context,
            file_context=class_context.file_context,
            class_context=class_context,
            method_name=method_name,
            method_node=class_context.get_method_node_by_name(method_name)
        )

    @property
    def block_statements(self) -> List[ast.Statement]:
        """获取代码块中的语句列表"""
        return self.method_node.block.statements

    # ------------------------------ 命名空间管理器 ------------------------------

    def get_simple_name_space(self) -> SimpleNameSpace:
        """返回方法参数变量和方法代码块中变量的单层命名空间"""
        return self._simple_name_space

    def get_name_space(self) -> NameSpace:
        """返回包含类变量、方法参数变量和方法代码块中变量的命名空间"""
        name_space = self.class_context.get_name_space()
        name_space.add_space(self._simple_name_space)
        return name_space

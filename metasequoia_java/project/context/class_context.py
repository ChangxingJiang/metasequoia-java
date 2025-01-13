"""
类上下文
"""

from metasequoia_java import ast
from metasequoia_java.project.context.file_context import FileContext
from metasequoia_java.project.context.project_context import ProjectContext
from metasequoia_java.project.name_space import NameSpace, SimpleNameSpace

__all__ = [
    "ClassContext"
]


class ClassContext:
    """类上下文"""

    def __init__(self,
                 project_context: ProjectContext,
                 file_context: FileContext,
                 class_name: str,
                 class_node: ast.Class):
        self.project_context = project_context
        self.file_context = file_context
        self.class_name = class_name
        self.class_node = class_node

        self._simple_name_space = SimpleNameSpace.create_by_class(class_node)

    @staticmethod
    def create_by_class_name(file_context: FileContext, class_name: str) -> "ClassContext":
        return ClassContext(
            project_context=file_context.project_context,
            file_context=file_context,
            class_name=class_name,
            class_node=file_context.get_class_declaration_by_class_name(class_name)
        )

    @staticmethod
    def create_by_public_class(file_context: FileContext) -> "ClassContext":
        return ClassContext(
            project_context=file_context.project_context,
            file_context=file_context,
            class_name=file_context.public_class_name,
            class_node=file_context.get_public_class_declaration()
        )

    # ------------------------------ 命名空间管理器 ------------------------------

    def get_simple_name_space(self) -> SimpleNameSpace:
        """返回类变量的单层命名空间"""
        return self._simple_name_space

    def get_name_space(self) -> NameSpace:
        """返回包含类变量的命名空间"""
        return NameSpace(self._simple_name_space)

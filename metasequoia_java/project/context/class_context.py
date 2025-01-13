"""
类上下文
"""

from metasequoia_java import ast
from metasequoia_java.project.context.base_context import ClassContextBase
from metasequoia_java.project.context.base_context import FileContextBase
from metasequoia_java.project.context.base_context import ProjectContextBase
from metasequoia_java.project.elements import RuntimeClass
from metasequoia_java.project.name_space import NameSpace, SimpleNameSpace

__all__ = [
    "ClassContext"
]


class ClassContext(ClassContextBase):
    """类上下文"""

    def __init__(self,
                 project_context: ProjectContextBase,
                 file_context: FileContextBase,
                 class_name: str,
                 class_node: ast.Class):
        self._project_context = project_context
        self._file_context = file_context
        self._class_name = class_name
        self._class_node = class_node

        self._simple_name_space = SimpleNameSpace.create_by_class(class_node)

    @staticmethod
    def create_by_class_name(file_context: FileContextBase, class_name: str) -> "ClassContext":
        return ClassContext(
            project_context=file_context.project_context,
            file_context=file_context,
            class_name=class_name,
            class_node=file_context.get_class_node_by_class_name(class_name)
        )

    @staticmethod
    def create_by_public_class(file_context: FileContextBase) -> "ClassContext":
        return ClassContext(
            project_context=file_context.project_context,
            file_context=file_context,
            class_name=file_context.public_class_name,
            class_node=file_context.get_public_class_declaration()
        )

    @property
    def project_context(self) -> ProjectContextBase:
        """返回所属项目上下文管理器"""
        return self._project_context

    @property
    def file_context(self) -> FileContextBase:
        """返回所属文件上下文管理器"""
        return self._file_context

    @property
    def class_name(self) -> str:
        """返回类名"""
        return self._class_name

    @property
    def class_node(self) -> ast.Class:
        """返回类的抽象语法树节点"""
        return self._class_node

    def get_method_node_by_name(self, method_name: str) -> ast.Method:
        """根据 method_name 获取方法的抽象语法树节点"""
        return self._class_node.get_method_by_name(method_name)

    def get_runtime_class(self) -> RuntimeClass:
        """构造当前类上下文对应的 RuntimeClass 对象"""
        return RuntimeClass(
            package_name=self.file_context.package_name,
            class_name=self.class_name,
            type_arguments=None
        )

    # ------------------------------ 命名空间管理器 ------------------------------

    def get_simple_name_space(self) -> SimpleNameSpace:
        """返回类变量的单层命名空间"""
        return self._simple_name_space

    def get_name_space(self) -> NameSpace:
        """返回包含类变量的命名空间"""
        return NameSpace(self._simple_name_space)

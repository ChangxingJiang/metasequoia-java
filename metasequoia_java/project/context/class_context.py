"""
类上下文
"""

import functools
from typing import List, Optional, Tuple

from metasequoia_java import ast
from metasequoia_java.common import LOGGER
from metasequoia_java.project.context.base_context import ClassContextBase
from metasequoia_java.project.context.base_context import FileContextBase
from metasequoia_java.project.context.base_context import ProjectContextBase
from metasequoia_java.project.elements import RuntimeClass
from metasequoia_java.project.utils import NameSpace
from metasequoia_java.project.utils import SimpleNameSpace

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

    def get_method_node_by_name(self, method_name: str) -> Optional[Tuple[ClassContextBase, ast.Method]]:
        """根据 method_name 获取方法所在类的 ClassContext 和抽象语法树节点"""
        # 优先在当前类中寻找方法
        method_node = self.class_node.get_method_by_name(method_name)
        if method_node is not None:
            return self, method_node

        # 尝试在父类中寻找方法（原则上只会有一个父类中包含）
        for runtime_class in self.get_extends_and_implements():
            class_context = self.project_context.create_class_context_by_runtime_class(runtime_class)
            if class_context is None:
                LOGGER.warning(f"在项目中找不到 runtime_class: {runtime_class}")
                continue

            method_info = class_context.get_method_node_by_name(method_name)
            if method_info is not None:
                return method_info
        return None

    def get_variable_node_by_name(self, variable_name: str) -> Optional[Tuple[ClassContextBase, ast.Variable]]:
        """根据 variable_name 获取类变量所在类的 ClassContext 和抽象语法树节点"""
        # 优先在当前类中寻找属性
        variable_node = self.class_node.get_variable_by_name(variable_name)
        if variable_node is not None:
            return self, variable_node

        # 尝试在父类中寻找属性
        for runtime_class in self.get_extends_and_implements():
            class_context = self.project_context.create_class_context_by_runtime_class(runtime_class)
            if class_context is None:
                LOGGER.warning(f"在项目中找不到 runtime_class: {runtime_class}")
                continue

            variable_info = class_context.get_variable_node_by_name(variable_name)
            if variable_info is not None:
                return variable_info

        return None

    @functools.lru_cache(maxsize=10)
    def get_extends_and_implements(self) -> List[RuntimeClass]:
        """获取继承和实现接口的类的 RuntimeClass 对象的列表"""
        result = []
        for type_node in self.class_node.get_extends_and_implements():
            # 获取继承的类名
            class_name = None
            if isinstance(type_node, ast.Identifier):
                class_name = type_node.name
            elif isinstance(type_node, ast.ParameterizedType):
                type_name = type_node.type_name
                if isinstance(type_name, ast.Identifier):
                    class_name = type_name.name

            if class_name is None:
                LOGGER.warning(f"无法处理的类名类型: {type_node}")
                continue

            runtime_class = self.file_context.get_runtime_class_by_class_name(class_name)
            if runtime_class is None:
                LOGGER.warning(f"找不到继承类: class_name={class_name}")
            package_name = runtime_class.package_name
            if package_name is None:
                LOGGER.warning(f"找不到继承类所属的包: class_name={class_name}")

            result.append(RuntimeClass.create(
                package_name=package_name,
                public_class_name=class_name,
                class_name=class_name,
                type_arguments=[]
            ))
        return result

    def get_runtime_class(self) -> RuntimeClass:
        """构造当前类上下文对应的 RuntimeClass 对象"""
        return RuntimeClass.create(
            package_name=self.file_context.package_name,
            public_class_name=self.file_context.public_class_name,
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

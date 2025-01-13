"""
上下文管理器的抽象基类
"""

import abc
from typing import Dict, Generator, List, Optional

from metasequoia_java import ast
from metasequoia_java.project.elements import RuntimeClass
from metasequoia_java.project.elements import RuntimeMethod
from metasequoia_java.project.elements import RuntimeVariable
from metasequoia_java.project.name_space import NameSpace
from metasequoia_java.project.name_space import SimpleNameSpace

__all__ = [
    "ProjectContextBase",
    "FileContextBase",
    "ClassContextBase",
    "MethodContextBase",
]


class ProjectContextBase(abc.ABC):
    """项目层级消上下文管理器的抽象基类"""

    @property
    @abc.abstractmethod
    def project_path(self) -> str:
        """返回项目根路径"""

    # ------------------------------ package 层级处理方法 ------------------------------

    @abc.abstractmethod
    def get_package_path_by_package_name(self, package_name: str) -> Optional[str]:
        """根据 package_name（包名称）获取 package_path（包路径）"""

    @abc.abstractmethod
    def get_file_path_list_by_package_name(self, package_name: str) -> List[str]:
        """根据 package_name（包名称）获取其中所有 file_path（文件路径）"""

    @abc.abstractmethod
    def get_class_name_list_by_package_name(self, package_name: str) -> List[str]:
        """根据 package_name（包名称）获取其中所有模块内可见类的 class_name（类名）的列表"""

    # ------------------------------ file 层级处理方法 ------------------------------

    @abc.abstractmethod
    def get_file_node_by_file_path(self, file_path: str) -> ast.CompilationUnit:
        """根据 file_path（文件路径）获取 file_node（抽象语法树的文件节点）"""

    @abc.abstractmethod
    def get_file_node_by_absolute_name(self, absolute_name: str) -> ast.CompilationUnit:
        """根据 absolute_name（绝对引用名称）获取 file_node（抽象语法树的文件节点）"""

    @abc.abstractmethod
    def get_file_node_by_package_name_class_name(self,
                                                 package_name: str,
                                                 class_name: str
                                                 ) -> Optional[ast.CompilationUnit]:
        """根据 absolute_name（绝对引用名称）获取 file_node（抽象语法树的文件节点）"""

    # ------------------------------ 项目全局搜索方法 ------------------------------

    @abc.abstractmethod
    def create_file_context_by_class_absolute_name(self, class_absolute_name: str) -> "FileContextBase":
        """根据公有类的绝对引用名称，构造 FileContext 对象"""

    @abc.abstractmethod
    def create_class_context_by_class_absolute_name(self, class_absolute_name: str) -> "ClassContextBase":
        """根据公有类的绝对引用名称，构造 ClassContext 对象"""

    @abc.abstractmethod
    def create_class_context_by_runtime_class(self, runtime_class: RuntimeClass) -> "ClassContextBase":
        """根据 runtimeClass 对象，构造 ClassContext 对象"""

    @abc.abstractmethod
    def create_method_context_by_runtime_method(self, runtime_method: RuntimeMethod) -> "MethodContextBase":
        """根据 runtimeMethod 对象构造 MethodContext 对象"""

    @abc.abstractmethod
    def get_type_node_by_runtime_variable(self, runtime_variable: RuntimeVariable) -> Optional[ast.Tree]:
        """根据 runtimeVariable 返回值的类型，构造 runtimeClass"""

    @abc.abstractmethod
    def get_runtime_class_by_runtime_method_return_type(self, runtime_method: RuntimeMethod) -> Optional[RuntimeClass]:
        """根据 runtimeMethod 返回值的类型，构造 runtimeClass"""

    # ------------------------------ 项目外已知信息管理方法 ------------------------------

    @abc.abstractmethod
    def try_get_outer_attribute_type(self, runtime_variable: RuntimeVariable) -> Optional[RuntimeClass]:
        """获取项目外已知类属性类型"""

    @abc.abstractmethod
    def try_get_outer_method_return_type(self, runtime_method: RuntimeMethod) -> Optional[RuntimeClass]:
        """获取项目外已知方法返回值类型"""


class FileContextBase(abc.ABC):
    """文件层级上下文管理器的抽象基类"""

    @property
    @abc.abstractmethod
    def project_context(self) -> ProjectContextBase:
        """返回所属项目上下文管理器"""

    @property
    @abc.abstractmethod
    def package_name(self) -> str:
        """返回所属 package 名称"""

    @property
    @abc.abstractmethod
    def public_class_name(self) -> str:
        """返回文件中的公有类名称"""

    @property
    @abc.abstractmethod
    def file_node(self) -> ast.CompilationUnit:
        """返回文件的抽象语法树节点"""

    # ------------------------------ class 层级处理方法 ------------------------------

    @abc.abstractmethod
    def get_public_class_declaration(self) -> ast.Class:
        """返回公有类的抽象语法树节点"""

    @abc.abstractmethod
    def get_class_node_by_class_name(self, class_name) -> Optional[ast.Class]:
        """根据 class_name 获取指定类的抽象语法树节点"""

    # ------------------------------ 项目映射管理器 ------------------------------

    @abc.abstractmethod
    def create_import_hash(self) -> Dict[str, RuntimeClass]:
        """构造文件中包含的引用逻辑"""

    @abc.abstractmethod
    def get_import_absolute_name_by_class_name(self, class_name: str) -> Optional[str]:
        """根据 class_name，获取引用映射中的完整名称"""

    @abc.abstractmethod
    def get_import_package_name_by_class_name(self, class_name: str) -> Optional[str]:
        """获取 class_name，获取引用映射中的包名称"""

    @abc.abstractmethod
    def get_runtime_class_by_type_node(self,
                                       class_node: ast.Class,
                                       runtime_class: RuntimeClass,
                                       type_node: ast.Tree) -> Optional[RuntimeClass]:
        """
        根据抽象语法树节点 class_node 中（运行中为 runtime_class），表示类型的抽象语法树节点 type_node，构造该类型对应的 runtime_class
        对象
        """


class ClassContextBase(abc.ABC):
    """类层级上下文管理器的抽象基类"""

    @property
    @abc.abstractmethod
    def project_context(self) -> ProjectContextBase:
        """返回所属项目上下文管理器"""

    @property
    @abc.abstractmethod
    def file_context(self) -> FileContextBase:
        """返回所属文件上下文管理器"""

    @property
    @abc.abstractmethod
    def class_name(self) -> str:
        """返回类名"""

    @property
    @abc.abstractmethod
    def class_node(self) -> ast.Class:
        """返回类的抽象语法树节点"""

    # ------------------------------ method 和 variable 层级处理方法 ------------------------------

    @abc.abstractmethod
    def get_method_node_by_name(self, method_name: str) -> ast.Method:
        """根据 method_name 获取方法的抽象语法树节点"""

    @abc.abstractmethod
    def get_runtime_class(self) -> RuntimeClass:
        """构造当前类上下文对应的 RuntimeClass 对象"""

    # ------------------------------ 命名空间管理器 ------------------------------

    @abc.abstractmethod
    def get_simple_name_space(self) -> SimpleNameSpace:
        """返回类变量的单层命名空间"""

    @abc.abstractmethod
    def get_name_space(self) -> NameSpace:
        """返回包含类变量的命名空间"""


class MethodContextBase(abc.ABC):
    """方法层级上下文管理器的抽象基类"""

    @property
    @abc.abstractmethod
    def project_context(self) -> ProjectContextBase:
        """返回所属的项目上下文管理器"""

    @property
    @abc.abstractmethod
    def file_context(self) -> FileContextBase:
        """返回所属的文件上下文管理器"""

    @property
    @abc.abstractmethod
    def class_context(self) -> ClassContextBase:
        """返回所属的类上下文管理器"""

    @property
    @abc.abstractmethod
    def method_name(self) -> str:
        """返回方法名称"""

    @property
    @abc.abstractmethod
    def method_node(self) -> ast.Method:
        """返回方法的抽象语法树节点"""

    @property
    @abc.abstractmethod
    def block_statements(self) -> List[ast.Statement]:
        """获取代码块中的语句列表"""

    @abc.abstractmethod
    def get_runtime_method(self) -> RuntimeMethod:
        """返回当前方法上下文对应的 RuntimeMethod 对象"""

    # ------------------------------ 命名空间管理器 ------------------------------

    @abc.abstractmethod
    def get_simple_name_space(self) -> SimpleNameSpace:
        """返回方法参数变量和方法代码块中变量的单层命名空间"""

    @abc.abstractmethod
    def get_name_space(self) -> NameSpace:
        """返回包含类变量、方法参数变量和方法代码块中变量的命名空间"""

    # ------------------------------ 方法调用遍历器 ------------------------------

    @abc.abstractmethod
    def get_method_invocation(self,
                              namespace: NameSpace,
                              statement_node: ast.Tree
                              ) -> Generator[RuntimeMethod, None, None]:
        """获取当前表达式中调用的方法"""

    @abc.abstractmethod
    def get_runtime_class_by_node(self,
                                  namespace: NameSpace,
                                  expression_node: ast.Tree
                                  ) -> Optional[RuntimeClass]:
        """获取当前类中节点元素的类型"""

"""
上下文管理器的抽象基类
"""

import abc
from typing import Dict, Generator, List, Optional, Tuple, Type

from metasequoia_java import ast
from metasequoia_java.project.elements import RuntimeClass
from metasequoia_java.project.elements import RuntimeMethod
from metasequoia_java.project.elements import RuntimeVariable
from metasequoia_java.project.utils import NameSpace
from metasequoia_java.project.utils import SimpleNameSpace

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

    @abc.abstractmethod
    def get_static_variable_name_list_by_runtime_class(self, runtime_class: RuntimeClass) -> Optional[List[str]]:
        """根据 runtimeClass 对象获取该对象中静态变量名称的列表"""

    @abc.abstractmethod
    def get_static_method_name_list_by_runtime_class(self, runtime_class: RuntimeClass) -> Optional[List[str]]:
        """根据 runtimeClass 对象获取该对象中静态方法名称的列表"""

    # ------------------------------ file 层级处理方法 ------------------------------

    @abc.abstractmethod
    def get_file_node_by_file_path(self, file_path: str) -> ast.CompilationUnit:
        """根据 file_path（文件路径）获取 file_node（抽象语法树的文件节点）"""

    @abc.abstractmethod
    def get_file_node_by_absolute_name(self, absolute_name: str) -> ast.CompilationUnit:
        """根据 absolute_name（绝对引用名称）获取 file_node（抽象语法树的文件节点）"""

    @abc.abstractmethod
    def get_file_node_by_runtime_class(self, runtime_class: RuntimeClass) -> ast.CompilationUnit:
        """根据 RuntimeClass 对象构造类所在文件的抽象语法树节点"""

    @abc.abstractmethod
    def get_file_node_by_package_name_class_name(self,
                                                 package_name: str,
                                                 class_name: str
                                                 ) -> Optional[ast.CompilationUnit]:
        """根据 absolute_name（绝对引用名称）获取 file_node（抽象语法树的文件节点）"""

    # ------------------------------ 项目全局搜索方法 ------------------------------

    @abc.abstractmethod
    def create_file_context_by_runtime_class(self, runtime_class: Optional[RuntimeClass]) -> Optional[
        "FileContextBase"]:
        """根据 RuntimeClass 对象，构造类所在的文件的 FileContext 对象，如果不在当前项目中则返回 None"""

    @abc.abstractmethod
    def create_class_context_by_runtime_class(self, runtime_class: Optional[RuntimeClass]) -> "ClassContextBase":
        """根据 runtimeClass 对象，构造类的 ClassContext 对象，如果不在当前项目中则返回 None"""

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

    @abc.abstractmethod
    def try_get_outer_package_class_name_list(self, package_name: str) -> Optional[List[str]]:
        """获取项目外 package_name 对应的 class_name 的列表"""


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

    @property
    @abc.abstractmethod
    def import_class_hash(self) -> Dict[str, RuntimeClass]:
        """返回类引用映射"""

    @property
    @abc.abstractmethod
    def import_variable_hash(self) -> Dict[str, RuntimeVariable]:
        """返回静态属性引用映射"""

    @property
    @abc.abstractmethod
    def import_method_hash(self) -> Dict[str, RuntimeMethod]:
        """返回静态方法引用映射"""

    # ------------------------------ class 层级处理方法 ------------------------------

    @abc.abstractmethod
    def get_public_class_declaration(self) -> ast.Class:
        """返回公有类的抽象语法树节点"""

    @abc.abstractmethod
    def get_class_node_by_class_name(self, class_name) -> Optional[ast.Class]:
        """根据 class_name 获取指定类的抽象语法树节点"""

    # ------------------------------ 元素类型推断 ------------------------------

    @abc.abstractmethod
    def get_runtime_class_by_class_name(self, class_name: str) -> Optional[RuntimeClass]:
        """根据当前文件中出现的 class_name，获取对应的 RuntimeClass 对象"""

    @abc.abstractmethod
    def infer_runtime_class_by_node(self, type_node: ast.Tree) -> Optional[RuntimeClass]:
        """推断当前文件中出现的抽象语法树节点的类型"""


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
    def get_method_node_by_name(self, method_name: str) -> Optional[Tuple["ClassContextBase", ast.Method]]:
        """根据 method_name 获取方法的抽象语法树节点"""

    @abc.abstractmethod
    def get_variable_node_by_name(self, variable_name: str) -> Optional[Tuple["ClassContextBase", ast.Variable]]:
        """根据 variable_name 获取类变量的抽象语法树节点"""

    @abc.abstractmethod
    def get_extends_and_implements(self) -> List[RuntimeClass]:
        """获取继承和实现接口的类的 RuntimeClass 对象的列表"""

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

    # ------------------------------ 元素类型推断 ------------------------------

    @abc.abstractmethod
    def infer_runtime_class_by_node(self,
                                    runtime_class: RuntimeClass,
                                    type_node: ast.Tree) -> Optional[RuntimeClass]:
        """推断出现在当前类中的抽象语法树类型"""


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
    def search_node(self,
                    statement_node: ast.Tree,
                    search_type: Type,
                    ) -> Generator[ast.Tree, None, None]:
        """获取当前表达式中调用的方法中，寻找 search_type 类型的节点"""

    # ------------------------------ 元素类型推断 ------------------------------

    @abc.abstractmethod
    def infer_runtime_class_by_node(self,
                                    namespace: NameSpace,
                                    type_node: ast.Tree
                                    ) -> Optional[RuntimeClass]:
        """推断出现在当前方法中的抽象语法树类型"""

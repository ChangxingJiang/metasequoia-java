"""
项目级上下文
"""

import functools
import os
from typing import Callable, Dict, List, Optional, Tuple

from metasequoia_java import ast, parse_compilation_unit
from metasequoia_java.common import LOGGER
from metasequoia_java.sa.context.base_context import ClassContextBase
from metasequoia_java.sa.context.base_context import FileContextBase
from metasequoia_java.sa.context.base_context import MethodContextBase
from metasequoia_java.sa.context.base_context import ProjectContextBase
from metasequoia_java.sa.context.class_context import ClassContext
from metasequoia_java.sa.context.file_context import FileContext
from metasequoia_java.sa.context.method_context import MethodContext
from metasequoia_java.sa.elements import RuntimeClass
from metasequoia_java.sa.elements import RuntimeMethod
from metasequoia_java.sa.elements import RuntimeVariable
from metasequoia_java.sa.name_space import NameSpace


class ProjectContext(ProjectContextBase):
    """项目级上下文

    在初始化阶段，获取所有 module 以及 module 中的顶级目录。

    名称说明：
    absolute_name = 绝对引用名称 = {package_name}.{class_name}
    package_name = 包名称
    class_name = 类名称
    package_path = 包文件夹路径 = xxx/{package_name}
    file_name = 文件名称 = {class_name}.java
    file_path = 文件路径 = xxx/{package_name}/{class_name}.java
    file_node = 文件的抽象语法树节点

    如果方法中直接访问文件系统，则文件名前缀为 _load，否则方法名前缀为 _get
    """

    def __init__(
            self,
            project_path: str,
            modules: Dict[str, List[str]],
            outer_attribute_type: Optional[Dict[str, Callable[[RuntimeVariable], RuntimeClass]]] = None,
            outer_method_param_type: Optional[Dict[Tuple[str, int], Callable[[RuntimeMethod], RuntimeClass]]] = None,
            outer_method_return_type: Optional[Dict[str, Callable[[RuntimeMethod], RuntimeClass]]] = None,
            outer_package_class_list: Optional[Dict[str, List[str]]] = None,
            outer_lambda_param_type: Optional[Dict[str, Callable[[RuntimeClass], List[RuntimeClass]]]] = None,
            outer_java_file: Optional[Dict[str, str]] = None):
        """

        Parameters
        ----------
        project_path : str
            项目根路径地址
        modules : Dict[str, List[str]]
            项目中 module 路径地址
        outer_attribute_type : Optional[Dict[Tuple[str, str], RuntimeClass]], default = None
            项目外已知属性类型
        outer_method_param_type : Optional[Dict[Tuple[str, int], Callable[[RuntimeMethod], RuntimeClass]]],
                                  default = None
            项目外已知方法参数类型
        outer_method_return_type : Optional[Dict[Tuple[str, str], RuntimeClass]], default = None
            项目外已知方法返回值类型
        outer_package_class_list : Optional[Dict[str, List[str]]], default = None
            项目外已知 package 对应的 class_name 列表
        outer_lambda_param_type : Optional[Dict[str, Callable[[RuntimeClass], List[RuntimeClass]]]], default = None
            项目外已知的函数式接口（lambda 表达式）参数类型列表，即传入的函数式接口 RuntimeClass 类中唯一的抽象方法的参数
        outer_java_file : outer_file: Optional[Dict[str, str]], default = None
            项目外已知 package_name.class_name 对应的 Java 文件源码
        """
        if outer_attribute_type is None:
            outer_attribute_type = {}
        if outer_method_param_type is None:
            outer_method_param_type = {}
        if outer_method_return_type is None:
            outer_method_return_type = {}
        if outer_package_class_list is None:
            outer_package_class_list = {}
        if outer_lambda_param_type is None:
            outer_lambda_param_type = {}
        if outer_java_file is None:
            outer_java_file = {}

        self._project_path = project_path
        self._modules: Dict[str, str] = {
            module_name: [os.path.join(project_path, path) for path in module_source_list]
            for module_name, module_source_list in modules.items()
        }
        self._outer_attribute_type = outer_attribute_type
        self._outer_method_param_type = outer_method_param_type
        self._outer_method_return_type = outer_method_return_type
        self._outer_package_class_list = outer_package_class_list
        self._outer_lambda_param_type = outer_lambda_param_type
        self._outer_java_file = {}
        for class_absolute_name, java_file in outer_java_file.items():
            self._outer_java_file[f"outer:{class_absolute_name}.java"] = java_file

    @property
    def project_path(self) -> str:
        """返回项目根路径"""
        return self._project_path

    @functools.lru_cache(maxsize=1024)
    def get_file_node_by_file_path(self, file_path: str) -> Optional[ast.CompilationUnit]:
        """根据 file_path（文件路径）获取 file_node（抽象语法树的文件节点）"""
        if not file_path.startswith("outer:"):
            # 从文件系统中读取 Java 文件
            if not os.path.exists(file_path):
                return None
            with open(file_path, "r", encoding="UTF-8") as file:
                return parse_compilation_unit(file.read())
        return parse_compilation_unit(self._outer_java_file[file_path])

    @functools.lru_cache(maxsize=1024)
    def get_file_node_by_package_name_class_name(self,
                                                 package_name: str,
                                                 public_class_name: str,
                                                 need_warning: bool = True
                                                 ) -> Optional[ast.CompilationUnit]:
        """根据 package_name 和公有类的 class_name 获取对应文件的抽象语法树节点

        1. 如果 package_name 和公有类的 class_name 对应大于 1 个文件，则返回 None 并发送警告
        2. 如果 package_name 和公有类的 class_name 没有对应文件，则尝试通过项目外部 Java 源码文件路径获取，如果获取失败则返回 None 并发送警告
        """
        # 根据 package_name 获取所有可能的 package_path 的列表
        package_path_list = self.get_package_path_list_by_package_name(package_name)

        # 根据 package_path 的列表获取 class_name 对应的所有文件路径的列表
        file_path_list = []
        for package_path in package_path_list:
            # 通过文件系统读取 Java 代码文件
            file_path = os.path.join(package_path, f"{public_class_name}.java")
            if os.path.exists(file_path):
                file_path_list.append(file_path)

        if len(file_path_list) == 1:
            return self.get_file_node_by_file_path(file_path_list[0])

        if len(file_path_list) > 1:
            if need_warning:
                LOGGER.warning(f"公有类对应多个 Java 文件: package_name={package_name}, class_name={public_class_name}")
            return None

        file_path = f"outer:{package_name}.{public_class_name}.java"  # 项目外部 Java 源码文件路径
        if file_path not in self._outer_java_file:
            if need_warning:
                LOGGER.warning(f"公有类找不到 Java 文件: package_name={package_name}, class_name={public_class_name}")
            return None
        return self.get_file_node_by_file_path(file_path)

    @functools.lru_cache(maxsize=1024)
    def get_package_path_list_by_package_name(self, package_name: Optional[str]) -> List[str]:
        """根据 package_name 获取所有可能的 package_path 的列表

        因为代码中可能存在多个 source code root，所以同一个 package_name 对应多个 package_path 应该属于一种合理的场景。
        """
        if package_name is None:
            return []

        # 计算所有备选 module 根路径
        candidate_path_list = []
        for module_name, module_path in self._modules.items():
            candidate_path_list.extend(module_path)

        # 在每个备选路径中查找 package
        for name in package_name.split("."):
            new_candidate_path_list = []
            for candidate_path in candidate_path_list:
                new_candidate_path = os.path.join(candidate_path, name)
                if os.path.exists(new_candidate_path):
                    new_candidate_path_list.append(new_candidate_path)
            candidate_path_list = new_candidate_path_list

        return candidate_path_list

    @functools.lru_cache(maxsize=1024)
    def get_file_path_list_by_package_name(self, package_name: str) -> List[str]:
        """根据 package_name 获取其中所有文件的文件路径的列表"""
        package_path_list = self.get_package_path_list_by_package_name(package_name)
        file_path_list = []
        for package_path in package_path_list:
            for file_name in os.listdir(package_path):
                file_path = os.path.join(package_path, file_name)
                if not os.path.isdir(file_path):  # 不需要处理 package 中的子路径
                    file_path_list.append(file_path)
        return file_path_list

    @functools.lru_cache(maxsize=1024)
    def get_class_name_list_by_package_name(self, package_name: str) -> Optional[List[str]]:
        """根据 package_name（包名称）获取其中所有模块内可见类的 class_name（类名）的列表"""
        file_path_list = self.get_file_path_list_by_package_name(package_name)

        # package_name 不在当前项目中，尝试从项目外知识库中获取
        if not file_path_list:
            res = self.try_get_outer_package_class_name_list(package_name)
            if res is None:
                LOGGER.warning(f"在项目外补充信息中，找不到 package_name 对应的 class_name 的列表: {package_name}")
            return res

        # package_name 在当前项目中
        class_name_list: List[str] = []
        for file_path in file_path_list:
            if not file_path.endswith(".java"):
                continue  # 跳过非 Java 代码文件
            file_node: ast.CompilationUnit = self.get_file_node_by_file_path(file_path)
            if file_node is None:
                LOGGER.warning(f"获取文件失败: {file_path}")
                return []
            for class_declaration in file_node.get_class_node_list():
                if ast.Modifier.PRIVATE not in class_declaration.modifiers.flags:
                    class_name_list.append(class_declaration.name)
        return class_name_list

    def get_static_variable_name_list_by_runtime_class(self, runtime_class: RuntimeClass) -> Optional[List[str]]:
        """根据 runtimeClass 对象获取该对象中静态变量名称的列表"""
        class_context = self.create_class_context_by_runtime_class(runtime_class)
        if class_context is None:
            return None
        variable_name_list = []
        for variable_node in class_context.class_node.get_variable_list():
            if ast.Modifier.STATIC in variable_node.modifiers.flags:
                variable_name_list.append(variable_node.name)
        return variable_name_list

    def get_static_method_name_list_by_runtime_class(self, runtime_class: RuntimeClass) -> Optional[List[str]]:
        """根据 runtimeClass 对象获取该对象中静态方法名称的列表"""
        class_context = self.create_class_context_by_runtime_class(runtime_class)
        if class_context is None:
            return None
        method_name_list = []
        for method_node in class_context.class_node.get_method_list():
            if ast.Modifier.STATIC in method_node.modifiers.flags:
                method_name_list.append(method_node.name)
        return method_name_list

    # ------------------------------ 项目全局搜索方法 ------------------------------

    @functools.lru_cache(maxsize=65536)
    def create_file_context_by_runtime_class(self,
                                             runtime_class: Optional[RuntimeClass],
                                             need_warning: bool = True
                                             ) -> Optional[FileContextBase]:
        """尝试根据 RuntimeClass 对象构造公有类所在文件的 FileContext 对象，如果在当前项目中查找不到 RuntimeClass 则返回 None"""
        if runtime_class is None:
            return None
        file_node: Optional[ast.CompilationUnit] = self.get_file_node_by_package_name_class_name(
            package_name=runtime_class.package_name,
            public_class_name=runtime_class.public_class_name,
            need_warning=need_warning
        )
        if file_node is None:
            return None
        return FileContext.create_by_runtime_class(
            project_context=self,
            runtime_class=runtime_class,
            file_node=file_node
        )

    @functools.lru_cache(maxsize=65536)
    def create_class_context_by_runtime_class(self,
                                              runtime_class: Optional[RuntimeClass],
                                              need_warning: bool = True
                                              ) -> Optional[ClassContextBase]:
        """尝试根据 RuntimeClass 构造 ClassContext 对象，如果在当前项目中查找不到 RuntimeClass 则返回 None"""
        file_context = self.create_file_context_by_runtime_class(runtime_class, need_warning=need_warning)
        if file_context is None:
            return None
        return ClassContext.create_by_class_name(file_context, runtime_class.class_name)

    @functools.lru_cache(maxsize=65536)
    def create_method_context_by_runtime_method(self,
                                                runtime_method: Optional[RuntimeMethod],
                                                need_warning: bool = True) -> Optional[MethodContextBase]:
        """根据 runtimeMethod 对象构造 MethodContext 对象，如果不在当前项目中则返回 None"""
        if runtime_method is None or runtime_method.belong_class is None:
            return None
        class_context = self.create_class_context_by_runtime_class(
            runtime_class=runtime_method.belong_class,
            need_warning=need_warning
        )
        if class_context is None:
            return None
        return MethodContext.create_by_method_name(class_context, runtime_method.method_name)

    def get_type_runtime_class_by_runtime_variable(self, runtime_variable: RuntimeVariable) -> Optional[RuntimeClass]:
        """根据 RuntimeVariable 对象，获取该变量类型的 RuntimeClass 对象"""
        variable_info = self.get_variable_info_by_runtime_variable(runtime_variable, need_warning=False)
        if variable_info is None:
            res = self.try_get_outer_attribute_type(runtime_variable)
            if res is None:
                LOGGER.warning(f"在项目外补充信息中，找不到属性类型: "
                               f"variable={runtime_variable.absolute_name}")
            return res

        variable_class_context, variable_node = variable_info
        return variable_class_context.infer_runtime_class_by_node(
            runtime_class=variable_class_context.get_runtime_class(),
            type_node=variable_node.variable_type
        )

    def get_variable_info_by_runtime_variable(self,
                                              runtime_variable: RuntimeVariable,
                                              need_warning: bool = True
                                              ) -> Optional[Tuple[ClassContextBase, ast.Variable]]:
        """根据 RuntimeVariable 对象获取该变量所在类的 ClassContext 对象，以及初始化该对象的抽象语法树节点"""
        class_context = self.create_class_context_by_runtime_class(runtime_variable.belong_class, need_warning=False)
        if class_context is None:
            LOGGER.warning(f"获取类变量的抽象语法树节点失败(类不存在): {runtime_variable}")
            return None
        variable_info = class_context.get_variable_node_by_name(runtime_variable.variable_name)
        if variable_info is None:
            LOGGER.warning(f"获取类变量的抽象语法树节点失败(变量不存在): {runtime_variable}")
        return variable_info

    def get_runtime_class_by_runtime_method_param(self,
                                                  runtime_method: RuntimeMethod,
                                                  param_idx: int
                                                  ) -> Optional[RuntimeClass]:
        """根据 RuntimeMethod 对象，返回其中第 param_idx 个参数的类型"""
        method_context = self.create_method_context_by_runtime_method(runtime_method, need_warning=False)
        if method_context is None:
            res = self.try_get_outer_method_param_type(runtime_method, param_idx)
            if res is None:
                LOGGER.warning(f"在项目外补充信息中，找不到方法参数类型: {runtime_method}, {param_idx}")
            return res

        parameters = method_context.method_node.parameters

        if len(parameters) <= param_idx:
            LOGGER.warning(f"方法 {method_context} 没有第 {param_idx} 个参数")
            return None

        return method_context.infer_runtime_class_by_node(runtime_method, NameSpace(), parameters[param_idx])

    def get_runtime_class_by_runtime_method_return_type(self, runtime_method: RuntimeMethod) -> Optional[RuntimeClass]:
        """根据 runtimeMethod 返回值的类型，构造 runtimeClass"""
        # 处理继承自 java.langObject 的 toString 方法和 equals 方法
        if runtime_method.method_name == "toString":
            return RuntimeClass.create_by_public_class_absolute_name("java.lang.String")
        if runtime_method.method_name == "equals":
            return RuntimeClass.create_by_public_class_absolute_name("java.lang.Boolean")

        # 尝试根据 RuntimeClass 构造 ClassContext 对象，如果在当前项目中查找不到 RuntimeClass 则返回 None
        class_context = self.create_class_context_by_runtime_class(
            runtime_class=runtime_method.belong_class,
            need_warning=False
        )

        # runtime_method.belong_class 不在项目中，尝试通过项目外已知方法返回值类型获取
        if class_context is None:
            res = self.try_get_outer_method_return_type(runtime_method)
            if res is None:
                LOGGER.warning(f"在项目外补充信息中，找不到方法返回值类型: {runtime_method}")
            return res

        # runtime_method.belong_class 在项目中，获取返回值类型
        method_node = class_context.class_node.get_method_by_name(runtime_method.method_name)
        if method_node is None:
            return None
        return class_context.infer_runtime_class_by_node(
            runtime_class=runtime_method.belong_class,
            type_node=method_node.return_type
        )

    def get_runtime_class_list_by_functional_interface(self, runtime_class: RuntimeClass
                                                       ) -> Optional[List[RuntimeClass]]:
        """根据函数式接口 RuntimeClass 的 lambda 表达式的参数类型列表"""
        res = self.try_get_runtime_class_list_by_functional_interface(runtime_class)
        if res is None:
            LOGGER.warning(f"在项目外补充信息中，找不到函数式接口 {runtime_class} 的参数类型列表")
        return res

    # ------------------------------ 获取项目外已知类型 ------------------------------

    def try_get_outer_attribute_type(self, runtime_variable: RuntimeVariable) -> Optional[RuntimeClass]:
        """获取项目外已知类属性类型"""
        if runtime_variable is None or runtime_variable.absolute_name not in self._outer_attribute_type:
            return None
        return self._outer_attribute_type[runtime_variable.absolute_name](runtime_variable)

    def try_get_outer_method_param_type(self, runtime_method: RuntimeMethod, param_idx: int) -> Optional[RuntimeClass]:
        """获取项目外已知方法参数类型"""
        if runtime_method is None or (runtime_method.absolute_name, param_idx) not in self._outer_method_param_type:
            return None
        return self._outer_method_param_type[(runtime_method.absolute_name, param_idx)](runtime_method)

    def try_get_outer_method_return_type(self, runtime_method: RuntimeMethod) -> Optional[RuntimeClass]:
        """获取项目外已知方法返回值类型"""
        if runtime_method is None or runtime_method.absolute_name not in self._outer_method_return_type:
            return None
        return self._outer_method_return_type[runtime_method.absolute_name](runtime_method)

    def try_get_outer_package_class_name_list(self, package_name: str) -> Optional[List[str]]:
        """获取项目外 package_name 对应的 class_name 的列表"""
        if package_name not in self._outer_package_class_list:
            return None
        return self._outer_package_class_list[package_name]

    def try_get_runtime_class_list_by_functional_interface(self, runtime_class: RuntimeClass
                                                           ) -> Optional[List[RuntimeClass]]:
        """获取项目外的函数式接口 RuntimeClass 的 lambda 表达式的参数类型列表"""
        if runtime_class is None or runtime_class.absolute_name not in self._outer_lambda_param_type:
            return None
        return self._outer_lambda_param_type[runtime_class.absolute_name](runtime_class)

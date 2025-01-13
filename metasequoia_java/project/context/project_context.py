"""
项目级上下文
"""

import os
from typing import Callable, Dict, List, Optional

from metasequoia_java import ast, parse_compilation_unit
from metasequoia_java.project.context.base_context import ClassContextBase
from metasequoia_java.project.context.base_context import FileContextBase
from metasequoia_java.project.context.base_context import MethodContextBase
from metasequoia_java.project.context.base_context import ProjectContextBase
from metasequoia_java.project.context.class_context import ClassContext
from metasequoia_java.project.context.file_context import FileContext
from metasequoia_java.project.context.method_context import MethodContext
from metasequoia_java.project.elements import RuntimeClass
from metasequoia_java.project.elements import RuntimeMethod
from metasequoia_java.project.elements import RuntimeVariable
from metasequoia_java.project.utils import split_last_name_from_absolute_name


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

    def __init__(self,
                 project_path: str,
                 modules: Dict[str, List[str]],
                 outer_attribute_type: Optional[Dict[str, Callable[[RuntimeVariable], RuntimeClass]]] = None,
                 outer_method_return_type: Optional[Dict[str, Callable[[RuntimeMethod], RuntimeClass]]] = None):
        """

        Parameters
        ----------
        project_path : str
            项目根路径地址
        modules : Dict[str, List[str]]
            项目中 module 路径地址
        outer_attribute_type : Optional[Dict[Tuple[str, str], RuntimeClass]], default = None
            项目外已知属性类型
        outer_method_return_type : Optional[Dict[Tuple[str, str], RuntimeClass]], default = None
            项目外已知函数返回值类型
        """
        if outer_attribute_type is None:
            outer_attribute_type = {}
        if outer_method_return_type is None:
            outer_method_return_type = {}

        self._project_path = project_path
        self._modules: Dict[str, str] = {
            module_name: [os.path.join(project_path, path) for path in module_source_list]
            for module_name, module_source_list in modules.items()
        }
        self._outer_attribute_type = outer_attribute_type
        self._outer_method_return_type = outer_method_return_type

        # 绝对名称到所属文件路径的映射
        self._cache_file_node_to_file_path: Dict[str, ast.CompilationUnit] = {}
        self._cache_package_name_to_package_path: Dict[str, str] = {}

    @property
    def project_path(self) -> str:
        """返回项目根路径"""
        return self._project_path

    def get_file_node_by_file_path(self, file_path: str) -> ast.CompilationUnit:
        """根据 file_path（文件路径）获取 file_node（抽象语法树的文件节点）"""
        if file_path not in self._cache_file_node_to_file_path:
            with open(file_path, "r", encoding="UTF-8") as file:
                self._cache_file_node_to_file_path[file_path] = parse_compilation_unit(file.read())
        return self._cache_file_node_to_file_path[file_path]

    def get_file_node_by_absolute_name(self, absolute_name: str) -> ast.CompilationUnit:
        """根据 absolute_name（绝对引用名称）获取 file_node（抽象语法树的文件节点）"""
        package_name, class_name = split_last_name_from_absolute_name(absolute_name)
        return self.get_file_node_by_package_name_class_name(package_name, class_name)

    def get_file_node_by_package_name_class_name(self,
                                                 package_name: str,
                                                 class_name: str
                                                 ) -> Optional[ast.CompilationUnit]:
        """根据 absolute_name（绝对引用名称）获取 file_node（抽象语法树的文件节点）"""
        # 根据 package_name（包名称）获取 package_path（包路径）
        package_path = self.get_package_path_by_package_name(package_name)
        if package_path is None:
            return None

        # 获取类路径
        file_path = os.path.join(package_path, f"{class_name}.java")

        return self.get_file_node_by_file_path(file_path)

    def get_package_path_by_package_name(self, package_name: Optional[str]) -> Optional[str]:
        """根据 package_name（包名称）获取 package_path（包路径）"""
        if package_name is None:
            return None
        if package_name not in self._cache_package_name_to_package_path:
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

            if len(candidate_path_list) > 1:
                print(f"同一个包包含多个不同路径: {candidate_path_list}")  # 待改为 warning
                return None
            if len(candidate_path_list) == 0:
                return None

            self._cache_package_name_to_package_path[package_name] = candidate_path_list[0]

        return self._cache_package_name_to_package_path[package_name]

    def get_file_path_list_by_package_name(self, package_name: str) -> List[str]:
        """根据 package_name（包名称）获取其中所有 file_path（文件路径）"""
        package_path = self.get_package_path_by_package_name(package_name)
        if package_path is None:
            return []
        file_path_list = []
        for file_name in os.listdir(package_path):
            file_path = os.path.join(package_path, file_name)
            if os.path.isdir(file_path):  # 递归处理嵌套的包
                sub_package_name = f"{package_name}.{file_name}"
                file_path_list.extend(self.get_file_path_list_by_package_name(sub_package_name))
            else:
                file_path_list.append(file_path)
        return file_path_list

    def get_class_name_list_by_package_name(self, package_name: str) -> List[str]:
        """根据 package_name（包名称）获取其中所有模块内可见类的 class_name（类名）的列表"""
        file_path_list: List[str] = self.get_file_path_list_by_package_name(package_name)
        class_name_list: List[str] = []
        for file_path in file_path_list:
            file_node: ast.CompilationUnit = self.get_file_node_by_file_path(file_path)
            for class_declaration in file_node.get_class_declaration_list():
                if ast.Modifier.PRIVATE not in class_declaration.modifiers.flags:
                    class_name_list.append(class_declaration.name)
        return class_name_list

    # ------------------------------ 项目全局搜索方法 ------------------------------

    def create_file_context_by_class_absolute_name(self, class_absolute_name: str) -> Optional[FileContextBase]:
        """根据公有类的绝对引用名称，构造 FileContext 对象，如果不在当前项目中则返回 None"""
        return FileContext.create_by_public_class_absolute_name(self, class_absolute_name)

    def create_class_context_by_class_absolute_name(self, class_absolute_name: str) -> Optional[ClassContextBase]:
        """根据公有类的绝对引用名称，构造 ClassContext 对象，如果不在当前项目中则返回 None"""
        file_context = FileContext.create_by_public_class_absolute_name(self, class_absolute_name)
        if file_context is None:
            return None
        return ClassContext.create_by_public_class(file_context)

    def create_class_context_by_runtime_class(self, runtime_class: RuntimeClass) -> Optional[ClassContextBase]:
        """根据 runtimeClass 对象，构造 ClassContext 对象，如果不在当前项目中则返回 None"""
        if runtime_class is None:
            return None
        file_context = FileContext.create_by_public_class_absolute_name(self, runtime_class.absolute_name)
        if file_context is None:
            return None
        return ClassContext.create_by_public_class(file_context)

    def create_method_context_by_runtime_method(self, runtime_method: RuntimeMethod) -> Optional[MethodContextBase]:
        """根据 runtimeMethod 对象构造 MethodContext 对象，如果不在当前项目中则返回 None"""
        class_context = self.create_class_context_by_runtime_class(runtime_method.belong_class)
        if class_context is None:
            return None
        return MethodContext.create_by_method_name(class_context, runtime_method.method_name)

    def get_type_node_by_runtime_variable(self, runtime_variable: RuntimeVariable) -> Optional[ast.Tree]:
        """根据 runtimeVariable 返回值的类型，构造 runtimeClass"""
        file_context = FileContext.create_by_public_class_absolute_name(
            project_context=self,
            absolute_name=runtime_variable.belong_class.absolute_name
        )

        # runtime_variable.belong_class 不在项目中，尝试通过项目外已知方法返回值类型获取
        if file_context is None:
            res = self.try_get_outer_attribute_type(runtime_variable)
            if res is None:
                print(f"get_type_node_by_runtime_variable: 未知类型的属性 {runtime_variable}")
            return res

        # runtime_variable.belong_class 在项目中，获取变量类型
        class_node = file_context.get_class_node_by_class_name(runtime_variable.belong_class.class_name)
        variable_node = class_node.get_variable_by_name(runtime_variable.variable_name)
        return file_context.get_runtime_class_by_type_node(
            class_node=class_node,
            runtime_class=runtime_variable.belong_class,
            type_node=variable_node.variable_type
        )

    def get_runtime_class_by_runtime_method_return_type(self, runtime_method: RuntimeMethod) -> Optional[RuntimeClass]:
        """根据 runtimeMethod 返回值的类型，构造 runtimeClass"""
        file_context = FileContext.create_by_public_class_absolute_name(
            project_context=self,
            absolute_name=runtime_method.belong_class.absolute_name
        )

        # runtime_method.belong_class 不在项目中，尝试通过项目外已知方法返回值类型获取
        if file_context is None:
            return self.try_get_outer_method_return_type(runtime_method)

        # runtime_method.belong_class 在项目中，获取返回值类型
        class_node = file_context.get_class_node_by_class_name(runtime_method.belong_class.class_name)
        method_node = class_node.get_method_by_name(runtime_method.method_name)
        return file_context.get_runtime_class_by_type_node(
            class_node=class_node,
            runtime_class=runtime_method.belong_class,
            type_node=method_node.return_type
        )

    # ------------------------------ 获取项目外已知类型 ------------------------------
    def try_get_outer_attribute_type(self, runtime_variable: RuntimeVariable) -> Optional[RuntimeClass]:
        """获取项目外已知类属性类型"""
        if runtime_variable.absolute_name not in self._outer_attribute_type:
            return None
        return self._outer_attribute_type[runtime_variable.absolute_name](runtime_variable)

    def try_get_outer_method_return_type(self, runtime_method: RuntimeMethod) -> Optional[RuntimeClass]:
        """获取项目外已知方法返回值类型"""
        if runtime_method.absolute_name not in self._outer_method_return_type:
            return None
        return self._outer_method_return_type[runtime_method.absolute_name](runtime_method)

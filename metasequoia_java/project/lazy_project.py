"""
懒加载项目级代码目录
"""

import os
from typing import Dict, List, Tuple

from metasequoia_java import ast, parse_compilation_unit


class AnalyzeError(Exception):
    """分析异常"""


class LazyProject:
    """懒加载的项目级代码对象

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

    def __init__(self, project_path: str, modules: Dict[str, List[str]]):
        self._project_path = project_path
        self._modules: Dict[str, str] = {
            module_name: [os.path.join(project_path, path) for path in module_source_list]
            for module_name, module_source_list in modules.items()
        }

        # 绝对名称到所属文件路径的映射
        self._cache_file_node_to_file_path: Dict[str, ast.CompilationUnit] = {}
        self._cache_package_name_to_package_path: Dict[str, str] = {}

    @property
    def project_path(self) -> str:
        return self._project_path

    def get_file_node_by_file_path(self, file_path: str) -> ast.CompilationUnit:
        """根据 file_path（文件路径）获取 file_node（抽象语法树的文件节点）"""
        if file_path not in self._cache_file_node_to_file_path:
            with open(file_path, "r", encoding="UTF-8") as file:
                self._cache_file_node_to_file_path[file_path] = parse_compilation_unit(file.read())
        return self._cache_file_node_to_file_path[file_path]

    def get_file_node_by_absolute_name(self, absolute_name: str) -> ast.CompilationUnit:
        """根据 absolute_name（绝对引用名称）获取 file_node（抽象语法树的文件节点）"""
        # 拆分 package 和 class
        package_name, class_name = self.get_package_and_class_name_by_absolute_name(absolute_name)

        # 根据 package_name（包名称）获取 package_path（包路径）
        package_path = self.get_package_path_by_package_name(package_name)

        # 获取类路径
        file_path = os.path.join(package_path, f"{class_name}.java")

        return self.get_file_node_by_file_path(file_path)

    def get_package_path_by_package_name(self, package_name: str) -> str:
        """根据 package_name（包名称）获取 package_path（包路径）"""
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
                raise AnalyzeError(f"同一个包包含多个不同路径: {candidate_path_list}")
            if len(candidate_path_list) == 0:
                raise AnalyzeError(f"包路径不存在: {package_name}")

            self._cache_package_name_to_package_path[package_name] = candidate_path_list[0]

        return self._cache_package_name_to_package_path[package_name]

    def get_file_path_list_by_package_name(self, package_name: str) -> List[str]:
        """根据 package_name（包名称）获取其中所有 file_path（文件路径）"""
        package_path = self.get_package_path_by_package_name(package_name)
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

    @staticmethod
    def get_package_and_class_name_by_absolute_name(absolute_name: str) -> Tuple[str, str]:
        """获取 absolute_name（绝对名称）中获取 package_name 和 class_name"""
        if "." in absolute_name:
            return absolute_name[:absolute_name.rindex(".")], absolute_name[absolute_name.rindex(".") + 1:]
        else:
            return "", absolute_name

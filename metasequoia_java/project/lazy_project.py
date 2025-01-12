"""
懒加载项目级代码目录
"""

import os
from typing import Dict, Generator, List, Optional, Tuple

from metasequoia_java import ast, parse_compilation_unit
from metasequoia_java.project.elements import RuntimeClass
from metasequoia_java.project.elements import RuntimeMethod
from metasequoia_java.project.import_manager import ImportManager
from metasequoia_java.project.name_space import NameSpace


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
        package_name, class_name = self.get_package_and_class_name_by_absolute_name(absolute_name)
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

    def get_package_path_by_package_name(self, package_name: str) -> Optional[str]:
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
                print(f"同一个包包含多个不同路径: {candidate_path_list}")  # 待改为 warning
                return None
            if len(candidate_path_list) == 0:
                print(f"包路径不存在: {package_name}")  # 待改为 warning
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

    def get_import_manager_by_file_node(self,
                                        package_name: str,
                                        file_node: ast.CompilationUnit
                                        ) -> "ImportManager":
        """根据文件的抽象语法树节点构造引用映射管理器

        Parameters
        ----------
        package_name : str
            Java 文件所在包路径
        file_node : ast.CompilationUnit
            Java 文件级抽象语法树节点
        """
        import_hash = {}

        # 读取 import 语句中的引用映射关系
        for import_node in file_node.imports:
            absolute_name = import_node.identifier.generate()
            name = (absolute_name[absolute_name.rindex(".") + 1:] if "." in absolute_name else absolute_name)
            import_hash[name] = absolute_name

        # 读取 package 中其他类的引用关系
        for package_class_name in self.get_class_name_list_by_package_name(package_name):
            import_hash[package_class_name] = f"{package_name}.{package_class_name}"

        return ImportManager(import_hash)

    @staticmethod
    def get_package_and_class_name_by_absolute_name(absolute_name: str) -> Tuple[str, str]:
        """获取 absolute_name（绝对名称）中获取 package_name 和 class_name"""
        if "." in absolute_name:
            return absolute_name[:absolute_name.rindex(".")], absolute_name[absolute_name.rindex(".") + 1:]
        else:
            return "", absolute_name

    def get_method_invocation(self,
                              import_manager: ImportManager,
                              name_space: NameSpace,
                              package_name: str,
                              class_name: str,
                              statement_node: ast.Tree
                              ) -> Generator[RuntimeMethod, None, None]:
        """获取当前表达式中调用的方法

        适配场景：
        `name1()`
        `name1.name2()`
        `name1.name2.name3()`：依赖泛型解析器，获取 `name2` 的类型
        `name1().name2()` 或 `name1.name2().name3()`：依赖泛型管理器，获取 `name1()` 的类型
        """
        # -------------------- 递归结束条件 --------------------
        if statement_node.kind in {ast.TreeKind.IDENTIFIER, ast.TreeKind.INT_LITERAL, ast.TreeKind.LONG_LITERAL,
                                   ast.TreeKind.FLOAT_LITERAL, ast.TreeKind.DOUBLE_LITERAL, ast.TreeKind.CHAR_LITERAL,
                                   ast.TreeKind.STRING_LITERAL, ast.TreeKind.BOOLEAN_LITERAL,
                                   ast.TreeKind.NULL_LITERAL}:
            return

        # -------------------- 递归元素产出 --------------------
        if isinstance(statement_node, ast.MethodInvocation):

            method_select = statement_node.method_select

            # name1() -- 调用当前类的其他方法
            if isinstance(method_select, ast.Identifier):
                yield RuntimeMethod(
                    belong_class=RuntimeClass(package_name=package_name, class_name=class_name, type_arguments=None),
                    method_name=method_select.name
                )

            # name1.name2()
            # name1.name2.name3()
            elif isinstance(method_select, ast.MemberSelect):
                expression = method_select.expression
                runtime_class = self.get_runtime_class_by_node(import_manager, name_space, package_name, class_name,
                                                               expression)
                yield RuntimeMethod(
                    belong_class=runtime_class,
                    method_name=method_select.identifier.name
                )

            else:
                print(f"get_method_invocation, 暂不支持的表达式类型: {statement_node}")

            # 递归处理方法参数
            for argument in statement_node.arguments:
                yield from self.get_method_invocation(import_manager, name_space, package_name, class_name, argument)

            return

        if isinstance(statement_node, ast.NewClass):
            identifier = statement_node.identifier
            if isinstance(identifier, ast.Identifier):
                method_class_name = identifier.name
                method_package_name = import_manager.get_package_name(method_class_name)
                yield RuntimeMethod(
                    belong_class=RuntimeClass(package_name=method_package_name, class_name=method_class_name,
                                              type_arguments=None),
                    method_name=method_class_name
                )
            else:
                print("NewClass 暂不支持的类型: ", identifier)

            # 递归处理方法参数
            for argument in statement_node.arguments:
                yield from self.get_method_invocation(import_manager, name_space, package_name, class_name, argument)

            return

        # -------------------- 其他递归条件 --------------------
        if isinstance(statement_node, ast.Variable):
            next_node = statement_node.initializer
            yield from self.get_method_invocation(import_manager, name_space, package_name, class_name, next_node)
            return

        if isinstance(statement_node, ast.MemberSelect):
            next_node = statement_node.expression
            yield from self.get_method_invocation(import_manager, name_space, package_name, class_name, next_node)
            return

        if isinstance(statement_node, ast.ExpressionStatement):
            next_node = statement_node.expression
            yield from self.get_method_invocation(import_manager, name_space, package_name, class_name, next_node)
            return

        if isinstance(statement_node, ast.Assignment):
            next_node = statement_node.expression
            yield from self.get_method_invocation(import_manager, name_space, package_name, class_name, next_node)
            return

        print(statement_node)

    def get_runtime_class_by_node(self,
                                  import_manager: ImportManager,
                                  name_space: NameSpace,
                                  package_name: str,
                                  class_name: str,
                                  expression_node: ast.Tree) -> RuntimeClass:
        """获取节点元素的类型"""

        # name1
        if isinstance(expression_node, ast.Identifier):
            unknown_name = expression_node.name
            # 标识符是变量名
            if name_space.has_name(unknown_name):
                return self.get_runtime_class_by_type_node(
                    package_name=package_name,
                    class_name=class_name,
                    type_node=name_space.get_name(unknown_name)
                )

            # 标识符是类名
            return RuntimeClass(
                package_name=import_manager.get_package_name(unknown_name),
                class_name=unknown_name,
                type_arguments=[]
            )

        # name1.name2
        elif isinstance(expression_node, ast.MemberSelect):
            # 获取 name1 的类信息
            runtime_class = self.get_runtime_class_by_node(import_manager, name_space, package_name, class_name,
                                                           expression_node.expression)
            print("runtime_class:", runtime_class)
            # 获取 name2 的类型
            type_node = self.get_variable_type_node(
                package_name=runtime_class.package_name,
                class_name=runtime_class.class_name,
                variable_name=expression_node.identifier.name
            )
            return self.get_runtime_class_by_type_node(
                package_name=package_name,
                class_name=class_name,
                type_node=type_node
            )

        else:
            print(f"get_runtime_class_by_node: 暂不支持的表达式 {expression_node}")

    def get_variable_type_node(self, package_name: str, class_name: str, variable_name: str) -> Optional[ast.Tree]:
        """获取 package_name.class_name 中 variable_name 的类型节点"""
        file_node = self.get_file_node_by_package_name_class_name(package_name=package_name, class_name=class_name)
        if file_node is None:
            return None
        class_node = file_node.get_class_by_name(class_name)
        variable_node = class_node.get_variable_by_name(variable_name)
        return variable_node.variable_type

    def get_runtime_class_by_type_node(self,
                                       package_name: str,
                                       class_name: str,
                                       type_node: ast.Tree
                                       ) -> Optional[RuntimeClass]:
        """根据 type_node 获取 runtime_class 对象"""
        file_node = self.get_file_node_by_package_name_class_name(package_name, class_name)
        import_manager = self.get_import_manager_by_file_node(package_name, file_node)

        if isinstance(type_node, ast.Identifier):
            class_name = type_node.name
            return RuntimeClass(
                package_name=import_manager.get_package_name(class_name),
                class_name=class_name,
                type_arguments=[]
            )
        elif isinstance(type_node, ast.ParameterizedType):
            class_name = type_node.type_name.generate()
            if "." not in class_name:
                package_name = import_manager.get_package_name(class_name)
            else:
                package_name = class_name[:class_name.rindex(".")]
                class_name = class_name[class_name.rindex(".") + 1:]
            type_arguments = [
                self.get_runtime_class_by_type_node(package_name, class_name, argument)
                for argument in type_node.type_arguments
            ]
            return RuntimeClass(
                package_name=package_name,
                class_name=class_name,
                type_arguments=type_arguments
            )
        else:
            print(f"get_runtime_class_by_type_node: 暂不支持的表达式 {type_node}")
            return None

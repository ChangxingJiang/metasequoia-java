"""
文件级上下文
"""

from typing import Dict, Optional

from metasequoia_java import ast
from metasequoia_java.common import LOGGER
from metasequoia_java.project.constants import JAVA_LANG_CLASS_NAME_SET
from metasequoia_java.project.context.base_context import FileContextBase
from metasequoia_java.project.context.base_context import ProjectContextBase
from metasequoia_java.project.elements import RuntimeClass
from metasequoia_java.project.elements import RuntimeMethod
from metasequoia_java.project.elements import RuntimeVariable
from metasequoia_java.project.utils import split_last_name_from_absolute_name

__all__ = [
    "FileContext"
]


class FileContext(FileContextBase):
    """文件级上下文"""

    def __init__(self,
                 project_context: ProjectContextBase,
                 package_name: str,
                 public_class_name: str,
                 file_node: ast.CompilationUnit):
        self._project_context = project_context
        self._package_name = package_name
        self._public_class_name = public_class_name
        self._file_node = file_node

        self._import_class_hash: Dict[str, RuntimeClass] = {}
        self._import_variable_hash: Dict[str, RuntimeVariable] = {}
        self._import_method_hash: Dict[str, RuntimeMethod] = {}
        self._init_import_hash()

    @staticmethod
    def create_by_public_class_absolute_name(project_context: ProjectContextBase,
                                             absolute_name: str
                                             ) -> Optional["FileContext"]:
        """使用公有类的绝对引用路径构造 FileContext"""
        package_name, class_name = split_last_name_from_absolute_name(absolute_name)
        file_node: ast.CompilationUnit = project_context.get_file_node_by_absolute_name(absolute_name)
        if file_node is None:
            return None
        return FileContext(
            project_context=project_context,
            package_name=package_name,
            public_class_name=class_name,
            file_node=file_node
        )

    @property
    def project_context(self) -> ProjectContextBase:
        """返回所属项目上下文管理器"""
        return self._project_context

    @property
    def package_name(self) -> str:
        """返回所属 package 名称"""
        return self._package_name

    @property
    def public_class_name(self) -> str:
        """返回文件中的公有类名称"""
        return self._public_class_name

    @property
    def file_node(self) -> ast.CompilationUnit:
        """返回文件的抽象语法树节点"""
        return self._file_node

    @property
    def import_class_hash(self) -> Dict[str, RuntimeClass]:
        """返回类引用映射"""
        return self._import_class_hash

    @property
    def import_variable_hash(self) -> Dict[str, RuntimeVariable]:
        """返回静态属性引用映射"""
        return self._import_variable_hash

    @property
    def import_method_hash(self) -> Dict[str, RuntimeMethod]:
        """返回静态方法引用映射"""
        return self._import_method_hash

    # ------------------------------ class 层级处理方法 ------------------------------

    def get_public_class_declaration(self) -> ast.Class:
        """返回公有类的抽象语法树节点"""
        return self._file_node.get_public_class()

    def get_class_node_by_class_name(self, class_name) -> Optional[ast.Class]:
        """根据 class_name 获取指定类的抽象语法树节点"""
        return self._file_node.get_class_by_name(class_name)

    # ------------------------------ 引用映射管理器 ------------------------------

    def _init_import_hash(self) -> None:
        """构造文件中包含的引用逻辑

        在 Java 中，导入的优先级从高到低如下：
        1. 精确导入：import package.ClassName;
        2. 通配符导入：import package.*;
        3. 静态精确导入：import static package.ClassName.staticMember;
        4. 静态通配符导入：import static package.ClassName.*;
        5. package 中的其他类
        """
        # 精确导入：import package.ClassName;
        for import_node in self.file_node.imports:
            if import_node.is_static is True:
                continue
            package_name, class_name = split_last_name_from_absolute_name(import_node.identifier.generate())
            if class_name == "*":
                continue
            self._import_class_hash[class_name] = RuntimeClass(
                package_name=package_name,
                class_name=class_name,
                type_arguments=[]
            )

        # 通配符导入：import package.*;
        for import_node in self.file_node.imports:
            if import_node.is_static is True:
                continue
            package_name, class_name = split_last_name_from_absolute_name(import_node.identifier.generate())
            if class_name != "*":
                continue
            class_name_list = self.project_context.get_class_name_list_by_package_name(package_name)
            if class_name_list is None:
                LOGGER.warning(f"无法通过 package_name 获取其中包含的 class_name 列表: {package_name}")
                continue
            for class_name in class_name_list:
                if class_name not in self._import_class_hash:
                    self._import_class_hash[class_name] = RuntimeClass(
                        package_name=package_name,
                        class_name=class_name,
                        type_arguments=[]
                    )

        # 静态精确导入：import static package.ClassName.staticMember;
        for import_node in self.file_node.imports:
            if import_node.is_static is False:
                continue
            class_name, unknown_name = split_last_name_from_absolute_name(import_node.identifier.generate())
            if unknown_name == "*":
                continue
            package_name, class_name = split_last_name_from_absolute_name(class_name)

            # TODO 向 method 和 variable 中分别插入一条，待增加优先解析类的方法
            self._import_method_hash[unknown_name] = RuntimeMethod(
                belong_class=RuntimeClass(package_name=package_name, class_name=class_name, type_arguments=[]),
                method_name=unknown_name
            )
            self._import_variable_hash[unknown_name] = RuntimeVariable(
                belong_class=RuntimeClass(package_name=package_name, class_name=class_name, type_arguments=[]),
                variable_name=unknown_name
            )

        # 静态通配符导入：import static package.ClassName.*;
        for import_node in self.file_node.imports:
            if import_node.is_static is False:
                continue
            class_name, method_name = split_last_name_from_absolute_name(import_node.identifier.generate())
            if method_name != "*":
                continue
            package_name, class_name = split_last_name_from_absolute_name(class_name)
            runtime_class = RuntimeClass(package_name=package_name, class_name=class_name, type_arguments=[])

            # 获取静态属性
            variable_name_list = self.project_context.get_static_variable_name_list_by_runtime_class(runtime_class)
            if variable_name_list is None:
                LOGGER.warning(f"无法通过 runtime_class 获取其中包含静态 variable_name 列表: {runtime_class}")
            else:
                for variable_name in variable_name_list:
                    self._import_variable_hash[method_name] = RuntimeVariable(
                        belong_class=runtime_class,
                        variable_name=variable_name
                    )

            # 获取静态方法
            method_name_list = self.project_context.get_static_method_name_list_by_runtime_class(runtime_class)
            if method_name_list is None:
                LOGGER.warning(f"无法通过 runtime_class 获取其中包含静态 method_name 列表: {runtime_class}")
            else:
                for method_name in method_name_list:
                    self._import_method_hash[method_name] = RuntimeMethod(
                        belong_class=runtime_class,
                        method_name=method_name
                    )

        # 读取 package 中其他类的引用关系
        class_name_list = self.project_context.get_class_name_list_by_package_name(self.package_name)
        if class_name_list is None:
            LOGGER.warning(f"无法通过 package_name 获取其中包含的 class_name 列表: {self.package_name}")
        else:
            for class_name in class_name_list:
                # 检查是否有更高优先级的引用
                if class_name not in self._import_class_hash:
                    self._import_class_hash[class_name] = RuntimeClass(
                        package_name=self.package_name,
                        class_name=class_name,
                        type_arguments=[]
                    )

    def import_contains_class_name(self, class_name: str) -> bool:
        """返回引用映射中是否包含类型"""
        return class_name in self._import_class_hash

    def get_import_absolute_name_by_class_name(self, class_name: str) -> Optional[str]:
        """根据 class_name，获取引用映射中的完整名称"""
        if class_name not in self._import_class_hash:
            return None
        return self._import_class_hash[class_name].absolute_name

    def get_import_package_name_by_class_name(self, class_name: str) -> Optional[str]:
        """获取 class_name，获取引用映射中的包名称"""
        if class_name in self._import_class_hash:
            return self._import_class_hash[class_name].package_name
        if class_name in JAVA_LANG_CLASS_NAME_SET:
            return "java.lang"
        return None

    def get_runtime_class_by_type_node(self,
                                       class_node: ast.Class,
                                       runtime_class: RuntimeClass,
                                       type_node: ast.Tree) -> Optional[RuntimeClass]:
        """
        根据抽象语法树节点 class_node 中（运行中为 runtime_class），表示类型的抽象语法树节点 type_node，构造该类型对应的 runtime_class
        对象

        TODO 参数待优化
        """
        if isinstance(type_node, ast.Identifier):
            class_name = type_node.name
            package_name = self.get_import_package_name_by_class_name(class_name)

            # 引用的类
            if package_name is not None:
                return RuntimeClass(
                    package_name=package_name,
                    class_name=class_name,
                    type_arguments=[]
                )

            # java.lang 模块中的类
            if class_name in JAVA_LANG_CLASS_NAME_SET:
                return RuntimeClass(
                    package_name="java.lang",
                    class_name=class_name,
                    type_arguments=[]
                )

            # 没有引用关系，可能是泛型
            if runtime_class.type_arguments is not None:
                for idx, type_argument in enumerate(class_node.type_parameters):
                    if isinstance(type_argument, ast.TypeParameter):
                        if type_argument.name == class_name:
                            return runtime_class.type_arguments[idx]
                    else:
                        print("未知泛型参数节点:", type_argument)

            # 当前文件中的其他类
            class_name_list = self.file_node.get_class_name_list()
            if class_name in class_name_list:
                # TODO 考虑不是公有类的情况
                return RuntimeClass(
                    package_name=self.package_name,
                    class_name=class_name,
                    type_arguments=[]
                )

            LOGGER.warning(f"无法根据抽象语法树节点获取类型: "
                           f"class_name={class_name}, "
                           f"position={self.package_name}.{self.public_class_name}")

            return RuntimeClass(
                package_name=None,
                class_name=type_node.generate(),
                type_arguments=None
            )

        if isinstance(type_node, ast.ParameterizedType):
            class_name = type_node.type_name.generate()
            if "." not in class_name:
                # "类名"
                package_name = self.get_import_package_name_by_class_name(class_name)
            else:
                # "包名.类名"
                package_name = class_name[:class_name.rindex(".")]
                class_name = class_name[class_name.rindex(".") + 1:]
                if self.import_contains_class_name(package_name):
                    # "主类名.子类名"
                    main_class_name = package_name  # 主类名
                    package_name = self.get_import_package_name_by_class_name(main_class_name)
                    class_name = f"{main_class_name}.{class_name}"
            type_arguments = [
                self.get_runtime_class_by_type_node(class_node, runtime_class, argument)
                for argument in type_node.type_arguments
            ]
            return RuntimeClass(
                package_name=package_name,
                class_name=class_name,
                type_arguments=type_arguments
            )

        # 将 Java 数组模拟为 java.lang.Array[xxx]
        if isinstance(type_node, ast.ArrayType):
            runtime_class = self.get_runtime_class_by_type_node(class_node, runtime_class, type_node.expression)
            return RuntimeClass(
                package_name="java.lang",
                class_name="Array",
                type_arguments=[runtime_class]
            )

        print(f"get_runtime_class_by_type_node: 暂不支持的表达式 {type_node}")
        return None

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

    def __repr__(self) -> str:
        return f"<FileContext package_name={self.package_name}, public_class_name={self.public_class_name}>"

    @staticmethod
    def create_by_runtime_class(project_context: ProjectContextBase,
                                runtime_class: Optional[RuntimeClass]
                                ) -> Optional["FileContext"]:
        """使用公有类或飞公有类的 RuntimeClass 构造 FileContext 对象"""
        if runtime_class is None:
            return None
        file_node: ast.CompilationUnit = project_context.get_file_node_by_runtime_class(runtime_class)
        if file_node is None:
            return None
        return FileContext(
            project_context=project_context,
            package_name=runtime_class.package_name,
            public_class_name=runtime_class.public_class_name,
            file_node=file_node
        )

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
        return self.file_node.get_public_class()

    def get_class_node_by_class_name(self, class_name: str) -> Optional[ast.Class]:
        """根据 class_name 获取指定类的抽象语法树节点，如果获取不到则返回 None"""
        if "." in class_name:
            return self.file_node.get_inner_class_by_name(class_name)  # 根据内部类名获取类的抽象语法树节点
        return self.file_node.get_class_by_name(class_name)  # 根据类名获取类的抽象语法树节点

    # ------------------------------ 引用映射管理器 ------------------------------

    def _init_import_hash(self) -> None:
        """构造文件中包含的引用逻辑

        在 Java 中，导入的优先级从高到低如下：
        1. 当前文件中的类（包含子类）
        2. 精确导入：import package.ClassName;
        3. 通配符导入：import package.*;
        4. 静态精确导入：import static package.ClassName.staticMember;
        5. 静态通配符导入：import static package.ClassName.*;
        6. package 中的其他类
        7. java.lang 中的类
        """
        for class_name in self.file_node.get_class_and_sub_class_name_list():
            runtime_class = RuntimeClass.create(
                package_name=self.package_name,
                public_class_name=self.public_class_name,
                class_name=class_name,
                type_arguments=None
            )

            # 将当前文件中的 ClassName 和 ClassName.SubClassName 添加到引用映射管理器中
            self._import_class_hash[class_name] = runtime_class

            # 将当前文件中的 SubClassName 添加到引用映射管理器中
            if "." in class_name:
                sub_class_name = class_name[class_name.rindex(".") + 1:]
                self._import_class_hash[sub_class_name] = runtime_class

        # 精确导入：import package.ClassName;
        for import_node in self.file_node.imports:
            if import_node.is_static is True:
                continue
            package_name, class_name = split_last_name_from_absolute_name(import_node.identifier.generate())
            if class_name == "*":
                continue
            if class_name not in self._import_class_hash:
                self._import_class_hash[class_name] = RuntimeClass.create(
                    package_name=package_name,
                    public_class_name=class_name,
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
                    self._import_class_hash[class_name] = RuntimeClass.create(
                        package_name=package_name,
                        public_class_name=class_name,
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
                belong_class=RuntimeClass.create(
                    package_name=package_name,
                    public_class_name=class_name,
                    class_name=class_name,
                    type_arguments=[]
                ),
                method_name=unknown_name
            )
            self._import_variable_hash[unknown_name] = RuntimeVariable(
                belong_class=RuntimeClass.create(
                    package_name=package_name,
                    public_class_name=class_name,
                    class_name=class_name,
                    type_arguments=[]
                ),
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
            runtime_class = RuntimeClass.create(
                package_name=package_name,
                public_class_name=class_name,
                class_name=class_name,
                type_arguments=[]
            )

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
                    self._import_class_hash[class_name] = RuntimeClass.create(
                        package_name=self.package_name,
                        public_class_name=class_name,
                        class_name=class_name,
                        type_arguments=[]
                    )

        # 加载 java.lang 中的类
        for class_name in JAVA_LANG_CLASS_NAME_SET:
            if class_name not in self._import_class_hash:
                self._import_class_hash[class_name] = RuntimeClass.create(
                    package_name="java.lang",
                    public_class_name=class_name,
                    class_name=class_name,
                    type_arguments=[]
                )

    def import_contains_class_name(self, class_name: str) -> bool:
        """返回引用映射中是否包含类型"""
        return class_name in self._import_class_hash

    def infer_runtime_class_by_identifier_name(self,
                                               identifier_name: str,
                                               need_warning: bool = True) -> Optional[RuntimeClass]:
        """根据当前文件中出现的 class_name，获取对应的 RuntimeClass 对象"""
        if identifier_name in self._import_class_hash:
            return self._import_class_hash[identifier_name]
        if need_warning is True:
            LOGGER.error(f"使用了未知的标识符: {identifier_name}, "
                         f"position={self.package_name}.{self.public_class_name}")
        return None

    def infer_runtime_class_by_node(self, type_node: Optional[ast.Tree]) -> Optional[RuntimeClass]:
        """
        推断当前文件中出现的抽象语法树节点的类型

        TODO 参数待优化
        """
        if type_node is None:
            return None

        if isinstance(type_node, ast.Identifier):
            class_name = type_node.name

            # 根据当前文件中出现的 class_name，获取对应的 RuntimeClass 对象
            # 1. 当前文件中的类（包含公有类、非公有类和子类）
            # 2. 精确导入：import package.ClassName;
            # 3. 通配符导入：import package.*;
            # 4. 静态精确导入：import static package.ClassName.staticMember;
            # 5. 静态通配符导入：import static package.ClassName.*;
            # 6. package 中的其他类
            # 7. java.lang 中的类
            if result := self.infer_runtime_class_by_identifier_name(class_name):
                return result

            LOGGER.warning(f"无法根据抽象语法树节点获取类型: "
                           f"class_name={class_name}, "
                           f"position={self.package_name}.{self.public_class_name}")

            return RuntimeClass.create(
                package_name=None,
                public_class_name=type_node.generate(),
                class_name=type_node.generate(),
                type_arguments=None
            )

        # 将 Java 数组模拟为 java.lang.Array[xxx]  TODO 在 MethodContext 中已复制，待判断这里是否还有意义
        if isinstance(type_node, ast.ArrayType):
            runtime_class = self.infer_runtime_class_by_node(type_node.expression)
            return RuntimeClass.create(
                package_name="java.lang",
                public_class_name="Array",
                class_name="Array",
                type_arguments=[runtime_class]
            )

        LOGGER.error(f"get_runtime_class_by_type_node: 暂不支持的表达式 {type_node}")
        return None

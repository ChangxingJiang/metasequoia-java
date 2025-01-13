"""
文件级上下文
"""

from typing import Dict, Optional

from metasequoia_java import ast
from metasequoia_java.project.context.project_context import ProjectContext
from metasequoia_java.project.elements import RuntimeType
from metasequoia_java.project.utils import get_package_and_class_name_by_absolute_name

__all__ = [
    "FileContext"
]


class FileContext:
    """文件级上下文"""

    def __init__(self,
                 project_context: ProjectContext,
                 package_name: str,
                 public_class_name: str,
                 file_node: ast.CompilationUnit):
        self.project_context = project_context
        self.package_name = package_name
        self.public_class_name = public_class_name
        self.file_node = file_node

        self.import_hash: Dict[str, RuntimeType] = self.create_import_hash()

    @staticmethod
    def create_by_public_class_absolute_name(project_context: ProjectContext, absolute_name: str) -> "FileContext":
        """使用公有类的绝对引用路径构造 FileContext"""
        package_name, class_name = get_package_and_class_name_by_absolute_name(absolute_name)
        file_node: ast.CompilationUnit = project_context.get_file_node_by_absolute_name(absolute_name)
        return FileContext(
            project_context=project_context,
            package_name=package_name,
            public_class_name=class_name,
            file_node=file_node
        )

    def get_public_class_declaration(self) -> ast.Class:
        """返回公有类的抽象语法树节点"""
        return self.file_node.get_public_class()

    def get_class_declaration_by_class_name(self, class_name) -> Optional[ast.Class]:
        """根据 class_name 获取指定类的抽象语法树节点"""
        return self.file_node.get_class_by_name(class_name)

    # ------------------------------ 引用映射管理器 ------------------------------

    def create_import_hash(self) -> Dict[str, RuntimeType]:
        """构造文件中包含的引用逻辑"""
        import_hash = {}

        # 读取 import 语句中的引用映射关系
        for import_node in self.file_node.imports:
            absolute_name = import_node.identifier.generate()
            package_name, class_name = get_package_and_class_name_by_absolute_name(absolute_name)
            import_hash[class_name] = RuntimeType(package_name=package_name, class_name=class_name, type_arguments=[])

        # 读取 package 中其他类的引用关系
        for class_name in self.project_context.get_class_name_list_by_package_name(self.package_name):
            import_hash[class_name] = RuntimeType(package_name=self.package_name, class_name=class_name,
                                                  type_arguments=[])

        return import_hash

    def get_import_absolute_name_by_class_name(self, class_name: str) -> Optional[str]:
        """根据 class_name，获取引用映射中的完整名称"""
        if class_name not in self.import_hash:
            return None
        return self.import_hash[class_name].absolute_name

    def get_import_package_name_by_class_name(self, class_name: str) -> Optional[str]:
        """获取 class_name，获取引用映射中的包名称"""
        if class_name not in self.import_hash:
            return None
        return self.import_hash[class_name].package_name

"""
命名空间管理器

TODO 待将 ast.Tree 替换为 ast.Type
"""

from typing import Dict, List, Optional

from metasequoia_java import ast

__all__ = [
    "SimpleNameSpace",
    "NameSpace",
]


class SimpleNameSpace:
    """单层命名空间"""

    def __init__(self):
        self._space: Dict[str, ast.Tree] = {}  # variable_name（变量名）到 gsp_type（通用语法树类型节点）的映射关系

    def set_name(self, variable_name: str, variable_type: ast.Tree) -> None:
        """添加 variable_name 到 gsp_type 的映射关系"""
        self._space[variable_name] = variable_type

    def get_name(self, variable_name: str, default: Optional[ast.Tree] = None) -> ast.Tree:
        """返回 variable_name 对应的 gsp_type"""
        return self._space.get(variable_name, default)

    def contains(self, variable_name: str) -> bool:
        """返回是否包含 variable_name"""
        return variable_name in self._space

    def name_list(self) -> List[str]:
        """获取 variable_name 的列表"""
        return list(self._space)

    def __add__(self, other: "SimpleNameSpace") -> "SimpleNameSpace":
        for variable_name, variable_type in other._space.items():
            self._space[variable_name] = variable_type
        return self

    def __repr__(self):
        space_text = ", ".join(f"{variable_name}={gst_type.generate()}"
                               for variable_name, gst_type in self._space.items())
        return f"<NameSpace {space_text}>"

    @staticmethod
    def create_by_class(class_node: ast.Class) -> "SimpleNameSpace":
        """根据类变量构造单层命名空间"""
        simple_name_space = SimpleNameSpace()
        for variable in class_node.get_variable_list():
            simple_name_space.set_name(variable.name, variable.variable_type)
        return simple_name_space

    @staticmethod
    def create_by_method_params(method_node: ast.Method) -> "SimpleNameSpace":
        """根据方法的参数构造单层命名空间"""
        simple_name_space = SimpleNameSpace()
        for variable in method_node.parameters:
            simple_name_space.set_name(variable.name, variable.variable_type)
        return simple_name_space

    @staticmethod
    def create_by_method_body(method_node: ast.Method) -> "SimpleNameSpace":
        """根据方法的代码块构造单层命名空间"""
        simple_name_space = SimpleNameSpace()
        for statement in method_node.block.statements:
            if isinstance(statement, ast.Variable):  # 赋值语句
                simple_name_space.set_name(statement.name, statement.variable_type)
        return simple_name_space


class NameSpace:
    """命令空间管理器"""

    def __init__(self, name_space: Optional[SimpleNameSpace] = None):
        self._stack: List[SimpleNameSpace] = []
        self.add_space(name_space)

    @property
    def level(self) -> int:
        return len(self._stack)

    def add_space(self, name_space: Optional[SimpleNameSpace] = None) -> None:
        """入栈一层命名空间"""
        if name_space is None:
            name_space = SimpleNameSpace()
        self._stack.append(name_space)

    def pop_space(self) -> SimpleNameSpace:
        """出栈一层命名空间"""
        return self._stack.pop()

    def set_name(self, variable_name: str, gst_type: ast.Tree) -> None:
        """在栈顶命名空间中添加 variable_name 到 gsp_type 的映射关系"""
        self._stack[-1].set_name(variable_name, gst_type)

    def get_name(self, variable_name: str, default: Optional[ast.Tree] = None) -> ast.Tree:
        """返回 variable_name 对应的 gsp_type"""
        for i in range(self.level - 1, -1, -1):
            if self._stack[i].contains(variable_name):
                return self._stack[i].get_name(variable_name)
        return default

    def has_name(self, variable_name: str) -> bool:
        """返回是否包含 variable_name"""
        for i in range(self.level - 1, -1, -1):
            if self._stack[i].contains(variable_name):
                return True
        return False

    def get_actual_name_space(self) -> SimpleNameSpace:
        """获取在当前状态下，实际可以访问的命名空间（不包括被覆盖的外层命名空间变量）"""
        actual_name_space = SimpleNameSpace()
        for simple_name_space in self._stack:  # 从外层向内层遍历
            for variable_name in simple_name_space.name_list():
                actual_name_space.set_name(variable_name, simple_name_space.get_name(variable_name))
        return actual_name_space

    def __repr__(self):
        return repr(self.get_actual_name_space())
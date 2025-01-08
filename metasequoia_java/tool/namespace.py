"""
命名空间管理器
"""

from typing import Dict, List, Optional

__all__ = [
    "NameSpace",
    "NameSpaceManager",
]


class NameSpace:
    """命名空间管理器"""

    def __init__(self):
        self._type_space: Dict[str, str] = {}  # class_name（类名）到 absolute_name（完整路径）的映射关系
        self._name_space: Dict[str, str] = {}  # variable_name（变量名）到 class_name（变量类型名）的映射关系

    def set_type_info(self, class_name: str, absolute_name: str) -> None:
        """添加 class_name 到 absolute_name 的映射"""
        self._type_space[class_name] = absolute_name

    def get_type_absolute_name(self, class_name: str) -> str:
        """返回 class_name 对应的 absolute_name"""
        return self._type_space[class_name]

    def has_type(self, class_name: str) -> bool:
        """返回是否包含 class_name 到 absolute_name 的映射"""
        return class_name in self._type_space

    def set_variable_info(self, variable_name: str, class_name: str) -> None:
        """添加 variable_name 到 class_name 的映射"""
        self._name_space[variable_name] = class_name

    def get_variable_type(self, variable_name: str) -> str:
        """返回 variable_name 对应的 class_name"""
        return self._name_space[variable_name]

    def get_variable_type_absolute_name(self, variable_name: str) -> str:
        """返回 variable_name 对应 class_name 对应的 full_name"""
        class_name = self._name_space[variable_name]
        return self._type_space[class_name]

    def has_variable(self, variable_name: str) -> bool:
        """返回是否包含 variable_name 到 class_name 的映射"""
        return variable_name in self._name_space

    def __repr__(self):
        return f"<NameSpace type_space={self._type_space}, name_space={self._name_space}>"


class NameSpaceManager:
    """命令空间管理器"""

    def __init__(self, name_space: Optional[NameSpace] = None):
        self._stack: List[NameSpace] = []
        if name_space is not None:
            self._stack.append(name_space)

    @property
    def level(self) -> int:
        return len(self._stack)

    def push_space(self, name_space: NameSpace) -> None:
        """入栈一层命名空间"""
        self._stack.append(name_space)

    def pop_space(self) -> NameSpace:
        """出栈一层命名空间"""
        return self._stack.pop()

    def set_type_info(self, class_name: str, absolute_name: str) -> None:
        """在栈顶命名空间中添加 class_name 到 full_name 的映射"""
        self._stack[-1].set_type_info(class_name, absolute_name)

    def set_variable_info(self, variable_name: str, class_name: str) -> None:
        """在栈顶命名空间中添加 variable_name 到 class_name 的映射"""
        self._stack[-1].set_variable_info(variable_name, class_name)

    def get_type_absolute_name(self, class_name: str) -> str:
        """从所有命名空间中返回 class_name 对应的 full_name"""
        for i in range(self.level - 1, -1, -1):
            if self._stack[i].has_type(class_name):
                return self._stack[i].get_type_absolute_name(class_name)
        raise KeyError(f"{class_name} 在命名空间中不存在")

    def get_variable_type(self, variable_name: str) -> str:
        """从所有命名空间中返回 variable_name 对应的 class_name"""
        for i in range(self.level - 1, -1, -1):
            if self._stack[i].has_variable(variable_name):
                return self._stack[i].get_variable_type(variable_name)
        raise KeyError(f"{variable_name} 在命名空间中不存在")

    def get_variable_type_absolute_name(self, variable_name: str) -> str:
        """从所有命名空间中返回 variable_name 对应 class_name 对应的 full_name"""
        for i in range(self.level - 1, -1, -1):
            if self._stack[i].has_variable(variable_name):
                return self._stack[i].get_variable_type_absolute_name(variable_name)
        raise KeyError(f"{variable_name} 在命名空间中不存在")

    def __repr__(self):
        return f"<NameSpaceManager stack={self._stack}>"

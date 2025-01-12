"""
运行中的类型
"""

import dataclasses
from typing import List

__all__ = [
    "RuntimeType"
]


@dataclasses.dataclass(slots=True)
class RuntimeType:
    """运行中的类型对象"""

    package_name: str = dataclasses.field(kw_only=True)
    class_name: str = dataclasses.field(kw_only=True)
    type_arguments: List["RuntimeType"] = dataclasses.field(kw_only=True)  # 泛型

    @property
    def absolute_name(self) -> str:
        """获取绝对引用名称"""
        return f"{self.package_name}.{self.class_name}"

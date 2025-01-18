"""
运行中的类型（类）
"""

import dataclasses
from typing import List, Optional

from metasequoia_java.project.utils.name_utils import split_last_name_from_absolute_name

__all__ = [
    "RuntimeClass"
]


@dataclasses.dataclass(slots=True)
class RuntimeClass:
    """运行中的类型（类）"""

    package_name: Optional[str] = dataclasses.field(kw_only=True)
    public_class_name: str = dataclasses.field(kw_only=True)
    class_name: str = dataclasses.field(kw_only=True)
    type_arguments: Optional[List["RuntimeClass"]] = dataclasses.field(kw_only=True)  # 泛型（如果未知则为 None）

    @staticmethod
    def create_by_public_class_absolute_name(absolute_name: str) -> "RuntimeClass":
        """根据公有类的绝对引用名称构造 RuntimeClass 对象"""
        package_name, class_name = split_last_name_from_absolute_name(absolute_name)
        return RuntimeClass(
            package_name=package_name,
            public_class_name=class_name,
            class_name=class_name,
            type_arguments=None
        )

    @property
    def absolute_name(self) -> str:
        """获取绝对引用名称"""
        if self.package_name is None:
            return self.class_name
        return f"{self.package_name}.{self.class_name}"

    def __repr__(self) -> str:
        if self.type_arguments is None:
            return (f"<RuntimeClass "
                    f"package={self.package_name}, "
                    f"class={self.class_name}>")
        else:
            return (f"<RuntimeClass "
                    f"package={self.package_name}, "
                    f"class={self.class_name}, "
                    f"type_arguments={self.type_arguments}>")

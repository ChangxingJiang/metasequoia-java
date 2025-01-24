"""
运行中的类型（类）
"""

import dataclasses
from typing import List, Optional, Tuple

from metasequoia_java.sa.utils.name_utils import split_last_name_from_absolute_name

__all__ = [
    "RuntimeClass"
]


@dataclasses.dataclass(slots=True, frozen=True)
class RuntimeClass:
    """运行中的类型（类）"""

    package_name: Optional[str] = dataclasses.field(kw_only=True)
    public_class_name: str = dataclasses.field(kw_only=True)
    class_name: str = dataclasses.field(kw_only=True)
    type_arguments: Optional[Tuple["RuntimeClass"]] = dataclasses.field(kw_only=True)  # 泛型（如果未知则为 None）

    @staticmethod
    def create(package_name: Optional[str],
               public_class_name: str,
               class_name: str,
               type_arguments: Optional[List["RuntimeClass"]]) -> "RuntimeClass":
        return RuntimeClass(
            package_name=package_name,
            public_class_name=public_class_name,
            class_name=class_name,
            type_arguments=tuple(type_arguments) if type_arguments is not None else None
        )

    @staticmethod
    def create_by_public_class_absolute_name(absolute_name: str) -> "RuntimeClass":
        """根据公有类的绝对引用名称构造 RuntimeClass 对象"""
        package_name, class_name = split_last_name_from_absolute_name(absolute_name)
        return RuntimeClass.create(
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

    @property
    def sub_class_name(self) -> Optional[str]:
        """获取子类名称，如果不是子类则返回 None"""
        if "." not in self.class_name:
            return None
        return self.class_name[self.class_name.rindex(".") + 1:]

    def __repr__(self) -> str:
        if self.type_arguments is None:
            return (f"<RuntimeClass "
                    f"package={self.package_name}, "
                    f"public_class={self.public_class_name}, "
                    f"class={self.class_name}>")
        else:
            return (f"<RuntimeClass "
                    f"package={self.package_name}, "
                    f"public_class={self.public_class_name}, "
                    f"class={self.class_name}, "
                    f"type_arguments={self.type_arguments}>")

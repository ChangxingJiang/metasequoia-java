"""
运行中的方法
"""

import dataclasses

from metasequoia_java.sa.elements.runtime_class import RuntimeClass

__all__ = [
    "RuntimeMethod"
]


@dataclasses.dataclass(slots=True, frozen=True)
class RuntimeMethod:
    """
    运行中的方法
    """

    belong_class: RuntimeClass = dataclasses.field(kw_only=True)  # 所属类
    method_name: str = dataclasses.field(kw_only=True)  # 方法名

    @staticmethod
    def create(package_name: str, class_name: str, method_name: str) -> "RuntimeMethod":
        """根据 package_name、class_name 和 method_name 构造 RuntimeMethod 对象"""
        return RuntimeMethod(
            belong_class=RuntimeClass.create(
                package_name=package_name,
                public_class_name=class_name,
                class_name=class_name,
                type_arguments=None
            ),
            method_name=method_name
        )

    @staticmethod
    def create_by_absolute_name(class_absolute_name: str, method_name: str) -> "RuntimeMethod":
        """根据 class_absolute_name 和 method_name 构造 RuntimeMethod 对象"""
        return RuntimeMethod(
            belong_class=RuntimeClass.create_by_public_class_absolute_name(class_absolute_name),
            method_name=method_name
        )

    @property
    def absolute_name(self) -> str:
        if self.belong_class is None:
            return self.method_name
        return f"{self.belong_class.absolute_name}.{self.method_name}"

    def __repr__(self) -> str:
        return (f"<RuntimeMethod "
                f"class={self.belong_class}, "
                f"method={self.method_name}>")

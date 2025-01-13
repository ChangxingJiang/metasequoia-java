"""
运行中的方法
"""

import dataclasses

from metasequoia_java.project.elements.runtime_class import RuntimeClass

__all__ = [
    "RuntimeMethod"
]


@dataclasses.dataclass(slots=True)
class RuntimeMethod:
    """
    运行中的方法
    """

    belong_class: RuntimeClass = dataclasses.field(kw_only=True)  # 所属类
    method_name: str = dataclasses.field(kw_only=True)  # 方法名

    @property
    def absolute_name(self) -> str:
        if self.belong_class is None:
            return self.method_name
        return f"{self.belong_class.absolute_name}.{self.method_name}"

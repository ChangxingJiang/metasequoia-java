"""
运行中的类变量
"""

import dataclasses

from metasequoia_java.project.elements.runtime_class import RuntimeClass

__all__ = [
    "RuntimeVariable"
]


@dataclasses.dataclass(slots=True)
class RuntimeVariable:
    """
    运行中的类变量
    """

    belong_class: RuntimeClass = dataclasses.field(kw_only=True)  # 所属类
    variable_name: str = dataclasses.field(kw_only=True)  # 变量名

    @property
    def absolute_name(self) -> str:
        return f"{self.belong_class.absolute_name}.{self.variable_name}"

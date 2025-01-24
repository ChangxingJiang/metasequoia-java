"""
运行中的类变量
"""

import dataclasses

from metasequoia_java.sa.elements.runtime_class import RuntimeClass

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

    def __repr__(self) -> str:
        if self.belong_class is None:
            return f"<RuntimeVariable package=None, class=None, variable={self.variable_name}>"
        return (f"<RuntimeVariable "
                f"package={self.belong_class.package_name}, "
                f"class={self.belong_class.class_name}, "
                f"variable={self.variable_name}>")

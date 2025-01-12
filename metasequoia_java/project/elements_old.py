"""
分析元素类
"""

import dataclasses
from typing import List, Optional

__all__ = [
    "RuntimeClass",
    "RuntimeMethod",
]


@dataclasses.dataclass(slots=True)
class RuntimeClass:
    """运行中的类定义（类型）"""

    package_name: str = dataclasses.field(kw_only=True)  # 包名
    class_name: str = dataclasses.field(kw_only=True)  # 类名
    type_arguments: Optional[List["RuntimeClass"]] = dataclasses.field(kw_only=True)  # 泛型类的实参，如果未知则为 None


@dataclasses.dataclass(slots=True)
class RuntimeMethod:
    """运行中的方法"""

    belong_class: RuntimeClass = dataclasses.field(kw_only=True)  # 所属类
    method_name: str = dataclasses.field(kw_only=True)  # 方法名

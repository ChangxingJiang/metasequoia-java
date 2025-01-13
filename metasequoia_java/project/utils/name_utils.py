"""
名称处理工具函数
"""

from typing import Tuple, Optional

__all__ = [
    "split_last_name_from_absolute_name"
]


def split_last_name_from_absolute_name(absolute_name: str) -> Tuple[Optional[str], str]:
    """获取 absolute_name（绝对名称）中拆分最后一个名称

    例如：
    1. 拆分 package_name 和 class_name
    2. 拆分 class_name 和 method_name
    """
    if "." in absolute_name:
        return absolute_name[:absolute_name.rindex(".")], absolute_name[absolute_name.rindex(".") + 1:]
    else:
        return None, absolute_name

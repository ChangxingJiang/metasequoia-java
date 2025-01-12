"""
名称处理工具函数
"""

from typing import Tuple

__all__ = [
    "get_package_and_class_name_by_absolute_name"
]


def get_package_and_class_name_by_absolute_name(absolute_name: str) -> Tuple[str, str]:
    """获取 absolute_name（绝对名称）中获取 package_name 和 class_name"""
    if "." in absolute_name:
        return absolute_name[:absolute_name.rindex(".")], absolute_name[absolute_name.rindex(".") + 1:]
    else:
        return "", absolute_name

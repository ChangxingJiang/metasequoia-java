"""
名称处理工具函数
"""

from typing import Optional, Tuple

__all__ = [
    "split_last_name_from_absolute_name",
    "get_first_name_from_absolute_name",
]


def split_last_name_from_absolute_name(absolute_name: str) -> Tuple[Optional[str], str]:
    """获取 absolute_name（完整引用名称）中拆分最后一个名称

    例如：
    1. 拆分 package_name 和 class_name
    2. 拆分 class_name 和 method_name

    Parameters
    ----------
    absolute_name : str
        完整引用名称（xxx.xxx.xxx）

    Returns
    -------
    str
        最后一个 "." 之前的部分，如果没有 "." 则为 None
    str
        最后一个 "." 之后不分
    """
    if "." not in absolute_name:
        return None, absolute_name
    return absolute_name[:absolute_name.rindex(".")], absolute_name[absolute_name.rindex(".") + 1:]


def get_first_name_from_absolute_name(absolute_name: str) -> str:
    """获取 absolute_name（完整引用名称）中的第一个名称

    Parameters
    ----------
    absolute_name : str
        完整引用名称（xxx.xxx.xxx）

    Returns
    -------
    str
        第一个名称
    """
    if "." not in absolute_name:
        return absolute_name
    return absolute_name[:absolute_name.index(".")]

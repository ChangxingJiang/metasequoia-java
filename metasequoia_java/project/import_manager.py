"""
引用映射管理器
"""

from typing import Any, Dict, Optional

__all__ = [
    "ImportManager"
]


class ImportManager:
    """引用映射管理器"""

    def __init__(self, import_hash: Dict[str, str]):
        self._import_hash = import_hash

    def set_import(self, name: str, full_name: str) -> None:
        self._import_hash[name] = full_name

    def get_absolute_name(self, name: str, default: Any = None) -> Optional[str]:
        """获取完整名称"""
        return self._import_hash.get(name, default)

    def get_package_name(self, name: str, default: Any = None) -> Optional[str]:
        """获取所属 package 名称"""
        if name not in self._import_hash:
            return default

        absolute_name = self._import_hash[name]
        return absolute_name.replace(f".{name}", "")

    def __repr__(self):
        text = ", ".join(f"{key}={value}" for key, value in self._import_hash.items())
        return f"<ImportAnalyzer {text}>"

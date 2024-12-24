import abc
import dataclasses
from typing import Optional

from metasequoia_java.grammar.constants import IntegerStyle
from metasequoia_java.grammar.constants import StringStyle
from metasequoia_java.grammar.utils import change_int_to_string

__all__ = [
    "Tree",

    # ------------------------------ Chapter 3 : Lexical Structure ------------------------------
    "Literal",
    "IntLiteral",  # 十进制整型字面值
    "LongLiteral",  # 十进制长整型字面值
    "FloatLiteral",  # 十进制单精度浮点数字面值
    "DoubleLiteral",  # 十进制双精度浮点数字面值
    "CharacterLiteral",  # 字符字面值
    "StringLiteral",  # 字符串字面值
    "TrueLiteral",  # 布尔值真值字面值
    "FalseLiteral",  # 布尔值假值字面值
    "NullLiteral",  # 空值字面值
]


@dataclasses.dataclass(slots=True)
class Tree(abc.ABC):
    """抽象语法树节点的抽象基类

    JDK 源码接口：https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/Tree.java
    """

    source: Optional[str] = dataclasses.field(kw_only=True)  # 原始代码

    @property
    def is_literal(self) -> bool:
        return False

    @abc.abstractmethod
    def generate(self) -> str:
        """生成当前节点元素的标准格式代码"""


@dataclasses.dataclass(slots=True)
class Literal(Tree, abc.ABC):

    @property
    def is_literal(self) -> bool:
        return True


@dataclasses.dataclass(slots=True)
class IntLiteral(Literal):
    """整型字面值（包括十进制、八进制、十六进制）"""

    style: IntegerStyle = dataclasses.field(kw_only=True)
    value: int = dataclasses.field(kw_only=True)

    def generate(self) -> str:
        return change_int_to_string(self.value, self.style)


@dataclasses.dataclass(slots=True)
class LongLiteral(Literal):
    """十进制长整型字面值"""

    style: IntegerStyle = dataclasses.field(kw_only=True)
    value: int = dataclasses.field(kw_only=True)

    def generate(self) -> str:
        return f"{self.value}L"


@dataclasses.dataclass(slots=True)
class FloatLiteral(Literal):
    """十进制单精度浮点数字面值"""

    value: float = dataclasses.field(kw_only=True)

    def generate(self) -> str:
        return f"{self.value}f"


@dataclasses.dataclass(slots=True)
class DoubleLiteral(Literal):
    """十进制双精度浮点数字面值"""

    value: float = dataclasses.field(kw_only=True)

    def generate(self) -> str:
        return f"{self.value}"


@dataclasses.dataclass(slots=True)
class TrueLiteral(Literal):
    """布尔值真值字面值"""

    def generate(self) -> str:
        return f"true"


@dataclasses.dataclass(slots=True)
class FalseLiteral(Literal):
    """布尔值假值字面值"""

    def generate(self) -> str:
        return f"false"


@dataclasses.dataclass(slots=True)
class CharacterLiteral(Literal):
    """字符字面值"""

    value: str = dataclasses.field(kw_only=True)  # 不包含单引号的字符串

    def generate(self) -> str:
        return f"'{self.value}'"


@dataclasses.dataclass(slots=True)
class StringLiteral(Literal):
    """字符串字面值"""

    style: StringStyle = dataclasses.field(kw_only=True)  # 字面值样式
    value: str = dataclasses.field(kw_only=True)  # 不包含双引号的字符串内容

    def generate(self) -> str:
        if self.style == StringStyle.STRING:
            return f"\"{repr(self.value)}\""
        return f"\"\"\"\n{repr(self.value)}\"\"\""


@dataclasses.dataclass(slots=True)
class NullLiteral(Literal):
    """空值字面值"""

    def generate(self) -> str:
        return f"null"

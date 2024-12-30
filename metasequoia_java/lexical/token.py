"""
终结符类
"""

import enum
from typing import List, Optional

from metasequoia_java.lexical.token_kind import TokenKind

__all__ = [
    "AffiliationStyle",
    "Affiliation",
    "Token",
    "IntToken",
    "FloatToken",
    "CharToken",
    "StringToken"
]


class AffiliationStyle(enum.IntEnum):
    """附属元素的类型"""

    SPACE = enum.auto()  # 空格
    LINEBREAK = enum.auto()  # 换行符
    COMMENT_LINE = enum.auto()  # 以 // 开头的注释
    COMMENT_BLOCK = enum.auto()  # 以 /* 开头的注释
    JAVADOC_LINE = enum.auto()  # 以 //* 开头的注释
    JAVADOC_BLOCK = enum.auto()  # 以 /** 开头的注释


class Affiliation:
    """附属元素：包括空格、换行符和注释

    之所以设计附属元素的概念，是为了给构造的抽象语法树提供重新转换为 Java 代码的功能，且在恢复时能够还原原始代码的空格、换行符和注释。从而使构造的抽象
    语法树能够被应用到格式化代码、添加注释的场景。
    """

    __slots__ = ("_style", "_pos", "_end_pos", "_text")

    def __init__(self, style: AffiliationStyle, pos: int, end_pos: int, text: str):
        self._style = style
        self._pos = pos
        self._end_pos = end_pos
        self._text = text

    @property
    def style(self) -> AffiliationStyle:
        return self._style

    @property
    def pos(self) -> int:
        return self._pos

    @property
    def end_pos(self) -> int:
        return self._end_pos

    @property
    def text(self) -> str:
        return self._text


class Token:
    """语法元素"""

    __slots__ = ("_kind", "_pos", "_end_pos", "_affiliations", "_source")

    def __init__(self, kind: TokenKind, pos: int, end_pos: int, affiliations: List[Affiliation], source: Optional[str]):
        """

        Parameters
        ----------
        kind : TokenKind
            语法元素类型
        pos : int
            语法元素开始位置（包含）
        end_pos : int
            语法元素结束位置（不包含）
        affiliations : List[Affiliation]
            语法元素之后的附属元素
        source : Optional[str]
            语法元素的源代码；当前仅当当前语法元素为结束符时源代码为 None
        """
        self._kind = kind
        self._pos = pos
        self._end_pos = end_pos
        self._affiliations = affiliations
        self._source = source

    @property
    def kind(self) -> TokenKind:
        return self._kind

    @property
    def pos(self) -> int:
        return self._pos

    @property
    def end_pos(self) -> int:
        return self._end_pos

    @property
    def affiliations(self) -> List[Affiliation]:
        return self._affiliations

    @property
    def source(self) -> str:
        return self._source

    @property
    def is_end(self) -> bool:
        return self.kind == TokenKind.EOF

    @property
    def name(self) -> str:
        return self.source

    def int_value(self) -> int:
        raise TypeError(f"{self.__class__.__name__}.int_value is undefined!")

    def float_value(self) -> int:
        raise TypeError(f"{self.__class__.__name__}.float_value is undefined!")

    def char_value(self) -> str:
        raise TypeError(f"{self.__class__.__name__}.char_value is undefined!")

    def string_value(self) -> str:
        raise TypeError(f"{self.__class__.__name__}.string_value is undefined!")

    def __repr__(self) -> str:
        return f"{self.kind.name}({self.source}){self.affiliations}"


class IntToken(Token):
    """整数类型的 Token"""

    __slots__ = ("_kind", "_pos", "_end_pos", "_affiliations", "_source", "_value")

    def __init__(self, kind: TokenKind, pos: int, end_pos: int, affiliations: List[Affiliation], source: Optional[str],
                 value: int):
        super().__init__(kind, pos, end_pos, affiliations, source)
        self._value = value

    def int_value(self) -> int:
        return self._value


class FloatToken(Token):
    """浮点数类型的 Token"""

    __slots__ = ("_kind", "_pos", "_end_pos", "_affiliations", "_source", "_value")

    def __init__(self, kind: TokenKind, pos: int, end_pos: int, affiliations: List[Affiliation], source: Optional[str],
                 value: float):
        super().__init__(kind, pos, end_pos, affiliations, source)
        self._value = value

    def float_value(self) -> float:
        return self._value


class CharToken(Token):
    """字符类型的 Token"""

    __slots__ = ("_kind", "_pos", "_end_pos", "_affiliations", "_source", "_value")

    def __init__(self, kind: TokenKind, pos: int, end_pos: int, affiliations: List[Affiliation], source: Optional[str],
                 value: str):
        super().__init__(kind, pos, end_pos, affiliations, source)
        self._value = value

    def char_value(self) -> str:
        return self._value


class StringToken(Token):
    """字符串类型的 Token"""

    __slots__ = ("_kind", "_pos", "_end_pos", "_affiliations", "_source", "_value")

    def __init__(self, kind: TokenKind, pos: int, end_pos: int, affiliations: List[Affiliation], source: Optional[str],
                 value: str):
        super().__init__(kind, pos, end_pos, affiliations, source)
        self._value = value

    def string_value(self) -> str:
        return self._value

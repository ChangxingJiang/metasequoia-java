import enum

from metasequoia_java.lexical.token_kind import TokenKind

__all__ = [
    "IntegerStyle",
    "StringStyle",
    "INT_LITERAL_STYLE_HASH",
    "LONG_LITERAL_STYLE_HASH",
    "CaseKind",
    "ModuleKind",
    "LambdaBodyKind",
    "ReferenceMode",
]


class IntegerStyle(enum.Enum):
    """整型或长整型的字面值样式"""

    OCT = enum.auto()  # 八进制
    DEC = enum.auto()  # 十进制
    HEX = enum.auto()  # 十六进制


class StringStyle(enum.Enum):
    """字符串字面值的样式"""

    STRING = enum.auto()  # 普通字符串
    TEXT_BLOCK = enum.auto()  # 字符块


# 整型终结符到整型进制样式的映射关系
INT_LITERAL_STYLE_HASH = {
    TokenKind.INT_OCT_LITERAL: IntegerStyle.OCT,
    TokenKind.INT_DEC_LITERAL: IntegerStyle.DEC,
    TokenKind.INT_HEX_LITERAL: IntegerStyle.HEX
}

# 长整型终结符到整型进制样式的映射关系
LONG_LITERAL_STYLE_HASH = {
    TokenKind.LONG_OCT_LITERAL: IntegerStyle.OCT,
    TokenKind.LONG_DEC_LITERAL: IntegerStyle.DEC,
    TokenKind.LONG_HEX_LITERAL: IntegerStyle.HEX
}


class CaseKind(enum.Enum):
    """Case 语句类型"""

    STATEMENT = enum.auto()  # <expression>: <statements>
    RULE = enum.auto()  # <expression> -> <expression>


class ModuleKind(enum.Enum):
    """模块类型"""

    OPEN = enum.auto()
    STRONG = enum.auto()


class LambdaBodyKind(enum.Enum):
    """lambda 表达式类型"""

    EXPRESSION = enum.auto()
    STATEMENT = enum.auto()


class ReferenceMode(enum.Enum):
    """引用模式"""

    INVOKE = enum.auto()
    NEW = enum.auto()

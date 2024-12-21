"""
词法解析器的有限状态自动机的状态枚举类
"""

import enum

__all__ = [
    "LexicalState"
]


class LexicalState(enum.IntEnum):
    """词法解析器的有限状态自动机的状态枚举类"""

    INIT = enum.auto()  # 当前没有正在解析的词语
    END = enum.auto()  # 已经解析到结束符
    IDENT = enum.auto()  # 当前词语为不是特殊词语

    # -------------------- 数值字面值 --------------------
    ZERO = enum.auto()  # 0（可能为八进制的前缀）
    ZERO_X = enum.auto()  # 0[xX]（十六进制的前缀）
    NUMBER = enum.auto()  # [1-9][0-9]+（十进制数）
    OCT_NUMBER = enum.auto()  # 0[0-7]+（八进制数）
    HEX_NUMBER = enum.auto()  # 0[xX][0-9a-fA-F]+（十六进制数）
    NUMBER_LONG = enum.auto()  # [1-9][0-9]*L（长整型字面值）
    NUMBER_DECIMAL = enum.auto()  # [0-9]+\.[0-9]*（小数）
    NUMBER_DECIMAL_E = enum.auto()  # [0-9]+(\.[0-9]+)?[eE]（科学记数法的前缀）
    NUMBER_SCIENTIFIC = enum.auto()  # [0-9]+(\.[0-9]+)?[eE]-?[0-9]*（科学记数法）
    NUMBER_FLOAT = enum.auto()  # [0-9]+(\.[0-9]+)?([eE]-?[0-9]*)?[fF]（单精度浮点数字面值）
    NUMBER_DOUBLE = enum.auto()  # [0-9]+(\.[0-9]+)?([eE]-?[0-9]*)?[dD]（双精度浮点数字典值）

    # -------------------- 字符字面值 --------------------
    IN_SINGLE_QUOTE = enum.auto()  # 在单引号字符串中
    IN_SINGLE_QUOTE_ESCAPE = enum.auto()  # 在单引号字符串中的转义符之后

    # -------------------- 字符串字面值 --------------------
    IN_DOUBLE_QUOTE = enum.auto()  # 在双引号字符串中
    IN_DOUBLE_QUOTE_ESCAPE = enum.auto()  # 在双引号字符串中的转义符之后

    # -------------------- 多字符运算符 --------------------
    CHAR_EQUAL = enum.auto()  # =
    CHAR_COL = enum.auto()  # =
    CHAR_EXCLAMATION = enum.auto()  # !
    CHAR_LESS = enum.auto()  # <
    CHAR_LESS_LESS = enum.auto()  # <<
    CHAR_MORE = enum.auto()  # >
    CHAR_MORE_MORE = enum.auto()  # >>
    CHAR_MORE_MORE_MORE = enum.auto()  # >>>
    CHAR_AND = enum.auto()  # &
    CHAR_OR = enum.auto()  # |
    CHAR_ADD = enum.auto()  # +
    CHAR_SUB = enum.auto()  # -
    CHAR_MULT = enum.auto()  # *
    CHAR_DIV = enum.auto()  # /
    CHAR_MOD = enum.auto()  # %

    # -------------------- 注释 --------------------
    IN_LINE_COMMENT = enum.auto()  # 在单行注释中
    IN_MULTI_COMMENT = enum.auto()  # 在多行注释中
    IN_MULTI_COMMENT_STAR = enum.auto()  # 在多行注释中的 * 之后

    # -------------------- 特殊场景 --------------------
    POINT = enum.auto()  # .（后面是否为数字为两种情况）
    DOT = enum.auto()  # ..

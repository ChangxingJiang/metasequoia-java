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
    DEC = enum.auto()  # [1-9][0-9]+（十进制数）
    DEC_L = enum.auto()  # [1-9][0-9]*L（长整型字面值）
    OCT = enum.auto()  # 0[0-7]+（八进制数）
    OCT_L = enum.auto()  # 0[0-7]+（八进制数）
    HEX = enum.auto()  # 0[xX][0-9a-fA-F]+（十六进制数）
    HEX_L = enum.auto()  # 0[xX][0-9a-fA-F]+（十六进制数）
    DEC_DOT_NUM = enum.auto()  # [0-9]+\.[0-9]*（小数）
    DEC_DOT_NUM_E = enum.auto()  # [0-9]+(\.[0-9]+)?[eE]（科学记数法的前缀）
    DEC_DOT_NUM_E_NUM = enum.auto()  # [0-9]+(\.[0-9]+)?[eE]-?[0-9]*（科学记数法）
    DEC_DOT_NUM_E_NUM_F = enum.auto()  # [0-9]+(\.[0-9]+)?([eE]-?[0-9]*)?[fF]（单精度浮点数字面值）
    DEC_DOT_NUM_E_NUM_D = enum.auto()  # [0-9]+(\.[0-9]+)?([eE]-?[0-9]*)?[dD]（双精度浮点数字典值）

    # -------------------- 字符字面值 --------------------
    LIT_CHAR = enum.auto()  # 在单引号字符串中
    LIT_CHAR_ESCAPE = enum.auto()  # 在单引号字符串中的转义符之后

    # -------------------- 字符串字面值 --------------------
    DQ = enum.auto()  # "
    DQ_DQ = enum.auto()  # ""
    LIT_STRING = enum.auto()  # 在双引号字符串中
    LIT_STRING_ESCAPE = enum.auto()  # 在双引号字符串中的转义符之后
    LIT_BLOCK = enum.auto()  # 在 TextBlock 中
    LIT_BLOCK_ESCAPE = enum.auto()  # 在 TextBlock 中的转义符之后
    LIT_BLOCK_DQ = enum.auto()  # 在 TextBlock 中的 " 之后
    LIT_BLOCK_DQ_DQ = enum.auto()  # 在 TextBlock 中的 "" 之后

    # -------------------- 多字符运算符 --------------------
    EQ = enum.auto()  # =
    BANG = enum.auto()  # !
    LT = enum.auto()  # <
    LT_LT = enum.auto()  # <<
    GT = enum.auto()  # >
    GT_GT = enum.auto()  # >>
    GT_GT_GT = enum.auto()  # >>>
    AMP = enum.auto()  # &
    BAR = enum.auto()  # |
    PLUS = enum.auto()  # +
    SUB = enum.auto()  # -
    STAR = enum.auto()  # *
    SLASH = enum.auto()  # /
    PERCENT = enum.auto()  # %
    COLON = enum.auto()  # :
    CARET = enum.auto()  # ^

    # -------------------- 注释 --------------------
    IN_LINE_COMMENT = enum.auto()  # 在单行注释中
    IN_MULTI_COMMENT = enum.auto()  # 在多行注释中
    IN_MULTI_COMMENT_STAR = enum.auto()  # 在多行注释中的 * 之后

    # -------------------- 特殊场景 --------------------
    DOT = enum.auto()  # .（后面是否为数字为两种情况）
    DOT_DOT = enum.auto()  # ..

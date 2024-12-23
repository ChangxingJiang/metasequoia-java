"""
Java 终结符类型的枚举类
"""

import enum


class TokenKind(enum.IntEnum):
    """Java 终结符类型的枚举类

    在终结符类型名称设计时，与 JDK 源码名称保持一致，但为了适应 Python 语法规范，在不同单词之间增加了下划线

    JDK 源码路径：src/jdk.compiler/share/classes/com/sun/tools/javac/parser/Tokens.java
    JDK 源码地址：https://github.com/openjdk/jdk/blob/249f141211c94afcce70d9d536d84e108e07b4e5/src/jdk.compiler/share/classes/com/sun/tools/javac/parser/Tokens.java
    """

    # ------------------------------ 特殊终结符 ------------------------------
    EOF = enum.auto()  # 结束符
    ERROR = enum.auto()  # 错误

    # ------------------------------ 标识符 ------------------------------
    IDENTIFIER = enum.auto()  # 标识符

    # ------------------------------ 关键字 ------------------------------
    ABSTRACT = enum.auto()  # 关键字：abstract
    ASSERT = enum.auto()  # 关键字：assert
    BOOLEAN = enum.auto()  # 关键字：boolean
    BREAK = enum.auto()  # 关键字：break
    BYTE = enum.auto()  # 关键字：byte
    CASE = enum.auto()  # 关键字：case
    CATCH = enum.auto()  # 关键字：catch
    CHAR = enum.auto()  # 关键字：char
    CLASS = enum.auto()  # 关键字：class
    CONST = enum.auto()  # 关键字：const
    CONTINUE = enum.auto()  # 关键字：continue
    DEFAULT = enum.auto()  # 关键字：default
    DO = enum.auto()  # 关键字：do
    DOUBLE = enum.auto()  # 关键字：double
    ELSE = enum.auto()  # 关键字：else
    ENUM = enum.auto()  # 关键字：enum
    EXTENDS = enum.auto()  # 关键字：extends
    FINAL = enum.auto()  # 关键字：final
    FINALLY = enum.auto()  # 关键字：finally
    FLOAT = enum.auto()  # 关键字：float
    FOR = enum.auto()  # 关键字：for
    GOTO = enum.auto()  # 关键字：goto
    IF = enum.auto()  # 关键字：if
    IMPLEMENTS = enum.auto()  # 关键字：implements
    IMPORT = enum.auto()  # 关键字：import
    INSTANCEOF = enum.auto()  # 关键字：instanceof
    INT = enum.auto()  # 关键字：int
    INTERFACE = enum.auto()  # 关键字：interface
    LONG = enum.auto()  # 关键字：long
    NATIVE = enum.auto()  # 关键字：native
    NEW = enum.auto()  # 关键字：new
    PACKAGE = enum.auto()  # 关键字：package
    PRIVATE = enum.auto()  # 关键字：private
    PROTECTED = enum.auto()  # 关键字：protected
    PUBLIC = enum.auto()  # 关键字：public
    RETURN = enum.auto()  # 关键字：return
    SHORT = enum.auto()  # 关键字：short
    STATIC = enum.auto()  # 关键字：static
    STRICTFP = enum.auto()  # 关键字：strictfp
    SUPER = enum.auto()  # 关键字：super
    SWITCH = enum.auto()  # 关键字：switch
    SYNCHRONIZED = enum.auto()  # 关键字：synchronized
    THIS = enum.auto()  # 关键字：this
    THROW = enum.auto()  # 关键字：throw
    THROWS = enum.auto()  # 关键字：throws
    TRANSIENT = enum.auto()  # 关键字：transient
    TRY = enum.auto()  # 关键字：try
    VOID = enum.auto()  # 关键字：void
    VOLATILE = enum.auto()  # 关键字：volatile
    WHILE = enum.auto()  # 关键字：while

    # ------------------------------ 字面值 ------------------------------
    INT_LITERAL = enum.auto()  # 整型字面值
    LONG_LITERAL = enum.auto()  # 长整型字面值
    FLOAT_LITERAL = enum.auto()  # 单精度浮点数字面值
    DOUBLE_LITERAL = enum.auto()  # 双精度浮点数字面值
    CHAR_LITERAL = enum.auto()  # 字符字面值
    STRING_LITERAL = enum.auto()  # 字符串字面值
    STRING_FRAGMENT = enum.auto()
    TRUE = enum.auto()  # 布尔字面值：true
    FALSE = enum.auto()  # 布尔字面值：false
    NULL = enum.auto()  # 空值字面值：null

    # ------------------------------ 下划线关键字 ------------------------------
    UNDERSCORE = enum.auto()  # 下划线：_

    # ------------------------------ 运算符 ------------------------------
    ARROW = enum.auto()  # ->
    COLCOL = enum.auto()  # ::
    LPAREN = enum.auto()  # (
    RPAREN = enum.auto()  # )
    LBRACE = enum.auto()  # {
    RBRACE = enum.auto()  # }
    LBRACKET = enum.auto()  # [
    RBRACKET = enum.auto()  # ]
    SEMI = enum.auto()  # ;
    COMMA = enum.auto()  # ,
    DOT = enum.auto()  # .
    ELLIPSIS = enum.auto()  # ...
    EQ = enum.auto()  # =
    GT = enum.auto()  # >
    LT = enum.auto()  # <
    BANG = enum.auto()  # !
    TILDE = enum.auto()  # ~
    QUES = enum.auto()  # ?
    COLON = enum.auto()  # :
    EQ_EQ = enum.auto()  # ==
    LT_EQ = enum.auto()  # <=
    GT_EQ = enum.auto()  # >=
    BANG_EQ = enum.auto()  # !=
    AMP_AMP = enum.auto()  # &&
    BAR_BAR = enum.auto()  # ||
    PLUS_PLUS = enum.auto()  # ++
    SUB_SUB = enum.auto()  # --
    PLUS = enum.auto()  # +
    SUB = enum.auto()  # -
    STAR = enum.auto()  # *
    SLASH = enum.auto()  # /
    AMP = enum.auto()  # &
    BAR = enum.auto()  # |
    CARET = enum.auto()  # ^
    PERCENT = enum.auto()  # %
    LT_LT = enum.auto()  # <<
    GT_GT = enum.auto()  # >>
    GT_GT_GT = enum.auto()  # >>>
    PLUS_EQ = enum.auto()  # +=
    SUB_EQ = enum.auto()  # -=
    STAR_EQ = enum.auto()  # *=
    SLASH_EQ = enum.auto()  # /=
    AMP_EQ = enum.auto()  # &=
    BAR_EQ = enum.auto()  # |=
    CARET_EQ = enum.auto()  # ^=
    PERCENT_EQ = enum.auto()  # %=
    LT_LT_EQ = enum.auto()  # <<=
    GT_GT_EQ = enum.auto()  # >>=
    GT_GT_GT_EQ = enum.auto()  # >>>=
    MONKEYS_AT = enum.auto()  # @

    # ------------------------------ 其他元素 ------------------------------
    CUSTOM = enum.auto()

    # # -------------------- 基础元素 --------------------
    # BRACE_OPEN = enum.auto()  # 开大括号（{）
    # BRACE_CLOSE = enum.auto()  # 闭大括号（}）
    # SQUARE_OPEN = enum.auto()  # 开中括号（[）
    # SQUARE_CLOSE = enum.auto()  # 闭中括号（]）
    # CURVE_OPEN = enum.auto()  # 开小括号（(）
    # CURVE_CLOSE = enum.auto()  # 闭小括号（)）
    # ANGLE_OPEN = enum.auto()  # 开尖括号（<）
    # ANGLE_CLOSE = enum.auto()  # 闭尖括号（>）
    # POINT = enum.auto()  # 点号（.）
    # SEMICOLON = enum.auto()  # 分号（;）
    # AT = enum.auto()  # 电子邮件符号（@）
    #
    # # -------------------- 字面值 --------------------
    # LIT_OCT = enum.auto()  # 八进制整数字面值（012）
    # LIT_HEX = enum.auto()  # 十六进制整数字面值（0x0A）
    #
    # # -------------------- 运算符 --------------------
    # OP_CAL_ADD = enum.auto()  # 算术运算符：加法（+）
    # OP_CAL_SUB = enum.auto()  # 算术运算符：减法（-）
    # OP_CAL_MULT = enum.auto()  # 算术运算符：乘法（*）
    # OP_CAL_DIV = enum.auto()  # 算术运算符：除法（/）
    # OP_CAL_MOD = enum.auto()  # 算术运算符：取模（%）
    # OP_EQ = enum.auto()  # 比较运算符：等于（==）
    # OP_NEQ = enum.auto()  # 比较运算符：不等于（!=）
    # OP_LTE = enum.auto()  # 比较运算符：小于等于（<=）
    # OP_GTE = enum.auto()  # 比较运算符：大于等于（>=）
    # OP_LOG_AND = enum.auto()  # 逻辑运算符：逻辑与（&&）
    # OP_LOG_OR = enum.auto()  # 逻辑运算符：逻辑或（||）
    # OP_LOG_NOT = enum.auto()  # 逻辑运算符：逻辑非（!）
    # OP_ASS_EQ = enum.auto()  # 赋值运算符：赋值（=）
    # OP_ASS_ADD = enum.auto()  # 赋值运算符：加并赋值（+=）
    # OP_ASS_SUB = enum.auto()  # 赋值运算符：减并赋值（-=）
    # OP_ASS_MULT = enum.auto()  # 赋值运算符：乘并赋值（*=）
    # OP_ASS_DIV = enum.auto()  # 赋值运算符：除并赋值（/=）
    # OP_ASS_MOD = enum.auto()  # 赋值运算符：取模并赋值（%=）
    # OP_INC = enum.auto()  # 自增运算符（++）
    # OP_DEC = enum.auto()  # 自减运算符（--）
    # OP_BIT_AND = enum.auto()  # 位运算符：按位与（&）
    # OP_BIT_OR = enum.auto()  # 位运算符：按位或（|）
    # OP_BIT_XOR = enum.auto()  # 位运算符：按位异或（^）
    # OP_BIT_LSHIFT = enum.auto()  # 位运算符：左移位（<<）
    # OP_BIT_RSHIFT = enum.auto()  # 位运算符：带符号右移位（>>）
    # OP_BIT_UNSIGNED_RSHIFT = enum.auto()  # 位运算符：无符号右移位（>>>）

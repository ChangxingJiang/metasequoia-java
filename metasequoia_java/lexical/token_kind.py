"""
Java 终结符类型的枚举类
"""

import enum


class TokenKind(enum.IntFlag):
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

    # ------------------------------ 下划线关键字 ------------------------------
    UNDERSCORE = enum.auto()  # 下划线：_

    # ------------------------------ 字面值 ------------------------------
    INT_OCT_LITERAL = enum.auto()  # 八进制整型字面值
    INT_DEC_LITERAL = enum.auto()  # 十进制整型字面值
    INT_HEX_LITERAL = enum.auto()  # 十六进制整型字面值
    LONG_OCT_LITERAL = enum.auto()  # 八进制长整型字面值
    LONG_DEC_LITERAL = enum.auto()  # 十进制长整型字面值
    LONG_HEX_LITERAL = enum.auto()  # 十六进制长整型字面值
    FLOAT_LITERAL = enum.auto()  # 单精度浮点数字面值
    DOUBLE_LITERAL = enum.auto()  # 双精度浮点数字面值
    CHAR_LITERAL = enum.auto()  # 字符字面值
    STRING_LITERAL = enum.auto()  # 字符串字面值
    TEXT_BLOCK = enum.auto()  # 字符块字面值（JDK 15+）
    STRING_FRAGMENT = enum.auto()
    TRUE = enum.auto()  # 布尔字面值：true
    FALSE = enum.auto()  # 布尔字面值：false
    NULL = enum.auto()  # 空值字面值：null

    # ------------------------------ 运算符 ------------------------------
    ARROW = enum.auto()  # ->
    COL_COL = enum.auto()  # ::
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

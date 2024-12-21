"""
关键字、布尔字面值、空值字面值名称到终结符类型的映射
"""

from metasequoia_java.terminal import TokenKind

__all__ = [
    "KEYWORD_HASH"
]

# 关键字、布尔字面值、空值字面值名称到终结符类型的映射
KEYWORD_HASH = {
    "abstract": TokenKind.ABSTRACT,
    "assert": TokenKind.ASSERT,
    "boolean": TokenKind.BOOLEAN,
    "break": TokenKind.BREAK,
    "byte": TokenKind.BYTE,
    "case": TokenKind.CASE,
    "catch": TokenKind.CATCH,
    "char": TokenKind.CHAR,
    "class": TokenKind.CLASS,
    "continue": TokenKind.CONTINUE,
    "default": TokenKind.DEFAULT,
    "do": TokenKind.DO,
    "double": TokenKind.DOUBLE,
    "else": TokenKind.ELSE,
    "enum": TokenKind.ENUM,
    "extends": TokenKind.EXTENDS,
    "final": TokenKind.FINAL,
    "finally": TokenKind.FINALLY,
    "float": TokenKind.FLOAT,
    "for": TokenKind.FOR,
    "if": TokenKind.IF,
    "implements": TokenKind.IMPLEMENTS,
    "import": TokenKind.IMPORT,
    "int": TokenKind.INT,
    "interface": TokenKind.INTERFACE,
    "instanceof": TokenKind.INSTANCEOF,
    "long": TokenKind.LONG,
    "native": TokenKind.NATIVE,
    "new": TokenKind.NEW,
    "package": TokenKind.PACKAGE,
    "private": TokenKind.PRIVATE,
    "protected": TokenKind.PROTECTED,
    "public": TokenKind.PUBLIC,
    "return": TokenKind.RETURN,
    "short": TokenKind.SHORT,
    "static": TokenKind.STATIC,
    "strictfp": TokenKind.STRICTFP,
    "super": TokenKind.SUPER,
    "switch": TokenKind.SWITCH,
    "synchronized": TokenKind.SYNCHRONIZED,
    "this": TokenKind.THIS,
    "throw": TokenKind.THROW,
    "throws": TokenKind.THROWS,
    "transient": TokenKind.TRANSIENT,
    "try": TokenKind.TRY,
    "void": TokenKind.VOID,
    "volatile": TokenKind.VOLATILE,
    "while": TokenKind.WHILE,
    "goto": TokenKind.GOTO,
    "const": TokenKind.CONST,
    "true": TokenKind.TRUE,
    "false": TokenKind.FALSE,
    "null": TokenKind.NULL,
}

"""
语法元素
"""

import enum

__all__ = [
    "Modifier",
    "TypeKind",
]


class Modifier(enum.Enum):
    """修饰符

    https://github.com/openjdk/jdk/blob/master/src/java.compiler/share/classes/javax/lang/model/element/Modifier.java
    Represents a modifier on a program element such as a class, method, or field.
    """

    PUBLIC = "public"
    PROTECTED = "protected"
    PRIVATE = "private"
    ABSTRACT = "abstract"
    DEFAULT = "default"
    STATIC = "static"
    FINAL = "final"
    TRANSIENT = "transient"
    VOLATILE = "volatile"
    SYNCHRONIZED = "synchronized"
    NATIVE = "native"
    STRICTFP = "strictfp"

    SEALED = "sealed"  # 【JDK 17+】
    NON_SEALED = "non-sealed"  # 【JDK 17+】

    # 虚拟修饰符
    DEPRECATED = "deprecated"  # JavaDoc 中包含 @deprecated 标记
    ANNOTATION = "annotation"
    ENUM = "enum"
    INTERFACE = "interface"

    # 其他虚拟修饰符  TODO 考虑将 tags 和修饰符拆分开
    PARAMETER = "parameter"
    RECORD = "record"
    GENERATED_MEMBER = "generated_member"
    VARARGS = "varargs"

    def is_virtual(self) -> bool:
        """是否为虚拟修饰符"""
        return self in {Modifier.DEPRECATED, Modifier.ANNOTATION, Modifier.ENUM, Modifier.INTERFACE, Modifier.PARAMETER,
                        Modifier.RECORD, Modifier.GENERATED_MEMBER, Modifier.VARARGS, Modifier.EMPTY}


class TypeKind(enum.Enum):
    """类型"""

    BOOLEAN = enum.auto()
    BYTE = enum.auto()
    SHORT = enum.auto()
    INT = enum.auto()
    LONG = enum.auto()
    CHAR = enum.auto()
    FLOAT = enum.auto()
    DOUBLE = enum.auto()
    VOID = enum.auto()
    NONE = enum.auto()
    NULL = enum.auto()
    ARRAY = enum.auto()
    DECLARED = enum.auto()
    ERROR = enum.auto()
    TYPE_VAR = enum.auto()  # type variable
    WILDCARD = enum.auto()
    PACKAGE = enum.auto()
    EXECUTABLE = enum.auto()
    OTHER = enum.auto()
    UNION = enum.auto()
    INTERSECTION = enum.auto()
    MODULE = enum.auto()  # 【JDK 9+】

    def is_primitive(self) -> bool:
        """返回是否为原生类型"""
        return self in {TypeKind.BOOLEAN, TypeKind.BYTE, TypeKind.SHORT, TypeKind.INT, TypeKind.LONG, TypeKind.CHAR,
                        TypeKind.FLOAT, TypeKind.DOUBLE}

"""
语法元素
"""

import enum

__all__ = [
    "Modifier"
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
    SEALED = "sealed"  # 【JDK 17+】
    NON_SEALED = "non-sealed"  # 【JDK 17+】
    FINAL = "final"
    TRANSIENT = "transient"
    VOLATILE = "volatile"
    SYNCHRONIZED = "synchronized"
    NATIVE = "native"
    STRICTFP = "strictfp"

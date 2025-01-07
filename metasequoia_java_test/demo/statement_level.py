"""
语句级样例
"""

from metasequoia_java.ast import TreeKind

__all__ = [
    "BLOCK_STATEMENT"
]

BLOCK_STATEMENT = [
    (TreeKind.VARIABLE,
     "Class<?> clazz = null;"),
    (TreeKind.CLASS,
     "class MyClassName { public MyClassName () {} }"),
    (TreeKind.CLASS,
     "enum MyEnumName { A(100), B(90), C(75), D(60); }"),
    (TreeKind.CLASS,
     "interface MyClassName { MyType value = new MyType(); }"),
    (TreeKind.IF,
     "if (name > 3) {} else {} "),
    (TreeKind.YIELD,
     "yield result; "),
    (TreeKind.LABELED_STATEMENT,
     "loop: while (true) {} "),
    (TreeKind.EXPRESSION_STATEMENT,
     "a + 3; "),
    (TreeKind.VARIABLE,
     "byte[] b = new byte[1024];")
]

"""
元素级样例
"""

from metasequoia_java.ast import TreeKind

__all__ = [
    "UNANNOTATED_TYPE"
]

# 无注解类型
UNANNOTATED_TYPE = [
    (TreeKind.PRIMITIVE_TYPE,
     "int"),
    (TreeKind.IDENTIFIER,
     "String"),
    (TreeKind.PARAMETERIZED_TYPE,
     "List<String>"),
    (TreeKind.ANNOTATION_TYPE,
     "@Select MyType"),
    (TreeKind.MEMBER_SELECT,
     "ProcessWindowFunction<Row, Row, Long, TimeWindow>.context"),
    (TreeKind.PARAMETERIZED_TYPE,
     "List<DataStream<?>>")
]

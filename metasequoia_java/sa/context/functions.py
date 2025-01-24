"""
上下文处理器相关函数
"""

from typing import Optional

from metasequoia_java import ast
from metasequoia_java.common import LOGGER
from metasequoia_java.sa.context.base_context import ClassContextBase
from metasequoia_java.sa.context.base_context import MethodContextBase
from metasequoia_java.sa.context.class_context import ClassContext
from metasequoia_java.sa.context.method_context import MethodContext

__all__ = [
    "create_anonymous_class_context",
    "create_anonymous_class_method_context",
]


def create_anonymous_class_context(method_context: MethodContextBase,
                                   class_node: Optional[ast.Class]
                                   ) -> Optional[ClassContextBase]:
    """根据匿名类的抽象语法树节点（Class 类型）构造 ClassContext 对象，如果抽象语法树节点为空（即不是匿名类）则返回 None

    Parameters
    ----------
    method_context : MethodContextBase
        匿名类所在方法的 MethodContext 对象
    class_node : ast.Class
        匿名类的抽象语法树节点

    Returns
    -------
    ClassContextBase
        匿名类的 ClassContext 对象
    """
    if class_node is None:
        return None
    return ClassContext(
        project_context=method_context.project_context,
        file_context=method_context.file_context,
        class_name="Anonymous",
        class_node=class_node,
        outer_class_context=method_context.class_context  # 将当前类作为外部类
    )


def create_anonymous_class_method_context(method_context: MethodContextBase,
                                          class_node: ast.Class,
                                          method_name: str) -> Optional[MethodContextBase]:
    """根据匿名类的抽象语法树节点（Class 类型）和方法名 method_name 构造匿名类中方法的 MethodContext 对象，如果抽象语法树节点为空（即不是匿
    名类）或 method_name 方法不存在则返回 None

    Parameters
    ----------
    method_context : MethodContextBase
        匿名类所在方法的 MethodContext 对象
    class_node : ast.Class
        匿名类的抽象语法树节点
    method_name : str
        方法名

    Returns
    -------
    MethodContextBase
        匿名类中方法的 MethodContext 对象
    """
    anonymous_class_context = create_anonymous_class_context(
        method_context=method_context,
        class_node=class_node
    )
    if anonymous_class_context is None:
        return None
    method_node = class_node.get_method_by_name(method_name)
    if method_node is None:
        LOGGER.warning(f"在 {method_context.get_runtime_method()} 方法的匿名类中找不到 {method_name} 方法")
        return None
    anonymous_method_context = MethodContext(
        project_context=method_context.project_context,
        file_context=method_context.file_context,
        class_context=anonymous_class_context,
        method_name=method_name,
        method_node=method_node
    )
    return anonymous_method_context

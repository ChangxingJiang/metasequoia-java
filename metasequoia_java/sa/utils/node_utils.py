"""
抽象语法树节点相关工具函数
"""

from metasequoia_java import ast

__all__ = [
    "is_long_member_select"
]


def is_long_member_select(ast_node: ast.Tree) -> bool:
    """判断 ast_node 是否为 xxx.xxx.xxx 的格式"""
    if not isinstance(ast_node, ast.MemberSelect):
        return False
    expression_node = ast_node.expression
    if isinstance(expression_node, ast.Identifier):
        return True
    return is_long_member_select(expression_node)

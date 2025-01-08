"""
入口函数
"""

from metasequoia_java import ast
from metasequoia_java.grammar import JavaParser
from metasequoia_java.grammar import ParserMode as Mode
from metasequoia_java.lexical import LexicalFSM

__all__ = [
    "init_parser",
    "parse_compilation_unit",
    "parse_statement",
    "parse_expression",
    "parse_type"
]


def init_parser(code: str, mode: Mode = Mode.NULL) -> JavaParser:
    """初始化解析器"""
    return JavaParser(LexicalFSM(code), mode=mode)


def parse_compilation_unit(code: str) -> ast.CompilationUnitTree:
    """解析根节点"""
    return init_parser(code).parse_compilation_unit()


def parse_statement(code: str) -> ast.Tree:
    """解析语句"""
    return init_parser(code).parse_statement()


def parse_expression(code: str) -> ast.Tree:
    """解析表达式"""
    return init_parser(code).parse_expression()


def parse_type(code: str) -> ast.Tree:
    """解析类型"""
    return init_parser(code, mode=Mode.TYPE).parse_type()


if __name__ == "__main__":
    print(parse_type("ProcessWindowFunction<Row, Row, Long, TimeWindow>.context"))

"""
方法上下文
"""

import dataclasses
from typing import Generator, List, Optional, Tuple, Type

from metasequoia_java import ast
from metasequoia_java.common import LOGGER
from metasequoia_java.project.context.base_context import ClassContextBase
from metasequoia_java.project.context.base_context import FileContextBase
from metasequoia_java.project.context.base_context import MethodContextBase
from metasequoia_java.project.context.base_context import ProjectContextBase
from metasequoia_java.project.elements import RuntimeClass
from metasequoia_java.project.elements import RuntimeMethod
from metasequoia_java.project.elements import RuntimeVariable
from metasequoia_java.project.name_space import NameSpace
from metasequoia_java.project.name_space import SimpleNameSpace
from metasequoia_java.project.utils import get_first_name_from_absolute_name
from metasequoia_java.project.utils import get_last_name_from_absolute_name
from metasequoia_java.project.utils import is_long_member_select
from metasequoia_java.project.utils import split_last_name_from_absolute_name

__all__ = [
    "MethodContext"
]


class MethodContext(MethodContextBase):
    """方法上下文"""

    def __init__(self,
                 project_context: ProjectContextBase,
                 file_context: FileContextBase,
                 class_context: ClassContextBase,
                 method_name: str,
                 method_node: Optional[ast.Method]):
        self._project_context = project_context
        self._file_context = file_context
        self._class_context = class_context
        self._method_name = method_name
        self._method_node = method_node

        # 初始化方法的命名空间
        if method_node is not None:
            self._simple_name_space = (SimpleNameSpace.create_by_method_params(method_node)
                                       + SimpleNameSpace.create_by_method_body(method_node))
        else:
            self._simple_name_space = SimpleNameSpace()
        self._name_space = self._class_context.get_name_space()
        self._name_space.add_space(self._simple_name_space)

    @staticmethod
    def create_by_method_name(class_context: Optional[ClassContextBase], method_name: str) -> Optional["MethodContext"]:
        # 如果方法名和类名一样，则说明方法为初始化方法，将方法名改为 init
        if class_context is None:
            return None

        class_absolute_name = class_context.get_runtime_class().absolute_name

        if get_last_name_from_absolute_name(class_context.class_name) == method_name:
            method_name = "init"

        method_info = class_context.get_method_node_by_name(method_name)

        # 递归地从内部类向外部类寻找方法
        while method_info is None and class_context.outer_class_context is not None:
            class_context = class_context.outer_class_context
            method_info = class_context.get_method_node_by_name(method_name)

        # 如果最终找不到方法
        if method_info is None:
            # 枚举类的 values() 方法
            if ast.Modifier.ENUM in class_context.class_node.modifiers.flags and method_name == "values":
                return MethodContext(
                    project_context=class_context.project_context,
                    file_context=class_context.file_context,
                    class_context=class_context,
                    method_name=method_name,
                    method_node=None
                )

            # 默认的构造方法
            if method_name == "init":
                return MethodContext(
                    project_context=class_context.project_context,
                    file_context=class_context.file_context,
                    class_context=class_context,
                    method_name=method_name,
                    method_node=None
                )

            LOGGER.warning(f"找不到方法 {class_absolute_name}.{method_name}")
            return None

        return MethodContext(
            project_context=class_context.project_context,
            file_context=class_context.file_context,
            class_context=class_context,
            method_name=method_name,
            method_node=method_info[1]
        )

    @property
    def project_context(self) -> ProjectContextBase:
        """返回所属的项目上下文管理器"""
        return self._project_context

    @property
    def file_context(self) -> FileContextBase:
        """返回所属的文件上下文管理器"""
        return self._file_context

    @property
    def class_context(self) -> ClassContextBase:
        """返回所属的类上下文管理器"""
        return self._class_context

    @property
    def method_name(self) -> str:
        """返回方法名称"""
        return self._method_name

    @property
    def method_node(self) -> ast.Method:
        """返回方法的抽象语法树节点"""
        return self._method_node

    @property
    def block_statements(self) -> List[ast.Statement]:
        """获取代码块中的语句列表"""
        if self.method_node.block is None:
            return []
        return self.method_node.block.statements

    def get_runtime_method(self) -> RuntimeMethod:
        """返回当前方法上下文对应的 RuntimeMethod 对象"""
        return RuntimeMethod(
            belong_class=self.class_context.get_runtime_class(),
            method_name=self.method_name
        )

    # ------------------------------ 命名空间管理器 ------------------------------

    def get_name_space(self) -> NameSpace:
        """返回包含类变量、方法参数变量和方法代码块中变量的命名空间"""
        name_space = self._class_context.get_name_space()
        name_space.add_space(self._simple_name_space)
        return name_space

    # ------------------------------ 方法调用遍历器 ------------------------------

    def get_method_invocation(self,
                              runtime_method: RuntimeMethod,
                              namespace: NameSpace,
                              statement_node: ast.Tree,
                              outer_runtime_method: Optional[RuntimeMethod] = None,
                              outer_method_param_idx: Optional[int] = None
                              ) -> Generator[Tuple[RuntimeMethod, List[ast.Expression]], None, None]:
        """获取当前表达式中调用的方法

        适配场景：
        `name1()`
        `name1.name2()`
        `name1.name2.name3()`：依赖泛型解析器，获取 `name2` 的类型
        `name1().name2()` 或 `name1.name2().name3()`：依赖泛型管理器，获取 `name1()` 的类型

        Parameters
        ----------
        runtime_method : RuntimeMethod
            当前方法所在的方法上下文管理器
        namespace : NameSpace
            当前方法所在位置的命名空间
        statement_node : ast.Tree
            待分析的抽象语法树节点
        outer_runtime_method : Optional[RuntimeClass], default = None
            如果当前抽象语法树节点为某个方法的参数，则为调用包含该参数的外层方法的 RuntimeMethod 对象，用于实现 lambda 语句的类型推断
        outer_method_param_idx : Optional[int], default = None
            如果当前抽象语法树节点为某个方法的参数，则为调用包含该参数的外层方法的参数下标，用于实现 lambda 语句的类型推断
        """
        for visit_namespace, visit_node in self.visitor_tree(runtime_method, namespace, statement_node):
            if not isinstance(visit_namespace, NameSpace):
                print(visit_namespace, visit_node)

            # -------------------- 递归元素产出 --------------------
            if isinstance(visit_node, ast.MethodInvocation):

                method_select = visit_node.method_select

                if isinstance(method_select, ast.Identifier):
                    method_name = method_select.name
                    if method_name in self.file_context.import_method_hash:
                        res_runtime_method = self.file_context.import_method_hash[method_name]
                        # 调用 import 导入的静态方法
                        yield res_runtime_method, visit_node.arguments
                    else:
                        # 调用当前类的其他方法 TODO 待优先获取当前类的其他方法
                        res_runtime_method = RuntimeMethod(
                            belong_class=RuntimeClass.create(
                                package_name=self.file_context.package_name,
                                public_class_name=self.file_context.public_class_name,
                                class_name=self.class_context.class_name,
                                type_arguments=None  # TODO 待改为当前类构造时的泛型
                            ),
                            method_name=method_name
                        )
                        LOGGER.debug(f"生成调用方法(类型 1): {res_runtime_method}")
                        yield res_runtime_method, visit_node.arguments

                # name1.name2() / name1.name2.name3() / name1().name2() / name1.name2().name3()
                elif isinstance(method_select, ast.MemberSelect):
                    expression = method_select.expression
                    runtime_class = self.infer_runtime_class_by_node(runtime_method, visit_namespace, expression)
                    res_runtime_method = RuntimeMethod(
                        belong_class=runtime_class,
                        method_name=method_select.identifier.name
                    )
                    LOGGER.debug(f"生成调用方法(类型 2): {res_runtime_method}")
                    yield res_runtime_method, visit_node.arguments

                else:
                    LOGGER.error(f"get_method_invocation, 暂不支持的表达式类型: {visit_node}")

            elif isinstance(visit_node, ast.NewClass):
                identifier = visit_node.identifier
                if isinstance(identifier, ast.Identifier):
                    method_class_name = identifier.name
                    method_runtime_class = self.file_context.infer_runtime_class_by_identifier_name(method_class_name)
                    res_runtime_method = RuntimeMethod(
                        belong_class=method_runtime_class,
                        method_name=method_class_name
                    )
                    LOGGER.debug(f"生成调用方法(类型 3): {res_runtime_method}")
                    yield res_runtime_method, visit_node.arguments
                elif isinstance(identifier, ast.ParameterizedType):
                    identifier_type_name = identifier.type_name
                    assert isinstance(identifier_type_name, ast.Identifier)
                    method_class_name = identifier_type_name.name
                    method_runtime_class = self.file_context.infer_runtime_class_by_identifier_name(method_class_name)
                    type_arguments = [
                        self.infer_runtime_class_by_node(runtime_method, visit_namespace, type_argument)
                        for type_argument in identifier.type_arguments
                    ]
                    res_runtime_method = RuntimeMethod(
                        belong_class=RuntimeClass.create(
                            package_name=method_runtime_class.package_name,
                            public_class_name=method_runtime_class.public_class_name,
                            class_name=method_runtime_class.class_name,
                            type_arguments=type_arguments
                        ),
                        method_name=method_class_name
                    )
                    LOGGER.debug(f"生成调用方法(类型 4): {res_runtime_method}")
                    yield res_runtime_method, visit_node.arguments
                elif isinstance(identifier, ast.MemberSelect):
                    runtime_class = self.infer_runtime_class_by_node(runtime_method, visit_namespace, identifier,
                                                                     is_type=True)
                    res_runtime_method = RuntimeMethod(
                        belong_class=runtime_class,
                        method_name=identifier.identifier.name
                    )
                    yield res_runtime_method, visit_node.arguments
                    LOGGER.debug(f"生成调用方法(类型 5): {res_runtime_method}")
                else:
                    LOGGER.error(f"NewClass 暂不支持的类型: {identifier}")

    def visitor_tree(self,
                     runtime_method: RuntimeMethod,
                     namespace: NameSpace,
                     ast_node: ast.Tree,
                     outer_runtime_method: Optional[RuntimeMethod] = None,
                     outer_method_param_idx: Optional[int] = None
                     ) -> Generator[Tuple[NameSpace, ast.Tree], None, None]:
        """获取当前表达式中调用的方法

        Parameters
        ----------
        runtime_method : RuntimeMethod
            当前方法所在的方法上下文管理器
        namespace : NameSpace
            当前方法所在位置的命名空间
        ast_node : ast.Tree
            待分析的抽象语法树节点
        outer_runtime_method : Optional[RuntimeClass], default = None
            如果当前抽象语法树节点为某个方法的参数，则为调用包含该参数的外层方法的 RuntimeMethod 对象，用于实现 lambda 语句的类型推断
        outer_method_param_idx : Optional[int], default = None
            如果当前抽象语法树节点为某个方法的参数，则为调用包含该参数的外层方法的参数下标，用于实现 lambda 语句的类型推断
        """
        if ast_node is None:
            return

        # 产出递归元素
        yield namespace, ast_node

        # 递归结束条件
        if ast_node.kind in {ast.TreeKind.IDENTIFIER, ast.TreeKind.INT_LITERAL, ast.TreeKind.LONG_LITERAL,
                             ast.TreeKind.FLOAT_LITERAL, ast.TreeKind.DOUBLE_LITERAL, ast.TreeKind.CHAR_LITERAL,
                             ast.TreeKind.STRING_LITERAL, ast.TreeKind.BOOLEAN_LITERAL,
                             ast.TreeKind.NULL_LITERAL}:
            return

        # 递归
        if isinstance(ast_node, ast.MethodInvocation):
            yield from self.visitor_tree(runtime_method, namespace, ast_node.method_select)

            method_select = ast_node.method_select

            if isinstance(method_select, ast.Identifier):
                method_name = method_select.name
                if method_name in self.file_context.import_method_hash:
                    res_runtime_method = self.file_context.import_method_hash[method_name]
                else:
                    # 调用当前类的其他方法 TODO 待优先获取当前类的其他方法
                    res_runtime_method = RuntimeMethod(
                        belong_class=RuntimeClass.create(
                            package_name=self.file_context.package_name,
                            public_class_name=self.file_context.public_class_name,
                            class_name=self.class_context.class_name,
                            type_arguments=None  # TODO 待改为当前类构造时的泛型
                        ),
                        method_name=method_name
                    )

            # name1.name2() / name1.name2.name3() / name1().name2() / name1.name2().name3()
            elif isinstance(method_select, ast.MemberSelect):
                expression = method_select.expression
                runtime_class = self.infer_runtime_class_by_node(runtime_method, namespace, expression)
                res_runtime_method = RuntimeMethod(
                    belong_class=runtime_class,
                    method_name=method_select.identifier.name
                )

            else:
                res_runtime_method = None
                LOGGER.error(f"visitor_tree, 暂不支持的表达式类型: {ast_node}")

            # 递归处理方法参数
            for idx, argument in enumerate(ast_node.arguments):
                yield from self.visitor_tree(runtime_method, namespace, argument,
                                             outer_runtime_method=res_runtime_method,
                                             outer_method_param_idx=idx)

        elif isinstance(ast_node, ast.NewClass):
            identifier = ast_node.identifier
            if isinstance(identifier, ast.Identifier):
                method_class_name = identifier.name
                method_runtime_class = self.file_context.infer_runtime_class_by_identifier_name(method_class_name)
                res_runtime_method = RuntimeMethod(
                    belong_class=method_runtime_class,
                    method_name=method_class_name
                )
            elif isinstance(identifier, ast.ParameterizedType):
                identifier_type_name = identifier.type_name
                assert isinstance(identifier_type_name, ast.Identifier)
                method_class_name = identifier_type_name.name
                method_runtime_class = self.file_context.infer_runtime_class_by_identifier_name(method_class_name)
                type_arguments = [
                    self.infer_runtime_class_by_node(runtime_method, namespace, type_argument)
                    for type_argument in identifier.type_arguments
                ]
                res_runtime_method = RuntimeMethod(
                    belong_class=RuntimeClass.create(
                        package_name=method_runtime_class.package_name,
                        public_class_name=method_runtime_class.public_class_name,
                        class_name=method_runtime_class.class_name,
                        type_arguments=type_arguments
                    ),
                    method_name=method_class_name
                )
            elif isinstance(identifier, ast.MemberSelect):
                runtime_class = self.infer_runtime_class_by_node(runtime_method, namespace, identifier, is_type=True)
                res_runtime_method = RuntimeMethod(
                    belong_class=runtime_class,
                    method_name=identifier.identifier.name
                )
            else:
                res_runtime_method = None
                LOGGER.error(f"NewClass 暂不支持的类型: {identifier}")

            # 递归处理方法参数
            for idx, argument in enumerate(ast_node.arguments):
                yield from self.visitor_tree(runtime_method, namespace, argument,
                                             outer_runtime_method=res_runtime_method,
                                             outer_method_param_idx=idx)

        elif isinstance(ast_node, ast.InstanceOf):
            yield from self.visitor_tree(runtime_method, namespace, ast_node.expression)
            yield from self.visitor_tree(runtime_method, namespace, ast_node.instance_type)
            yield from self.visitor_tree(runtime_method, namespace, ast_node.pattern)
        elif isinstance(ast_node, ast.TypeCast):
            yield from self.visitor_tree(runtime_method, namespace, ast_node.cast_type)
            yield from self.visitor_tree(runtime_method, namespace, ast_node.expression)
        elif isinstance(ast_node, (ast.Break, ast.Continue)):
            return  # break 语句中和 contain 语句中不会调用其他方法
        elif isinstance(ast_node, ast.Throw):
            yield from self.visitor_tree(runtime_method, namespace, ast_node.expression)
        elif isinstance(ast_node, ast.Variable):
            yield from self.visitor_tree(runtime_method, namespace, ast_node.initializer)
        elif isinstance(ast_node, ast.MemberSelect):
            yield from self.visitor_tree(runtime_method, namespace, ast_node.expression)
        elif isinstance(ast_node, ast.ExpressionStatement):
            yield from self.visitor_tree(runtime_method, namespace, ast_node.expression)
        elif isinstance(ast_node, ast.Assignment):
            yield from self.visitor_tree(runtime_method, namespace, ast_node.expression)
        elif isinstance(ast_node, ast.If):
            yield from self.visitor_tree(runtime_method, namespace, ast_node.condition)
            yield from self.visitor_tree(runtime_method, namespace, ast_node.then_statement)
            yield from self.visitor_tree(runtime_method, namespace, ast_node.else_statement)
        elif isinstance(ast_node, ast.Block):
            namespace.add_space(SimpleNameSpace.create_by_statements(ast_node.statements))
            for sub_node in ast_node.statements:
                yield from self.visitor_tree(runtime_method, namespace, sub_node)
            namespace.pop_space()
        elif isinstance(ast_node, ast.Parenthesized):
            yield from self.visitor_tree(runtime_method, namespace, ast_node.expression)
        elif isinstance(ast_node, ast.ArrayAccess):
            yield from self.visitor_tree(runtime_method, namespace, ast_node.expression)
            yield from self.visitor_tree(runtime_method, namespace, ast_node.index)
        elif isinstance(ast_node, ast.Binary):
            yield from self.visitor_tree(runtime_method, namespace, ast_node.left_operand)
            yield from self.visitor_tree(runtime_method, namespace, ast_node.right_operand)
        elif isinstance(ast_node, ast.Return):
            yield from self.visitor_tree(runtime_method, namespace, ast_node.expression)
        elif isinstance(ast_node, ast.ConditionalExpression):
            yield from self.visitor_tree(runtime_method, namespace, ast_node.condition)
            yield from self.visitor_tree(runtime_method, namespace, ast_node.true_expression)
            yield from self.visitor_tree(runtime_method, namespace, ast_node.false_expression)
        elif isinstance(ast_node, ast.EnhancedForLoop):
            namespace.add_space(SimpleNameSpace.create_by_variable(ast_node.variable))
            yield from self.visitor_tree(runtime_method, namespace, ast_node.variable)
            yield from self.visitor_tree(runtime_method, namespace, ast_node.expression)
            yield from self.visitor_tree(runtime_method, namespace, ast_node.statement)
            namespace.pop_space()
        elif isinstance(ast_node, ast.Unary):
            yield from self.visitor_tree(runtime_method, namespace, ast_node.expression)
        elif isinstance(ast_node, ast.Try):
            namespace.add_space(SimpleNameSpace.create_by_statements(ast_node.resources))
            yield from self.visitor_tree(runtime_method, namespace, ast_node.block)
            for sub_node in ast_node.catches:
                yield from self.visitor_tree(runtime_method, namespace, sub_node)
            yield from self.visitor_tree(runtime_method, namespace, ast_node.finally_block)
            for sub_node in ast_node.resources:
                yield from self.visitor_tree(runtime_method, namespace, sub_node)
            namespace.pop_space()
        elif isinstance(ast_node, ast.Catch):
            namespace.add_space(SimpleNameSpace.create_by_variable(ast_node.parameter))
            yield from self.visitor_tree(runtime_method, namespace, ast_node.block)
            namespace.pop_space()
        elif isinstance(ast_node, ast.Switch):
            yield from self.visitor_tree(runtime_method, namespace, ast_node.expression)
            for case_node in ast_node.cases:
                yield from self.visitor_tree(runtime_method, namespace, case_node)
        elif isinstance(ast_node, ast.Case):
            if ast_node.expressions is not None:
                for sub_node in ast_node.expressions:
                    yield from self.visitor_tree(runtime_method, namespace, sub_node)
            for sub_node in ast_node.labels:
                yield from self.visitor_tree(runtime_method, namespace, sub_node)
            yield from self.visitor_tree(runtime_method, namespace, ast_node.guard)
            namespace.add_space(SimpleNameSpace.create_by_statements(ast_node.statements))
            for sub_node in ast_node.statements:
                yield from self.visitor_tree(runtime_method, namespace, sub_node)
            yield from self.visitor_tree(runtime_method, namespace, ast_node.body)
            namespace.pop_space()
        elif isinstance(ast_node, ast.PatternCaseLabel):
            yield from self.visitor_tree(runtime_method, namespace, ast_node.pattern)
        elif isinstance(ast_node, ast.ConstantCaseLabel):
            yield from self.visitor_tree(runtime_method, namespace, ast_node.expression)
        elif isinstance(ast_node, ast.DefaultCaseLabel):
            return  # switch 语句的 default 子句不会调用其他方法
        elif isinstance(ast_node, ast.ForLoop):
            namespace.add_space(SimpleNameSpace.create_by_statements(ast_node.initializer))
            for sub_node in ast_node.initializer:
                yield from self.visitor_tree(runtime_method, namespace, sub_node)
            yield from self.visitor_tree(runtime_method, namespace, ast_node.condition)
            for sub_node in ast_node.update:
                yield from self.visitor_tree(runtime_method, namespace, sub_node)
            yield from self.visitor_tree(runtime_method, namespace, ast_node.statement)
            namespace.pop_space()
        elif isinstance(ast_node, ast.PrimitiveType):
            return  # 原生类型中不会调用其他方法
        elif isinstance(ast_node, ast.LambdaExpression):
            simple_name_space = SimpleNameSpace()
            # 获取 lambda 表达式对应的参数类型
            lambda_runtime_class = self.project_context.get_runtime_class_by_runtime_method_param(
                runtime_method=outer_runtime_method,
                param_idx=outer_method_param_idx
            )
            # 获取 lambda 表达式的参数类型
            lambda_param_type_list = self.project_context.get_runtime_class_list_by_functional_interface(
                runtime_class=lambda_runtime_class
            )
            if lambda_param_type_list is not None:
                if len(ast_node.parameters) == len(lambda_param_type_list):
                    for sub_idx, sub_node in enumerate(ast_node.parameters):
                        if sub_node.variable_type is not None:
                            simple_name_space.set_name(sub_node.name, sub_node.variable_type)
                        else:
                            simple_name_space.set_name(sub_node.name, lambda_param_type_list[sub_idx])
                else:
                    LOGGER.warning(f"lambda 表达式参数数量异常, position={outer_runtime_method}, "
                                   f"expected: {len(lambda_param_type_list)}, actual={len(ast_node.parameters)}")
            else:
                LOGGER.warning(f"无法获取 lambda 表达式的参数类型: {outer_runtime_method}")
            namespace.add_space(simple_name_space)
            yield from self.visitor_tree(runtime_method, namespace, ast_node.body)
            namespace.pop_space()
        elif isinstance(ast_node, ast.WhileLoop):
            yield from self.visitor_tree(runtime_method, namespace, ast_node.condition)
            yield from self.visitor_tree(runtime_method, namespace, ast_node.statement)
        elif isinstance(ast_node, ast.NewArray):
            yield from self.visitor_tree(runtime_method, namespace, ast_node.array_type)
            for sub_node in ast_node.dimensions:
                yield from self.visitor_tree(runtime_method, namespace, sub_node)
            if ast_node.initializers is not None:
                for sub_node in ast_node.initializers:
                    yield from self.visitor_tree(runtime_method, namespace, sub_node)
            if ast_node.annotations is not None:
                for sub_node in ast_node.annotations:
                    yield from self.visitor_tree(runtime_method, namespace, sub_node)
            if ast_node.dim_annotations is not None:
                for node_list in ast_node.dim_annotations:
                    for sub_node in node_list:
                        yield from self.visitor_tree(runtime_method, namespace, sub_node)
        elif isinstance(ast_node, ast.MemberReference):
            yield from self.visitor_tree(runtime_method, namespace, ast_node.expression)
            if ast_node.type_arguments is not None:
                for sub_node in ast_node.type_arguments:
                    yield from self.visitor_tree(runtime_method, namespace, sub_node)
        elif isinstance(ast_node, ast.CompoundAssignment):
            yield from self.visitor_tree(runtime_method, namespace, ast_node.variable)
            yield from self.visitor_tree(runtime_method, namespace, ast_node.expression)
        elif isinstance(ast_node, ast.EmptyStatement):
            return  # 跳过空表达式
        elif isinstance(ast_node, ast.Assert):
            yield from self.visitor_tree(runtime_method, namespace, ast_node.assertion)
        else:
            LOGGER.error(f"visitor_tree: 未知表达式类型: {ast_node}")
            yield None, None

    def search_node(self,
                    statement_node: ast.Tree,
                    search_type: Type,
                    ) -> Generator[ast.Tree, None, None]:
        """获取当前表达式中调用的方法中，寻找 search_type 类型的节点"""
        if statement_node is None:
            return

        if isinstance(statement_node, search_type):
            yield statement_node

        for field in dataclasses.fields(statement_node):
            value = getattr(statement_node, field.name)
            if isinstance(value, ast.Tree):
                yield from self.search_node(value, search_type)
            elif isinstance(value, (list, set, tuple)):
                for sub_node in value:
                    if isinstance(sub_node, ast.Tree):
                        yield from self.search_node(sub_node, search_type)

    # ------------------------------ 类型获取处理器 ------------------------------

    def infer_runtime_class_by_node(self,
                                    runtime_method: RuntimeMethod,
                                    namespace: NameSpace,
                                    type_node: Optional[ast.Tree],
                                    is_not_variable: bool = False,
                                    is_type: bool = False) -> Optional[RuntimeClass]:
        """推断出现在当前方法中抽象语法树节点的类型

        Parameters
        ----------
        runtime_method : RuntimeMethod
            目标抽象语法树节点所在运行中方法
        namespace : NameSpace
            目标抽象语法树节点所在位置的命名空间
        type_node : Optional[ast.Tree]
            目标抽象语法树节点
        is_not_variable : bool, default = False
            目标抽象语法树节点是否可能出现在命名空间中
        is_type : bool, default = False
            目标抽象语法树节点是否为类型
        """
        if type_node is None:
            return None

        # name1
        if isinstance(type_node, ast.Identifier):
            return self.infer_runtime_class_by_identifier_name(
                runtime_method=runtime_method,
                namespace=namespace,
                identifier_name=type_node.name,
                is_not_variable=is_not_variable,
                is_type=is_type
            )

        # name1.name2：如果 name1 为项目外元素，则可能无法获取
        elif isinstance(type_node, ast.MemberSelect):
            return self._get_runtime_class_by_member_select(
                runtime_method=runtime_method,
                namespace=namespace,
                member_select_node=type_node,
                is_type=is_type
            )

        # name1().name2()
        elif isinstance(type_node, ast.MethodInvocation):

            # 获取 name1 的类型
            method_select_node = type_node.method_select
            # name1() -- 调用当前类的其他方法
            if isinstance(method_select_node, ast.Identifier):
                runtime_method = RuntimeMethod(
                    belong_class=RuntimeClass.create(
                        package_name=self.file_context.package_name,
                        public_class_name=self.file_context.public_class_name,
                        class_name=self.class_context.class_name,
                        type_arguments=None  # TODO 待改为当前类构造时的泛型
                    ),
                    method_name=method_select_node.name
                )

            # name1.name2() / name1.name2.name3() / name1().name2() / name1.name2().name3()
            elif isinstance(method_select_node, ast.MemberSelect):
                expression = method_select_node.expression
                runtime_class = self.infer_runtime_class_by_node(runtime_method, namespace, expression)
                runtime_method = RuntimeMethod(
                    belong_class=runtime_class,
                    method_name=method_select_node.identifier.name
                )

            else:
                LOGGER.error(f"get_runtime_class_by_node: 未知的类型 {type_node}")
                return None

            return self.project_context.get_runtime_class_by_runtime_method_return_type(runtime_method)

        # 括号表达式
        elif isinstance(type_node, ast.Parenthesized):
            return self.infer_runtime_class_by_node(runtime_method, namespace, type_node.expression)

        # 强制类型转换表达式
        elif isinstance(type_node, ast.TypeCast):
            return self.infer_runtime_class_by_node(runtime_method, namespace, type_node.expression)

        # 字符串字面值
        elif isinstance(type_node, ast.StringLiteral):
            return RuntimeClass.create(
                package_name="java.lang",
                public_class_name="String",
                class_name="String",
                type_arguments=[]
            )

        # NewClass 节点
        elif isinstance(type_node, ast.NewClass):
            return self.infer_runtime_class_by_node(
                runtime_method=runtime_method,
                namespace=namespace,
                type_node=type_node.identifier,
                is_type=True
            )

        # ArrayAccess 节点
        elif isinstance(type_node, ast.ArrayAccess):
            variable_type = self.infer_runtime_class_by_node(runtime_method, namespace, type_node.expression)
            if variable_type is None or variable_type.type_arguments is None or len(variable_type.type_arguments) < 1:
                LOGGER.warning(f"数组类型没有第 0 个泛型: {variable_type}")
            return variable_type.type_arguments[0]

        # ParameterizedType 节点
        elif isinstance(type_node, ast.ParameterizedType):
            variable_type = self.infer_runtime_class_by_node(runtime_method, namespace, type_node.type_name,
                                                             is_not_variable=True, is_type=True)
            variable_arguments = [
                self.infer_runtime_class_by_node(runtime_method, namespace, argument, is_not_variable=True,
                                                 is_type=True)
                for argument in type_node.type_arguments]
            if variable_type is not None:
                return RuntimeClass.create(
                    package_name=variable_type.package_name,
                    public_class_name=variable_type.class_name,
                    class_name=variable_type.class_name,
                    type_arguments=variable_arguments
                )
            else:
                LOGGER.warning(f"找不到类型 {type_node.type_name}, position={runtime_method}")

        # 二元表达式
        elif isinstance(type_node, ast.Binary):
            return self.infer_runtime_class_by_node(runtime_method, namespace, type_node.left_operand)

        # 初始化类型
        # 【Java 样例】String[]
        if isinstance(type_node, ast.ArrayType):
            runtime_class = self.infer_runtime_class_by_node(runtime_method, namespace, type_node.expression)
            return RuntimeClass.create(
                package_name="java.lang",
                public_class_name="Array",
                class_name="Array",
                type_arguments=[runtime_class]
            )

        self.class_context.infer_runtime_class_by_node(
            runtime_class=runtime_method.belong_class,
            type_node=type_node
        )

    def infer_runtime_class_by_identifier_name(self,
                                               runtime_method: RuntimeMethod,
                                               namespace: NameSpace,
                                               identifier_name: str,
                                               is_not_variable: bool = False,
                                               is_type: bool = False,
                                               need_warning: bool = True
                                               ) -> RuntimeClass:
        """推断出现在当前方法中标识符名称的类型"""

        # 【场景】`this`
        # - 标识符类型（`Identifier`）节点
        # - 标识符的值为 `this`
        if identifier_name == "this":
            return self.class_context.get_runtime_class()

        # 【场景】变量名
        # - 识符类型（`Identifier`）节点
        # - 标识符的值在当前层级命名空间中
        if is_not_variable is False and namespace.has_name(identifier_name):  # TODO 命名空间中不需要包含类属性
            type_node = namespace.get_name(identifier_name)
            if isinstance(type_node, RuntimeClass):
                return type_node
            return self.infer_runtime_class_by_node(
                runtime_method=runtime_method,
                namespace=namespace,
                type_node=type_node,
                is_not_variable=True,
                is_type=True
            )

        return self.class_context.infer_runtime_class_by_identifier_name(
            runtime_class=runtime_method.belong_class,
            identifier_name=identifier_name,
            need_warning=need_warning
        )

    def _get_runtime_class_by_member_select(self,
                                            runtime_method: RuntimeMethod,
                                            namespace: NameSpace,
                                            member_select_node: ast.MemberSelect,
                                            is_type: bool) -> Optional[RuntimeClass]:
        """根据当前方法中的 MemberSelect 节点构造 RuntimeClass 对象"""

        # 【场景】直接使用类的绝对引用
        # - 抽象语法树节点 `MemberSelect`，且其中包含抽象语法树节点也是 `MemberSelect` 或 `Identifier`
        # - 第一个抽象语法树节点（`Identifier`）作为标识符无法被解析
        if is_long_member_select(member_select_node):
            class_absolute_name = member_select_node.generate()
            first_name = class_absolute_name[:class_absolute_name.index(".")]
            if self.infer_runtime_class_by_identifier_name(runtime_method, namespace, first_name,
                                                           need_warning=False) is None:
                package_name, class_name = split_last_name_from_absolute_name(class_absolute_name)
                return RuntimeClass(
                    package_name=package_name,
                    public_class_name=class_name,
                    class_name=class_name,
                    type_arguments=None  # 调用的一定是静态方法，不需要考虑类型参数
                )

            # 如果是类型，则一定是子类，ClassName.SubClassName
            if is_type is True:
                first_name = get_first_name_from_absolute_name(class_absolute_name)
                runtime_class = self.infer_runtime_class_by_identifier_name(
                    runtime_method=runtime_method,
                    namespace=namespace,
                    identifier_name=first_name,
                    is_type=True
                )
                return RuntimeClass.create(
                    package_name=runtime_class.package_name,
                    public_class_name=runtime_class.public_class_name,
                    class_name=class_absolute_name,
                    type_arguments=None
                )

        # 获取 name1 的类型
        runtime_class = self.infer_runtime_class_by_node(runtime_method, namespace, member_select_node.expression)

        # 全局搜索类属性的类型
        runtime_variable = RuntimeVariable(
            belong_class=runtime_class,
            variable_name=member_select_node.identifier.name
        )

        return self._project_context.get_type_node_by_runtime_variable(runtime_variable)

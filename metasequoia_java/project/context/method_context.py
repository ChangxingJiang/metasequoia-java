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
from metasequoia_java.project.utils import NameSpace
from metasequoia_java.project.utils import SimpleNameSpace

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
                 method_node: ast.Method):
        self._project_context = project_context
        self._file_context = file_context
        self._class_context = class_context
        self._method_name = method_name
        self._method_node = method_node

        # 初始化方法的命名空间
        self._simple_name_space = (SimpleNameSpace.create_by_method_params(method_node)
                                   + SimpleNameSpace.create_by_method_body(method_node))
        self._name_space = self._class_context.get_name_space()
        self._name_space.add_space(self._simple_name_space)

    @staticmethod
    def create_by_method_name(class_context: Optional[ClassContextBase], method_name: str) -> Optional["MethodContext"]:
        # 如果方法名和类名一样，则说明方法为初始化方法，将方法名改为 init
        if class_context is None:
            return None
        if method_name == class_context.class_name:
            method_name = "init"

        method_info = class_context.get_method_node_by_name(method_name)
        if method_info is None:
            # TODO 待考虑将类处理逻辑合并到其他位置
            class_name = class_context.class_name
            if "." in class_name:
                class_name = class_name[class_name.rindex(".") + 1:]
            if class_name != method_name:  # 未声明的默认构造方法不需要处理
                LOGGER.warning(f"找不到方法 {class_context.get_runtime_class().absolute_name}.{method_name}")
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

    def get_simple_name_space(self) -> SimpleNameSpace:
        """返回方法参数变量和方法代码块中变量的单层命名空间"""
        return self._simple_name_space

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
        """
        # -------------------- 递归结束条件 --------------------
        if statement_node is None:
            return

        if statement_node.kind in {ast.TreeKind.IDENTIFIER, ast.TreeKind.INT_LITERAL, ast.TreeKind.LONG_LITERAL,
                                   ast.TreeKind.FLOAT_LITERAL, ast.TreeKind.DOUBLE_LITERAL, ast.TreeKind.CHAR_LITERAL,
                                   ast.TreeKind.STRING_LITERAL, ast.TreeKind.BOOLEAN_LITERAL,
                                   ast.TreeKind.NULL_LITERAL}:
            return

        # -------------------- 递归元素产出 --------------------
        if isinstance(statement_node, ast.MethodInvocation):

            method_select = statement_node.method_select

            if isinstance(method_select, ast.Identifier):
                method_name = method_select.name
                if method_name in self.file_context.import_method_hash:
                    res_runtime_method = self.file_context.import_method_hash[method_name]
                    # 调用 import 导入的静态方法
                    yield res_runtime_method, statement_node.arguments
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
                    yield res_runtime_method, statement_node.arguments

            # name1.name2() / name1.name2.name3() / name1().name2() / name1.name2().name3()
            elif isinstance(method_select, ast.MemberSelect):
                expression = method_select.expression
                runtime_class = self.infer_runtime_class_by_node(runtime_method, namespace, expression)
                res_runtime_method = RuntimeMethod(
                    belong_class=runtime_class,
                    method_name=method_select.identifier.name
                )
                LOGGER.debug(f"生成调用方法(类型 2): {res_runtime_method}")
                yield res_runtime_method, statement_node.arguments

                # 继续递归寻找调用的方法
                yield from self.get_method_invocation(runtime_method, namespace, expression)

            else:
                res_runtime_method = None
                print(f"get_method_invocation, 暂不支持的表达式类型: {statement_node}")

            # 递归处理方法参数
            for idx, argument in enumerate(statement_node.arguments):
                yield from self.get_method_invocation(runtime_method, namespace, argument,
                                                      outer_runtime_method=res_runtime_method,
                                                      outer_method_param_idx=idx)

            return

        if isinstance(statement_node, ast.NewClass):
            identifier = statement_node.identifier
            if isinstance(identifier, ast.Identifier):
                method_class_name = identifier.name
                method_runtime_class = self.file_context.infer_runtime_class_by_identifier_name(method_class_name)
                res_runtime_method = RuntimeMethod(
                    belong_class=method_runtime_class,
                    method_name=method_class_name
                )
                LOGGER.debug(f"生成调用方法(类型 3): {res_runtime_method}")
                yield res_runtime_method, statement_node.arguments
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
                LOGGER.debug(f"生成调用方法(类型 4): {res_runtime_method}")
                yield res_runtime_method, statement_node.arguments
            else:
                res_runtime_method = None
                print("NewClass 暂不支持的类型: ", identifier)

            # 递归处理方法参数
            for idx, argument in enumerate(statement_node.arguments):
                yield from self.get_method_invocation(runtime_method, namespace, argument,
                                                      outer_runtime_method=res_runtime_method,
                                                      outer_method_param_idx=idx)

            return

        # -------------------- 其他递归条件 --------------------
        if isinstance(statement_node, ast.InstanceOf):
            yield from self.get_method_invocation(runtime_method, namespace, statement_node.expression)
            yield from self.get_method_invocation(runtime_method, namespace, statement_node.instance_type)
            yield from self.get_method_invocation(runtime_method, namespace, statement_node.pattern)
        elif isinstance(statement_node, ast.TypeCast):
            yield from self.get_method_invocation(runtime_method, namespace, statement_node.cast_type)
            yield from self.get_method_invocation(runtime_method, namespace, statement_node.expression)
        elif isinstance(statement_node, (ast.Break, ast.Continue)):
            return  # break 语句中和 contain 语句中不会调用其他方法
        elif isinstance(statement_node, ast.Throw):
            yield from self.get_method_invocation(runtime_method, namespace, statement_node.expression)
        elif isinstance(statement_node, ast.Variable):
            yield from self.get_method_invocation(runtime_method, namespace, statement_node.initializer)
        elif isinstance(statement_node, ast.MemberSelect):
            yield from self.get_method_invocation(runtime_method, namespace, statement_node.expression)
        elif isinstance(statement_node, ast.ExpressionStatement):
            yield from self.get_method_invocation(runtime_method, namespace, statement_node.expression)
        elif isinstance(statement_node, ast.Assignment):
            yield from self.get_method_invocation(runtime_method, namespace, statement_node.expression)
        elif isinstance(statement_node, ast.If):
            yield from self.get_method_invocation(runtime_method, namespace, statement_node.condition)
            yield from self.get_method_invocation(runtime_method, namespace, statement_node.then_statement)
            yield from self.get_method_invocation(runtime_method, namespace, statement_node.else_statement)
        elif isinstance(statement_node, ast.Block):
            namespace.add_space(SimpleNameSpace.create_by_statements(statement_node.statements))
            for sub_node in statement_node.statements:
                yield from self.get_method_invocation(runtime_method, namespace, sub_node)
            namespace.pop_space()
        elif isinstance(statement_node, ast.Parenthesized):
            yield from self.get_method_invocation(runtime_method, namespace, statement_node.expression)
        elif isinstance(statement_node, ast.ArrayAccess):
            yield from self.get_method_invocation(runtime_method, namespace, statement_node.expression)
            yield from self.get_method_invocation(runtime_method, namespace, statement_node.index)
        elif isinstance(statement_node, ast.Binary):
            yield from self.get_method_invocation(runtime_method, namespace, statement_node.left_operand)
            yield from self.get_method_invocation(runtime_method, namespace, statement_node.right_operand)
        elif isinstance(statement_node, ast.Return):
            yield from self.get_method_invocation(runtime_method, namespace, statement_node.expression)
        elif isinstance(statement_node, ast.ConditionalExpression):
            yield from self.get_method_invocation(runtime_method, namespace, statement_node.condition)
            yield from self.get_method_invocation(runtime_method, namespace, statement_node.true_expression)
            yield from self.get_method_invocation(runtime_method, namespace, statement_node.false_expression)
        elif isinstance(statement_node, ast.EnhancedForLoop):
            namespace.add_space(SimpleNameSpace.create_by_variable(statement_node.variable))
            yield from self.get_method_invocation(runtime_method, namespace, statement_node.variable)
            yield from self.get_method_invocation(runtime_method, namespace, statement_node.expression)
            yield from self.get_method_invocation(runtime_method, namespace, statement_node.statement)
            namespace.pop_space()
        elif isinstance(statement_node, ast.Unary):
            yield from self.get_method_invocation(runtime_method, namespace, statement_node.expression)
        elif isinstance(statement_node, ast.Try):
            namespace.add_space(SimpleNameSpace.create_by_statements(statement_node.resources))
            yield from self.get_method_invocation(runtime_method, namespace, statement_node.block)
            for sub_node in statement_node.catches:
                yield from self.get_method_invocation(runtime_method, namespace, sub_node)
            yield from self.get_method_invocation(runtime_method, namespace, statement_node.finally_block)
            for sub_node in statement_node.resources:
                yield from self.get_method_invocation(runtime_method, namespace, sub_node)
            namespace.pop_space()
        elif isinstance(statement_node, ast.Catch):
            namespace.add_space(SimpleNameSpace.create_by_variable(statement_node.parameter))
            yield from self.get_method_invocation(runtime_method, namespace, statement_node.block)
            namespace.pop_space()
        elif isinstance(statement_node, ast.Switch):
            yield from self.get_method_invocation(runtime_method, namespace, statement_node.expression)
            for case_node in statement_node.cases:
                yield from self.get_method_invocation(runtime_method, namespace, case_node)
        elif isinstance(statement_node, ast.Case):
            if statement_node.expressions is not None:
                for sub_node in statement_node.expressions:
                    yield from self.get_method_invocation(runtime_method, namespace, sub_node)
            for sub_node in statement_node.labels:
                yield from self.get_method_invocation(runtime_method, namespace, sub_node)
            yield from self.get_method_invocation(runtime_method, namespace, statement_node.guard)
            namespace.add_space(SimpleNameSpace.create_by_statements(statement_node.statements))
            for sub_node in statement_node.statements:
                yield from self.get_method_invocation(runtime_method, namespace, sub_node)
            yield from self.get_method_invocation(runtime_method, namespace, statement_node.body)
            namespace.pop_space()
        elif isinstance(statement_node, ast.PatternCaseLabel):
            yield from self.get_method_invocation(runtime_method, namespace, statement_node.pattern)
        elif isinstance(statement_node, ast.ConstantCaseLabel):
            yield from self.get_method_invocation(runtime_method, namespace, statement_node.expression)
        elif isinstance(statement_node, ast.DefaultCaseLabel):
            return  # switch 语句的 default 子句不会调用其他方法
        elif isinstance(statement_node, ast.ForLoop):
            namespace.add_space(SimpleNameSpace.create_by_statements(statement_node.initializer))
            for sub_node in statement_node.initializer:
                yield from self.get_method_invocation(runtime_method, namespace, sub_node)
            yield from self.get_method_invocation(runtime_method, namespace, statement_node.condition)
            for sub_node in statement_node.update:
                yield from self.get_method_invocation(runtime_method, namespace, sub_node)
            yield from self.get_method_invocation(runtime_method, namespace, statement_node.statement)
            namespace.pop_space()
        elif isinstance(statement_node, ast.PrimitiveType):
            return  # 原生类型中不会调用其他方法
        elif isinstance(statement_node, ast.LambdaExpression):
            simple_name_space = SimpleNameSpace()
            # print("外层:", len(statement_node.parameters), "-----", outer_runtime_method, outer_method_param_idx)
            # print("类型:", self.project_context.get_runtime_class_by_runtime_method_param(outer_runtime_method, outer_method_param_idx))
            for sub_idx, sub_node in enumerate(statement_node.parameters):
                # 执行类型的 lambda 表达式
                if sub_node.variable_type is not None:
                    simple_name_space.set_name(sub_node.name, sub_node.variable_type)
                else:
                    simple_name_space.set_name(sub_node.name, None)
            namespace.add_space(simple_name_space)
            yield from self.get_method_invocation(runtime_method, namespace, statement_node.body)
            namespace.pop_space()
        elif isinstance(statement_node, ast.WhileLoop):
            yield from self.get_method_invocation(runtime_method, namespace, statement_node.condition)
            yield from self.get_method_invocation(runtime_method, namespace, statement_node.statement)
        elif isinstance(statement_node, ast.NewArray):
            yield from self.get_method_invocation(runtime_method, namespace, statement_node.array_type)
            for sub_node in statement_node.dimensions:
                yield from self.get_method_invocation(runtime_method, namespace, sub_node)
            if statement_node.initializers is not None:
                for sub_node in statement_node.initializers:
                    yield from self.get_method_invocation(runtime_method, namespace, sub_node)
            if statement_node.annotations is not None:
                for sub_node in statement_node.annotations:
                    yield from self.get_method_invocation(runtime_method, namespace, sub_node)
            if statement_node.dim_annotations is not None:
                for node_list in statement_node.dim_annotations:
                    for sub_node in node_list:
                        yield from self.get_method_invocation(runtime_method, namespace, sub_node)
        elif isinstance(statement_node, ast.MemberReference):
            yield from self.get_method_invocation(runtime_method, namespace, statement_node.expression)
            if statement_node.type_arguments is not None:
                for sub_node in statement_node.type_arguments:
                    yield from self.get_method_invocation(runtime_method, namespace, sub_node)
        elif isinstance(statement_node, ast.CompoundAssignment):
            yield from self.get_method_invocation(runtime_method, namespace, statement_node.variable)
            yield from self.get_method_invocation(runtime_method, namespace, statement_node.expression)
        elif isinstance(statement_node, ast.EmptyStatement):
            return  # 跳过空表达式
        elif isinstance(statement_node, ast.Assert):
            yield from self.get_method_invocation(runtime_method, namespace, statement_node.assertion)
        else:
            print(f"get_method_invocation: 未知表达式类型: {statement_node}")
            yield None

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
                                    type_node: Optional[ast.Tree]) -> Optional[RuntimeClass]:
        """推断出现在当前方法中抽象语法树节点的类型"""
        if type_node is None:
            return None

        # name1
        if isinstance(type_node, ast.Identifier):
            return self.infer_runtime_class_by_identifier_name(runtime_method, namespace, type_node.name)

        # name1.name2：如果 name1 为项目外元素，则可能无法获取
        elif isinstance(type_node, ast.MemberSelect):
            return self._get_runtime_class_by_member_select(runtime_method, namespace, type_node)

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
                print(f"get_runtime_class_by_node: 未知的类型 {type_node}")
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
            return self.infer_runtime_class_by_node(runtime_method, namespace, type_node.identifier)

        # ArrayAccess 节点
        elif isinstance(type_node, ast.ArrayAccess):
            variable_type = self.infer_runtime_class_by_node(runtime_method, namespace, type_node.expression)
            return variable_type

        # ParameterizedType 节点
        elif isinstance(type_node, ast.ParameterizedType):
            variable_type = self.infer_runtime_class_by_node(runtime_method, namespace, type_node.type_name)
            variable_arguments = [self.infer_runtime_class_by_node(runtime_method, namespace, argument)
                                  for argument in type_node.type_arguments]
            return RuntimeClass.create(
                package_name=variable_type.package_name,
                public_class_name=variable_type.class_name,
                class_name=variable_type.class_name,
                type_arguments=variable_arguments
            )

        self.class_context.infer_runtime_class_by_node(
            runtime_class=runtime_method.belong_class,
            type_node=type_node
        )

    def infer_runtime_class_by_identifier_name(self,
                                               runtime_method: RuntimeMethod,
                                               namespace: NameSpace,
                                               identifier_name: str
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
        if namespace.has_name(identifier_name):  # TODO 命名空间中不需要包含类属性
            return self.class_context.infer_runtime_class_by_node(
                runtime_class=runtime_method.belong_class,
                type_node=namespace.get_name(identifier_name)
            )

        return self.class_context.infer_runtime_class_by_identifier_name(
            runtime_class=runtime_method.belong_class,
            identifier_name=identifier_name
        )

    def _get_runtime_class_by_member_select(self,
                                            runtime_method: RuntimeMethod,
                                            namespace: NameSpace,
                                            member_select_node: ast.MemberSelect) -> Optional[ast.Tree]:
        """根据当前方法中的 MemberSelect 节点构造 RuntimeClass 对象"""

        # 获取 name1 的类型
        runtime_class = self.infer_runtime_class_by_node(runtime_method, namespace, member_select_node.expression)

        # 全局搜索类属性的类型
        runtime_variable = RuntimeVariable(
            belong_class=runtime_class,
            variable_name=member_select_node.identifier.name
        )

        return self._project_context.get_type_node_by_runtime_variable(runtime_variable)

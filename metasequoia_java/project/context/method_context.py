"""
方法上下文
"""

from typing import Generator, List, Optional

from metasequoia_java import ast
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
    def create_by_method_name(class_context: ClassContextBase, method_name: str) -> Optional["MethodContext"]:
        # 如果方法名和类名一样，则说明方法为初始化方法，将方法名改为 init
        if method_name == class_context.class_name:
            method_name = "init"

        method_node = class_context.get_method_node_by_name(method_name)
        if method_node is None:
            print(f"找不到方法: {class_context.get_runtime_class().absolute_name}.{method_name}")
            return None

        return MethodContext(
            project_context=class_context.project_context,
            file_context=class_context.file_context,
            class_context=class_context,
            method_name=method_name,
            method_node=method_node
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
            belong_class=self._class_context.get_runtime_class(),
            method_name=self._method_name
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
                              namespace: NameSpace,
                              statement_node: ast.Tree
                              ) -> Generator[RuntimeMethod, None, None]:
        """获取当前表达式中调用的方法

        适配场景：
        `name1()`
        `name1.name2()`
        `name1.name2.name3()`：依赖泛型解析器，获取 `name2` 的类型
        `name1().name2()` 或 `name1.name2().name3()`：依赖泛型管理器，获取 `name1()` 的类型
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

            # name1() -- 调用当前类的其他方法
            if isinstance(method_select, ast.Identifier):
                yield RuntimeMethod(
                    belong_class=RuntimeClass(
                        package_name=self._file_context.package_name,
                        class_name=self._class_context.class_name,
                        type_arguments=None  # TODO 待改为当前类构造时的泛型
                    ),
                    method_name=method_select.name
                )

            # name1.name2() / name1.name2.name3() / name1().name2() / name1.name2().name3()
            elif isinstance(method_select, ast.MemberSelect):
                expression = method_select.expression
                runtime_class = self.get_runtime_class_by_node(namespace, expression)
                yield RuntimeMethod(
                    belong_class=runtime_class,
                    method_name=method_select.identifier.name
                )
                yield from self.get_method_invocation(namespace, expression)

            else:
                print(f"get_method_invocation, 暂不支持的表达式类型: {statement_node}")

            # 递归处理方法参数
            for argument in statement_node.arguments:
                yield from self.get_method_invocation(namespace, argument)

            return

        if isinstance(statement_node, ast.NewClass):
            identifier = statement_node.identifier
            if isinstance(identifier, ast.Identifier):
                method_class_name = identifier.name
                method_package_name = self.file_context.get_import_package_name_by_class_name(method_class_name)
                yield RuntimeMethod(
                    belong_class=RuntimeClass(package_name=method_package_name, class_name=method_class_name,
                                              type_arguments=None),
                    method_name=method_class_name
                )
            elif isinstance(identifier, ast.ParameterizedType):
                identifier_type_name = identifier.type_name
                assert isinstance(identifier_type_name, ast.Identifier)
                method_class_name = identifier_type_name.name
                method_package_name = self._file_context.get_import_package_name_by_class_name(method_class_name)
                type_arguments = [
                    self.get_runtime_class_by_node(namespace, type_argument)
                    for type_argument in identifier.type_arguments
                ]
                yield RuntimeMethod(
                    belong_class=RuntimeClass(package_name=method_package_name, class_name=method_class_name,
                                              type_arguments=type_arguments),
                    method_name=method_class_name
                )
            else:
                print("NewClass 暂不支持的类型: ", identifier)

            # 递归处理方法参数
            for argument in statement_node.arguments:
                yield from self.get_method_invocation(namespace, argument)

            return

        # -------------------- 其他递归条件 --------------------
        if isinstance(statement_node, ast.InstanceOf):
            yield from self.get_method_invocation(namespace, statement_node.expression)
            yield from self.get_method_invocation(namespace, statement_node.instance_type)
            yield from self.get_method_invocation(namespace, statement_node.pattern)
        elif isinstance(statement_node, ast.TypeCast):
            yield from self.get_method_invocation(namespace, statement_node.cast_type)
            yield from self.get_method_invocation(namespace, statement_node.expression)
        elif isinstance(statement_node, (ast.Break, ast.Continue)):
            return  # break 语句中和 contain 语句中不会调用其他方法
        elif isinstance(statement_node, ast.Throw):
            yield from self.get_method_invocation(namespace, statement_node.expression)
        elif isinstance(statement_node, ast.Variable):
            yield from self.get_method_invocation(namespace, statement_node.initializer)
        elif isinstance(statement_node, ast.MemberSelect):
            yield from self.get_method_invocation(namespace, statement_node.expression)
        elif isinstance(statement_node, ast.ExpressionStatement):
            yield from self.get_method_invocation(namespace, statement_node.expression)
        elif isinstance(statement_node, ast.Assignment):
            yield from self.get_method_invocation(namespace, statement_node.expression)
        elif isinstance(statement_node, ast.If):
            yield from self.get_method_invocation(namespace, statement_node.condition)
            yield from self.get_method_invocation(namespace, statement_node.then_statement)
            yield from self.get_method_invocation(namespace, statement_node.else_statement)
        elif isinstance(statement_node, ast.Block):
            namespace.add_space(SimpleNameSpace.create_by_statements(statement_node.statements))
            for sub_node in statement_node.statements:
                yield from self.get_method_invocation(namespace, sub_node)
            namespace.pop_space()
        elif isinstance(statement_node, ast.Parenthesized):
            yield from self.get_method_invocation(namespace, statement_node.expression)
        elif isinstance(statement_node, ast.ArrayAccess):
            yield from self.get_method_invocation(namespace, statement_node.expression)
            yield from self.get_method_invocation(namespace, statement_node.index)
        elif isinstance(statement_node, ast.Binary):
            yield from self.get_method_invocation(namespace, statement_node.left_operand)
            yield from self.get_method_invocation(namespace, statement_node.right_operand)
        elif isinstance(statement_node, ast.Return):
            yield from self.get_method_invocation(namespace, statement_node.expression)
        elif isinstance(statement_node, ast.ConditionalExpression):
            yield from self.get_method_invocation(namespace, statement_node.condition)
            yield from self.get_method_invocation(namespace, statement_node.true_expression)
            yield from self.get_method_invocation(namespace, statement_node.false_expression)
        elif isinstance(statement_node, ast.EnhancedForLoop):
            namespace.add_space(SimpleNameSpace.create_by_variable(statement_node.variable))
            yield from self.get_method_invocation(namespace, statement_node.variable)
            yield from self.get_method_invocation(namespace, statement_node.expression)
            yield from self.get_method_invocation(namespace, statement_node.statement)
            namespace.pop_space()
        elif isinstance(statement_node, ast.Unary):
            yield from self.get_method_invocation(namespace, statement_node.expression)
        elif isinstance(statement_node, ast.Try):
            yield from self.get_method_invocation(namespace, statement_node.block)
            for sub_node in statement_node.catches:
                yield from self.get_method_invocation(namespace, sub_node)
            yield from self.get_method_invocation(namespace, statement_node.finally_block)
            for sub_node in statement_node.resources:
                yield from self.get_method_invocation(namespace, sub_node)
        elif isinstance(statement_node, ast.Catch):
            yield from self.get_method_invocation(namespace, statement_node.parameter)
            yield from self.get_method_invocation(namespace, statement_node.block)
        elif isinstance(statement_node, ast.Switch):
            yield from self.get_method_invocation(namespace, statement_node.expression)
            for case_node in statement_node.cases:
                yield from self.get_method_invocation(namespace, case_node)
        elif isinstance(statement_node, ast.Case):
            if statement_node.expressions is not None:
                for sub_node in statement_node.expressions:
                    yield from self.get_method_invocation(namespace, sub_node)
            for sub_node in statement_node.labels:
                yield from self.get_method_invocation(namespace, sub_node)
            yield from self.get_method_invocation(namespace, statement_node.guard)
            for sub_node in statement_node.statements:
                yield from self.get_method_invocation(namespace, sub_node)
            yield from self.get_method_invocation(namespace, statement_node.body)
        elif isinstance(statement_node, ast.PatternCaseLabel):
            yield from self.get_method_invocation(namespace, statement_node.pattern)
        elif isinstance(statement_node, ast.ConstantCaseLabel):
            yield from self.get_method_invocation(namespace, statement_node.expression)
        elif isinstance(statement_node, ast.DefaultCaseLabel):
            return  # switch 语句的 default 子句不会调用其他方法
        elif isinstance(statement_node, ast.ForLoop):
            namespace.add_space(SimpleNameSpace.create_by_statements(statement_node.initializer))
            for sub_node in statement_node.initializer:
                yield from self.get_method_invocation(namespace, sub_node)
            yield from self.get_method_invocation(namespace, statement_node.condition)
            for sub_node in statement_node.update:
                yield from self.get_method_invocation(namespace, sub_node)
            yield from self.get_method_invocation(namespace, statement_node.statement)
            namespace.pop_space()
        elif isinstance(statement_node, ast.PrimitiveType):
            return  # 原生类型中不会调用其他方法
        elif isinstance(statement_node, ast.LambdaExpression):
            for sub_node in statement_node.parameters:
                yield from self.get_method_invocation(namespace, sub_node)
            yield from self.get_method_invocation(namespace, statement_node.body)
        elif isinstance(statement_node, ast.WhileLoop):
            yield from self.get_method_invocation(namespace, statement_node.condition)
            yield from self.get_method_invocation(namespace, statement_node.statement)
        elif isinstance(statement_node, ast.NewArray):
            yield from self.get_method_invocation(namespace, statement_node.array_type)
            for sub_node in statement_node.dimensions:
                yield from self.get_method_invocation(namespace, sub_node)
            for sub_node in statement_node.initializers:
                yield from self.get_method_invocation(namespace, sub_node)
            if statement_node.annotations is not None:
                for sub_node in statement_node.annotations:
                    yield from self.get_method_invocation(namespace, sub_node)
            if statement_node.dim_annotations is not None:
                for node_list in statement_node.dim_annotations:
                    for sub_node in node_list:
                        yield from self.get_method_invocation(namespace, sub_node)
        elif isinstance(statement_node, ast.MemberReference):
            yield from self.get_method_invocation(namespace, statement_node.expression)
            for sub_node in statement_node.type_arguments:
                yield from self.get_method_invocation(namespace, sub_node)
        elif isinstance(statement_node, ast.CompoundAssignment):
            yield from self.get_method_invocation(namespace, statement_node.variable)
            yield from self.get_method_invocation(namespace, statement_node.expression)
        else:
            print(f"get_method_invocation: 未知表达式类型: {statement_node}")
            yield None

    # ------------------------------ 类型获取处理器 ------------------------------

    def get_runtime_class_by_node(self,
                                  namespace: NameSpace,
                                  expression_node: ast.Tree) -> Optional[RuntimeClass]:
        """获取当前类中节点元素的类型"""
        # name1
        if isinstance(expression_node, ast.Identifier):
            return self._get_runtime_class_by_identifier_node(namespace, expression_node)

        # name1.name2：如果 name1 为项目外元素，则可能无法获取
        elif isinstance(expression_node, ast.MemberSelect):
            return self._get_runtime_class_by_member_select(namespace, expression_node)

        # name1().name2()
        elif isinstance(expression_node, ast.MethodInvocation):

            # 获取 name1 的类型
            method_select_node = expression_node.method_select
            # name1() -- 调用当前类的其他方法
            if isinstance(method_select_node, ast.Identifier):
                runtime_method = RuntimeMethod(
                    belong_class=RuntimeClass(
                        package_name=self._file_context.package_name,
                        class_name=self._class_context.class_name,
                        type_arguments=None  # TODO 待改为当前类构造时的泛型
                    ),
                    method_name=method_select_node.name
                )

            # name1.name2() / name1.name2.name3() / name1().name2() / name1.name2().name3()
            elif isinstance(method_select_node, ast.MemberSelect):
                expression = method_select_node.expression
                runtime_class = self.get_runtime_class_by_node(namespace, expression)
                runtime_method = RuntimeMethod(
                    belong_class=runtime_class,
                    method_name=method_select_node.identifier.name
                )

            else:
                print(f"get_runtime_class_by_node: 未知的类型 {expression_node}")
                return None

            return self._project_context.get_runtime_class_by_runtime_method_return_type(runtime_method)

        # 括号表达式
        elif isinstance(expression_node, ast.Parenthesized):
            return self.get_runtime_class_by_node(namespace, expression_node.expression)

        # 强制类型转换表达式
        elif isinstance(expression_node, ast.TypeCast):
            return self.get_runtime_class_by_node(namespace, expression_node.expression)

        # 字符串字面值
        elif isinstance(expression_node, ast.StringLiteral):
            return RuntimeClass(
                package_name="java.lang",
                class_name="String",
                type_arguments=[]
            )

        else:
            print(f"get_runtime_class_by_node: 暂不支持的表达式 {expression_node}")

    def _get_runtime_class_by_identifier_node(self,
                                              namespace: NameSpace,
                                              identifier_node: ast.Identifier
                                              ) -> RuntimeClass:
        """根据当前方法中的 Identifier 节点中构造 RuntimeClass 对象"""
        unknown_name = identifier_node.name

        # 标识符是变量名
        if namespace.has_name(unknown_name):
            return self.file_context.get_runtime_class_by_type_node(
                class_node=self.class_context.class_node,
                runtime_class=self.class_context.get_runtime_class(),  # TODO 待考虑当前类的泛型
                type_node=namespace.get_name(unknown_name)
            )

        # 标识符是类名
        return RuntimeClass(
            package_name=self.file_context.get_import_package_name_by_class_name(unknown_name),
            class_name=unknown_name,
            type_arguments=[]
        )

    def _get_runtime_class_by_member_select(self,
                                            namespace: NameSpace,
                                            member_select_node: ast.MemberSelect) -> Optional[ast.Tree]:
        """根据当前方法中的 MemberSelect 节点构造 RuntimeClass 对象"""

        # 获取 name1 的类型
        runtime_class = self.get_runtime_class_by_node(namespace, member_select_node.expression)

        # 全局搜索类属性的类型
        runtime_variable = RuntimeVariable(
            belong_class=runtime_class,
            variable_name=member_select_node.identifier.name
        )

        return self._project_context.get_type_node_by_runtime_variable(runtime_variable)

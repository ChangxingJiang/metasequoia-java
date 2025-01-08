import abc
import dataclasses
from typing import List, Optional

from metasequoia_java.ast.base import CaseLabelTree
from metasequoia_java.ast.base import DirectiveTree
from metasequoia_java.ast.base import ExpressionTree
from metasequoia_java.ast.base import PatternTree
from metasequoia_java.ast.base import StatementTree
from metasequoia_java.ast.base import Tree
from metasequoia_java.ast.constants import CaseKind
from metasequoia_java.ast.constants import IntegerStyle
from metasequoia_java.ast.constants import LambdaBodyKind
from metasequoia_java.ast.constants import ModuleKind
from metasequoia_java.ast.constants import ReferenceMode
from metasequoia_java.ast.constants import StringStyle
from metasequoia_java.ast.element import Modifier
from metasequoia_java.ast.element import TypeKind
from metasequoia_java.ast.generate_utils import Separator, change_int_to_string, generate_enum_list, generate_tree_list
from metasequoia_java.ast.kind import TreeKind
from metasequoia_java.tool import NameSpace

__all__ = [
    "AnnotatedTypeTree",  # 包含注解的类型
    "AnnotationTree",  # 注解
    "AnyPatternTree",  # 【JDK 22+】
    "ArrayAccessTree",  # 访问数组中元素
    "ArrayTypeTree",  # 数组类型
    "AssertTree",  # assert 语句
    "AssignmentTree",  # 赋值表达式
    "BinaryTree",  # 二元表达式
    "BindingPatternTree",  # 【JDK 16+】
    "BlockTree",  # 代码块
    "BreakTree",  # break 语句
    "CaseTree",  # switch 语句或表达式中的 case 子句
    "CatchTree",  # try 语句中的 catch 代码块
    "ClassTree",  # 类（class）、接口（interface）、枚举类（enum）、记录类（record）或注解类（annotation type）的声明语句
    "CompilationUnitTree",  # 表示普通编译单元和模块化编译单元的抽象语法树节点
    "CompoundAssignmentTree",  # 赋值表达式
    "ConditionalExpressionTree",  # 三目表达式
    "ConstantCaseLabelTree",  #
    "ContinueTree",  # continue 语句
    "DeconstructionPatternTree",  # 【JDK 21+】
    "DefaultCaseLabelTree",  # 【JDK 21+】
    "DoWhileLoopTree",  # do while 语句【JDK 21+】
    "EmptyStatementTree",  # 空语句
    "EnhancedForLoopTree",  # 增强 for 循环语句
    "ErroneousTree",
    "ExportsTree",  # 模块声明语句中的 exports 指令【JDK 9+】
    "ExpressionStatementTree",  # 表达式语句
    "ForLoopTree",  # for 循环语句
    "IdentifierTree",  # 标识符
    "IfTree",  # if 语句
    "ImportTree",  # 声明引用
    "InstanceOfTree",  # instanceof 表达式
    "IntersectionTypeTree",  # 强制类型转换表达式中的交叉类型
    "LabeledStatementTree",  # 包含标签的表达式
    "LambdaExpressionTree",  # lambda 表达式
    "LiteralTree",  # 字面值
    "IntLiteralTree",  # 整型字面值（包括十进制、八进制、十六进制）
    "LongLiteralTree",  # 十进制长整型字面值（包括十进制、八进制、十六进制）
    "FloatLiteralTree",  # 单精度浮点数字面值
    "DoubleLiteralTree",  # 双精度浮点数字面值
    "TrueLiteralTree",  # 布尔值真值字面值
    "FalseLiteralTree",  # 布尔值假值字面值
    "CharacterLiteralTree",  # 字符字面值
    "StringLiteralTree",  # 字符串字面值
    "NullLiteralTree",  # 空值字面值
    "MemberReferenceTree",  # 成员引用表达式
    "MemberSelectTree",  # 成员访问表达式
    "MethodInvocationTree",  # 方法调用表达式
    "MethodTree",  # 声明方法或注解类型元素
    "ModifiersTree",  # 用于声明表达式的修饰符，包括注解
    "ModuleTree",  # 声明模块【JDK 9+】
    "NewArrayTree",  # 初始化数组表达式
    "NewClassTree",  # 实例化类表达式
    "OpensTree",  # 模块声明中的 opens 指令
    "PackageTree",  # 声明包【JDK 9+】
    "ParameterizedTypeTree",  # 包含类型参数的类型表达式
    "ParenthesizedTree",  # 括号表达式
    "PatternCaseLabelTree",  # 【JDK 21+】
    "PrimitiveTypeTree",  # 原生类型
    "ProvidesTree",  # 模块声明语句的 provides 指令【JDK 9+】
    "RequiresTree",  # 模块声明语句中的 requires 指令【JDK 9+】
    "ReturnTree",  # 返回语句
    "SwitchExpressionTree",  # switch 表达式【JDK 14+】
    "SwitchTree",  # switch 语句
    "SynchronizedTree",  # 同步代码块语句
    "ThrowTree",  # throw 语句
    "TryTree",  # try 语句
    "TypeCastTree",  # 强制类型转换表达式
    "TypeParameterTree",  # 类型参数列表
    "UnaryTree",  # 一元表达式
    "UnionTypeTree",  #
    "UsesTree",  # 模块声明语句中的 uses 指令【JDK 9+】
    "VariableTree",  # 声明变量
    "WhileLoopTree",  # while 循环语句
    "WildcardTree",  # 通配符
    "YieldTree",  # yield 语句
]


@dataclasses.dataclass(slots=True)
class DefaultCaseLabelTree(CaseLabelTree):
    """【JDK 21+】TODO 名称待整理

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/DefaultCaseLabelTree.java
    A case label that marks `default` in `case null, default`.
    """

    @staticmethod
    def create(start_pos: int, end_pos: int, source: str) -> "DefaultCaseLabelTree":
        return DefaultCaseLabelTree(
            kind=TreeKind.DEFAULT_CASE_LABEL,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        """TODO"""


@dataclasses.dataclass(slots=True)
class AnnotationTree(ExpressionTree):
    """注解

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/AnnotationTree.java
    A tree node for an annotation.

    样例：
    - @annotationType
    - @annotationType ( arguments )
    """

    annotation_type: Tree = dataclasses.field(kw_only=True)
    arguments: List[ExpressionTree] = dataclasses.field(kw_only=True)

    @staticmethod
    def create_annotation(annotation_type: Tree,
                          arguments: List[ExpressionTree],
                          start_pos: int, end_pos: int, source: str) -> "AnnotationTree":
        return AnnotationTree(
            kind=TreeKind.ANNOTATION,
            annotation_type=annotation_type,
            arguments=arguments,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    @staticmethod
    def create_type_annotation(annotation_type: Tree,
                               arguments: List[ExpressionTree],
                               start_pos: int, end_pos: int, source: str) -> "AnnotationTree":
        return AnnotationTree(
            kind=TreeKind.TYPE_ANNOTATION,
            annotation_type=annotation_type,
            arguments=arguments,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        if len(self.arguments) > 0:
            return f"@{self.annotation_type.generate()}({generate_tree_list(self.arguments, Separator.COMMA)})"
        return f"@{self.annotation_type.generate()}"


@dataclasses.dataclass(slots=True)
class AnnotatedTypeTree(ExpressionTree):
    """包含注解的类型

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/AnnotatedTypeTree.java
    A tree node for an annotated type.

    样例：
    - @annotationType String
    - @annotationType ( arguments ) Date
    """

    annotations: List[AnnotationTree] = dataclasses.field(kw_only=True)
    underlying_type: ExpressionTree = dataclasses.field(kw_only=True)

    @staticmethod
    def create(annotations: List[AnnotationTree], underlying_type: ExpressionTree,
               start_pos: int, end_pos: int, source: str) -> "AnnotatedTypeTree":
        return AnnotatedTypeTree(
            kind=TreeKind.ANNOTATION_TYPE,
            annotations=annotations,
            underlying_type=underlying_type,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        return f"{generate_tree_list(self.annotations, Separator.SPACE)} {self.underlying_type.generate()}"


@dataclasses.dataclass(slots=True)
class AnyPatternTree(PatternTree):
    """【JDK 22+】TODO 名称待整理

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/AnyPatternTree.java
    A tree node for a binding pattern that matches a pattern with a variable of any name and a type of the match
    candidate; an unnamed pattern.

    使用下划线 `_` 的样例：
    if (r instanceof R(_)) {}
    """

    @staticmethod
    def create(start_pos: int, end_pos: int, source: str) -> "AnyPatternTree":
        return AnyPatternTree(
            kind=TreeKind.ANY_PATTERN,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    @staticmethod
    def mock() -> "AnyPatternTree":
        return AnyPatternTree(
            kind=TreeKind.ANY_PATTERN,
            start_pos=None,
            end_pos=None,
            source=None
        )

    def generate(self) -> str:
        """TODO"""


@dataclasses.dataclass(slots=True)
class ArrayAccessTree(ExpressionTree):
    """访问数组中元素

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/ArrayAccessTree.java
    A tree node for an array access expression.

    样例：
    - expression[index]
    """

    expression: ExpressionTree = dataclasses.field(kw_only=True)
    index: ExpressionTree = dataclasses.field(kw_only=True)

    @staticmethod
    def create(expression: ExpressionTree, index: ExpressionTree,
               start_pos: int, end_pos: int, source: str) -> "ArrayAccessTree":
        return ArrayAccessTree(
            kind=TreeKind.ARRAY_ACCESS,
            expression=expression,
            index=index,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        return f"{self.expression.generate()}[{self.index.generate()}]"


@dataclasses.dataclass(slots=True)
class ArrayTypeTree(ExpressionTree):
    """数组类型

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/ArrayTypeTree.java
    A tree node for an array type.

    样例：
    - type[]
    """

    expression: ExpressionTree = dataclasses.dataclass(slots=True)

    @staticmethod
    def create(expression: ExpressionTree,
               start_pos: int, end_pos: int, source: str) -> "ArrayTypeTree":
        return ArrayTypeTree(
            kind=TreeKind.ARRAY_TYPE,
            expression=expression,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        return f"{self.expression.generate()}[]"


@dataclasses.dataclass(slots=True)
class AssertTree(StatementTree):
    """assert 语句

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/AssertTree.java
    A tree node for an `assert` statement.

    样例：
    - assert condition ;
    - assert condition : detail ;
    """

    assertion: ExpressionTree = dataclasses.field(kw_only=True)
    message: Optional[ExpressionTree] = dataclasses.field(kw_only=True)

    @staticmethod
    def create(assertion: ExpressionTree,
               message: Optional[ExpressionTree],
               start_pos: int, end_pos: int, source: str) -> "AssertTree":
        return AssertTree(
            kind=TreeKind.ASSERT,
            assertion=assertion,
            message=message,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        if self.message is not None:
            return f"assert {self.assertion.generate()} : {self.message.generate()} ;"
        return f"assert {self.assertion.generate()} ;"


@dataclasses.dataclass(slots=True)
class AssignmentTree(ExpressionTree):
    """赋值表达式

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/AssignmentTree.java
    A tree node for an assignment expression.

    样例：
    - variable = expression
    """

    variable: ExpressionTree = dataclasses.field(kw_only=True)
    expression: ExpressionTree = dataclasses.field(kw_only=True)

    @staticmethod
    def create(variable: ExpressionTree,
               expression: ExpressionTree,
               start_pos: int, end_pos: int, source: str) -> "AssignmentTree":
        return AssignmentTree(
            kind=TreeKind.ASSIGNMENT,
            variable=variable,
            expression=expression,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        return f"{self.variable.generate()} = {self.expression.generate()}"


@dataclasses.dataclass(slots=True)
class BinaryTree(ExpressionTree):
    """二元表达式

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/BinaryTree.java
    A tree node for a binary expression.
    Use `getKind` to determine the kind of operator.

    样例：
    - leftOperand operator rightOperand
    """

    left_operand: ExpressionTree = dataclasses.field(kw_only=True)
    right_operand: ExpressionTree = dataclasses.field(kw_only=True)

    @staticmethod
    def create(start_pos: int, end_pos: int, source: str,
               kind: TreeKind,
               left_operand: ExpressionTree,
               right_operand: ExpressionTree) -> "BinaryTree":
        return BinaryTree(
            kind=kind,
            left_operand=left_operand,
            right_operand=right_operand,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        """TODO"""


@dataclasses.dataclass(slots=True)
class ModifiersTree(Tree):
    """用于声明表达式的修饰符，包括注解

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/ModifiersTree.java
    A tree node for the modifiers, including annotations, for a declaration.

    样例：
    - flags
    - flags annotations
    """

    flags: List[Modifier] = dataclasses.field(kw_only=True)
    annotations: List[AnnotationTree] = dataclasses.field(kw_only=True)

    @staticmethod
    def create(flags: List[Modifier],
               annotations: Optional[List[AnnotationTree]],
               start_pos: int, end_pos: int, source: str) -> "ModifiersTree":
        if annotations is None:
            annotations = []
        return ModifiersTree(
            kind=TreeKind.MODIFIERS,
            flags=flags,
            annotations=annotations,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    @staticmethod
    def create_empty() -> "ModifiersTree":
        """创建没有任何修饰符的 ModifiersTree 节点，且该节点没有实际的位置和代码"""
        return ModifiersTree(
            kind=TreeKind.MODIFIERS,
            flags=[],
            annotations=[],
            start_pos=None,
            end_pos=None,
            source=None
        )

    @staticmethod
    def mock() -> "ModifiersTree":
        return ModifiersTree(
            kind=TreeKind.MODIFIERS,
            flags=[],
            annotations=[],
            start_pos=None,
            end_pos=None,
            source=None
        )

    @property
    def actual_flags(self):
        """不包含虚拟修饰符的修饰符列表"""
        return [flag for flag in self.flags if not flag.is_virtual()]

    def generate(self) -> str:
        if len(self.annotations) > 0:
            return (f"{generate_enum_list(self.actual_flags, Separator.SPACE)} "
                    f"{generate_tree_list(self.annotations, Separator.SPACE)}")
        return f"{generate_enum_list(self.actual_flags, Separator.SPACE)}"


@dataclasses.dataclass(slots=True)
class VariableTree(StatementTree):
    """声明变量

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/VariableTree.java
    A tree node for a variable declaration.

    样例：
    - modifiers type name initializer ;
    - modifiers type qualified-name.this
    """

    modifiers: ModifiersTree = dataclasses.field(kw_only=True)
    name: Optional[str] = dataclasses.field(kw_only=True, default=None)
    name_expression: Optional[ExpressionTree] = dataclasses.field(kw_only=True, default=None)
    variable_type: Tree = dataclasses.field(kw_only=True)
    initializer: Optional[ExpressionTree] = dataclasses.field(kw_only=True)

    @staticmethod
    def create_by_name(modifiers: ModifiersTree,
                       name: Optional[str],
                       variable_type: Tree,
                       initializer: Optional[ExpressionTree],
                       start_pos: int, end_pos: int, source: str) -> "VariableTree":
        return VariableTree(
            kind=TreeKind.VARIABLE,
            modifiers=modifiers,
            name=name,
            variable_type=variable_type,
            initializer=initializer,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    @staticmethod
    def create_by_name_expression(modifiers: ModifiersTree, name_expression: Optional[ExpressionTree],
                                  variable_type: Tree,
                                  start_pos: int, end_pos: int, source: str) -> "VariableTree":
        return VariableTree(
            kind=TreeKind.VARIABLE,
            modifiers=modifiers,
            name_expression=name_expression,
            variable_type=variable_type,
            initializer=None,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        """TODO"""


@dataclasses.dataclass(slots=True)
class BindingPatternTree(PatternTree):
    """【JDK 16+】TODO 名称待整理

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/BindingPatternTree.java
    A binding pattern tree
    """

    variable: VariableTree = dataclasses.field(kw_only=True)

    @staticmethod
    def create(variable: VariableTree, start_pos: int, end_pos: int, source: str) -> "BindingPatternTree":
        return BindingPatternTree(
            kind=TreeKind.VARIABLE,
            variable=variable,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        """TODO"""


@dataclasses.dataclass(slots=True)
class BlockTree(StatementTree):
    """代码块

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/BlockTree.java
    A tree node for a statement block.

    样例：
    - { }
    - { statements }
    - static { statements }
    """

    is_static: bool = dataclasses.field(kw_only=True)
    statements: List[StatementTree] = dataclasses.field(kw_only=True)

    @staticmethod
    def create(is_static: bool, statements: List[StatementTree], start_pos: int, end_pos: int,
               source: str) -> "BlockTree":
        return BlockTree(
            kind=TreeKind.BLOCK,
            is_static=is_static,
            statements=statements,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    @staticmethod
    def mock() -> "BlockTree":
        return BlockTree(
            kind=TreeKind.BLOCK,
            is_static=False,
            statements=[],
            start_pos=None,
            end_pos=None,
            source=None
        )

    def generate(self) -> str:
        static_str = "static " if self.is_static is True else ""
        return f"{static_str}{{{generate_tree_list(self.statements, Separator.SEMI)}}}"


@dataclasses.dataclass(slots=True)
class BreakTree(StatementTree):
    """break 语句

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/BreakTree.java
    A tree node for a `break` statement.

    样例：
    - break;
    - break label ;
    """

    label: Optional[str] = dataclasses.field(kw_only=True)

    @staticmethod
    def create(label: Optional[str],
               start_pos: int, end_pos: int, source: str) -> "BreakTree":
        return BreakTree(
            kind=TreeKind.BREAK,
            label=label,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        if self.label is None:
            return "break;"
        return f"break {self.label};"


@dataclasses.dataclass(slots=True)
class CaseTree(Tree):
    """switch 语句或表达式中的 case 子句

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/CaseTree.java
    A tree node for a `case` in a `switch` statement or expression.

    样例：
    case expression :
        statements
    default :
        statements
    """

    expressions: Optional[List[ExpressionTree]] = dataclasses.field(kw_only=True, default=None)  # @Deprecated
    labels: List[CaseLabelTree] = dataclasses.field(kw_only=True)  # 【JDK 21+】
    guard: ExpressionTree = dataclasses.field(kw_only=True)  # 【JDK 21+】
    statements: List[StatementTree] = dataclasses.field(kw_only=True)
    body: Optional[Tree] = dataclasses.field(kw_only=True)  # 【JDK 14+】
    case_kind: CaseKind = dataclasses.field(kw_only=True)  # 【JDK 14+】

    @staticmethod
    def create_rule(start_pos: int, end_pos: int, source: str,
                    labels: List[CaseLabelTree], guard: ExpressionTree,
                    statements: List[StatementTree], body: Optional[Tree]) -> "CaseTree":
        return CaseTree(
            kind=TreeKind.CASE,
            labels=labels,
            guard=guard,
            statements=statements,
            body=body,
            case_kind=CaseKind.RULE,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    @staticmethod
    def create_statement(start_pos: int, end_pos: int, source: str,
                         labels: List[CaseLabelTree], guard: ExpressionTree,
                         statements: List[StatementTree], body: Optional[Tree]) -> "CaseTree":
        return CaseTree(
            kind=TreeKind.CASE,
            labels=labels,
            guard=guard,
            statements=statements,
            body=body,
            case_kind=CaseKind.STATEMENT,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        """TODO"""


@dataclasses.dataclass(slots=True)
class CatchTree(Tree):
    """try 语句中的 catch 代码块

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/CatchTree.java
    A tree node for a `catch` block in a `try` statement.

    样例：
    catch ( parameter )
        block
    """

    parameter: VariableTree = dataclasses.field(kw_only=True)
    block: BlockTree = dataclasses.field(kw_only=True)

    @staticmethod
    def create(parameter: VariableTree,
               block: BlockTree,
               start_pos: int, end_pos: int, source: str) -> "CatchTree":
        return CatchTree(
            kind=TreeKind.CATCH,
            parameter=parameter,
            block=block,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        return f"catch ({self.parameter.generate()}) {self.block.generate()}"


@dataclasses.dataclass(slots=True)
class IdentifierTree(ExpressionTree):
    """标识符

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/IdentifierTree.java
    A tree node for an identifier expression.

    样例：name
    """

    name: str = dataclasses.field(kw_only=True)

    @staticmethod
    def create(name: str, start_pos: int, end_pos: int, source: str) -> "IdentifierTree":
        return IdentifierTree(
            kind=TreeKind.IDENTIFIER,
            name=name,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    @staticmethod
    def mock(name: str) -> "IdentifierTree":
        return IdentifierTree(
            kind=TreeKind.IDENTIFIER,
            name=name,
            start_pos=None,
            end_pos=None,
            source=None
        )

    def generate(self) -> str:
        return self.name


@dataclasses.dataclass(slots=True)
class TypeParameterTree(Tree):
    """类型参数列表

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/TypeParameterTree.java
    A tree node for a type parameter.

    样例：
    - name
    - name extends bounds
    - annotations name
    """

    name: str = dataclasses.field(kw_only=True)
    bounds: List[Tree] = dataclasses.field(kw_only=True)
    annotations: List[AnnotationTree] = dataclasses.field(kw_only=True)

    @staticmethod
    def create(name: str, bounds: List[Tree], annotations: List[AnnotationTree],
               start_pos: int, end_pos: int, source: str) -> "TypeParameterTree":
        return TypeParameterTree(
            kind=TreeKind.TYPE_PARAMETER,
            name=name,
            bounds=bounds,
            annotations=annotations,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        """TODO"""


@dataclasses.dataclass(slots=True)
class ClassTree(StatementTree):
    """类（class）、接口（interface）、枚举类（enum）、记录类（record）或注解类（annotation type）的声明语句

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/ClassTree.java
    A tree node for a class, interface, enum, record, or annotation type declaration.

    样例：
    modifiers class simpleName typeParameters
        extends extendsClause
        implements implementsClause
    {
        members
    }
    """

    modifiers: ModifiersTree = dataclasses.field(kw_only=True)
    name: Optional[str] = dataclasses.field(kw_only=True)  # 如果为匿名类则为 None
    type_parameters: List[TypeParameterTree] = dataclasses.field(kw_only=True)
    extends_clause: Optional[Tree] = dataclasses.field(kw_only=True)  # 如果没有继承关系则为 None
    implements_clause: List[Tree] = dataclasses.field(kw_only=True)
    permits_clause: Optional[List[Tree]] = dataclasses.field(kw_only=True)  # 【JDK 17+】
    members: List[Tree] = dataclasses.field(kw_only=True)

    @staticmethod
    def create(modifiers: ModifiersTree,
               name: str,
               type_parameters: List[TypeParameterTree],
               extends_clause: Optional[Tree],
               implements_clause: List[Tree],
               permits_clause: Optional[List[Tree]],
               members: List[Tree],
               start_pos: int, end_pos: int, source: str) -> "ClassTree":
        return ClassTree(
            kind=TreeKind.CLASS,
            modifiers=modifiers,
            name=name,
            type_parameters=type_parameters,
            extends_clause=extends_clause,
            implements_clause=implements_clause,
            permits_clause=permits_clause,
            members=members,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    @staticmethod
    def create_anonymous_class(modifiers: ModifiersTree,
                               members: List[Tree],
                               start_pos: int, end_pos: int, source: str) -> "ClassTree":
        return ClassTree(
            kind=TreeKind.CLASS,
            modifiers=modifiers,
            name=None,
            type_parameters=[],
            extends_clause=None,
            implements_clause=[],
            permits_clause=[],
            members=members,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        """TODO"""

    def get_method_by_name(self, method_name: str) -> Optional["MethodTree"]:
        """根据方法名获取 Method 对象"""
        for member in self.members:
            if isinstance(member, MethodTree) and member.name == method_name:
                return member
        return None

    def get_variable_list(self) -> List["VariableTree"]:
        """获取类属性的列表"""
        variable_list = []
        for member in self.members:
            if isinstance(member, VariableTree):
                variable_list.append(member)
        return variable_list

    def get_variable_namespace(self) -> NameSpace:
        name_space = NameSpace()
        for variable in self.get_variable_list():
            variable_name = variable.name
            class_name = variable.variable_type.generate()
            name_space.set_variable_info(variable_name, class_name)
        return name_space

@dataclasses.dataclass(slots=True)
class ModuleTree(Tree):
    """声明模块【JDK 9+】

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/ModuleTree.java
    A tree node for a module declaration.

    样例：
    annotations
    [open] module module-name {
        directives
    }
    """

    annotations: List[AnnotationTree] = dataclasses.field(kw_only=True)
    module_kind: ModuleKind = dataclasses.field(kw_only=True)
    name: ExpressionTree = dataclasses.field(kw_only=True)
    directives: List[DirectiveTree] = dataclasses.field(kw_only=True)

    @staticmethod
    def create(annotations: List[AnnotationTree],
               module_kind: ModuleKind,
               name: ExpressionTree,
               directives: List[DirectiveTree],
               start_pos: int, end_pos: int, source: str) -> "ModuleTree":
        return ModuleTree(
            kind=TreeKind.MODULE,
            annotations=annotations,
            module_kind=module_kind,
            name=name,
            directives=directives,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        """TODO"""


@dataclasses.dataclass(slots=True)
class PackageTree(Tree):
    """声明包【JDK 9+】

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/PackageTree.java
    Represents the package declaration.
    """

    annotations: List[AnnotationTree] = dataclasses.field(kw_only=True)
    package_name: ExpressionTree = dataclasses.field(kw_only=True)

    @staticmethod
    def create(annotations: List[AnnotationTree],
               package_name: ExpressionTree,
               start_pos: int, end_pos: int, source: str) -> "PackageTree":
        return PackageTree(
            kind=TreeKind.PACKAGE,
            annotations=annotations,
            package_name=package_name,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        """TODO"""


@dataclasses.dataclass(slots=True)
class ImportTree(Tree):
    """引入声明

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/ImportTree.java
    A tree node for an import declaration.

    样例：
    - import qualifiedIdentifier ;
    - import static qualifiedIdentifier ;
    """

    is_static: bool = dataclasses.field(kw_only=True)
    is_module: bool = dataclasses.field(kw_only=True)
    identifier: Tree = dataclasses.field(kw_only=True)

    @staticmethod
    def create(is_static: bool,
               is_module: bool,
               identifier: Tree,
               start_pos: int, end_pos: int, source: str) -> "ImportTree":
        return ImportTree(
            kind=TreeKind.IMPORT,
            is_static=is_static,
            is_module=is_module,
            identifier=identifier,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    @staticmethod
    def create_module(identifier: Tree,
                      start_pos: int, end_pos: int, source: str) -> "ImportTree":
        return ImportTree(
            kind=TreeKind.IMPORT,
            is_static=False,
            is_module=True,
            identifier=identifier,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        """TODO"""


@dataclasses.dataclass(slots=True)
class CompilationUnitTree(Tree):
    """表示普通编译单元和模块编译单元的抽象语法树节点

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/CompilationUnitTree.java
    Represents the abstract syntax tree for ordinary compilation units and modular compilation units.

    TODO 增加 sourceFile、LineMap 的属性
    """

    module: ModuleTree = dataclasses.field(kw_only=True)  # 【JDK 17+】
    package: PackageTree = dataclasses.field(kw_only=True)
    imports: List[ImportTree] = dataclasses.field(kw_only=True)
    type_declarations: List[Tree] = dataclasses.field(kw_only=True)

    @staticmethod
    def create(module: ModuleTree,
               package: PackageTree,
               imports: List[ImportTree],
               type_declarations: List[Tree],
               start_pos: int, end_pos: int, source: str) -> "CompilationUnitTree":
        return CompilationUnitTree(
            kind=TreeKind.COMPILATION_UNIT,
            module=module,
            package=package,
            imports=imports,
            type_declarations=type_declarations,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    @property
    def package_name(self) -> ExpressionTree:
        return self.package.package_name

    @property
    def package_annotations(self) -> List[AnnotationTree]:
        return self.package.annotations

    def generate(self) -> str:
        """TODO"""

    def get_public_class(self) -> Optional[ClassTree]:
        """获取文件中的公有类，如果没有则返回 None"""
        for class_declaration in self.get_class_declaration_list():
            if Modifier.PUBLIC in class_declaration.modifiers.flags:
                return class_declaration
        return None

    def get_class_declaration_list(self) -> List[ClassTree]:
        """获取文件中的类对象，如果没有则返回空列表"""
        class_declaration_list = []
        for declaration in self.type_declarations:
            if isinstance(declaration, ClassTree):
                class_declaration_list.append(declaration)
        return class_declaration_list

    def get_pure_namespace(self) -> NameSpace:
        """获取通过 import 生成的文件顶级命名空间，其中不包含 package 中其他类的名称"""
        name_space = NameSpace()
        for import_node in self.imports:
            full_name = import_node.identifier.generate()
            class_name = full_name[full_name.rindex(".") + 1:] if "." in full_name else full_name
            name_space.set_type_info(class_name, full_name)
        return name_space


@dataclasses.dataclass(slots=True)
class CompoundAssignmentTree(ExpressionTree):
    """赋值表达式

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/CompoundAssignmentTree.java
    A tree node for compound assignment operator.
    Use `getKind` to determine the kind of operator.

    样例：
    - variable operator expression
    """

    variable: ExpressionTree = dataclasses.field(kw_only=True)
    expression: ExpressionTree = dataclasses.field(kw_only=True)

    @staticmethod
    def create(kind: TreeKind,
               variable: ExpressionTree,
               expression: ExpressionTree,
               start_pos: int, end_pos: int, source: str) -> "CompoundAssignmentTree":
        return CompoundAssignmentTree(
            kind=kind,
            variable=variable,
            expression=expression,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        """TODO"""


@dataclasses.dataclass(slots=True)
class ConditionalExpressionTree(ExpressionTree):
    """三目表达式

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/ConditionalExpressionTree.java
    A tree node for the conditional operator `? :`.

    样例：condition ? trueExpression : falseExpression
    """

    condition: ExpressionTree = dataclasses.field(kw_only=True)
    true_expression: ExpressionTree = dataclasses.field(kw_only=True)
    false_expression: ExpressionTree = dataclasses.field(kw_only=True)

    @staticmethod
    def create(condition: ExpressionTree,
               true_expression: ExpressionTree,
               false_expression: ExpressionTree,
               start_pos: int, end_pos: int, source: str) -> "ConditionalExpressionTree":
        return ConditionalExpressionTree(
            kind=TreeKind.CONDITIONAL_EXPRESSION,
            condition=condition,
            true_expression=true_expression,
            false_expression=false_expression,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        return f"{self.condition.generate()} ? {self.true_expression.generate()} : {self.false_expression.generate()}"


@dataclasses.dataclass(slots=True)
class ConstantCaseLabelTree(CaseLabelTree):
    """TODO 名称待整理

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/ConstantCaseLabelTree.java
    A case label element that refers to a constant expression
    """

    expression: ExpressionTree = dataclasses.field(kw_only=True)

    @staticmethod
    def create(expression: ExpressionTree,
               start_pos: int, end_pos: int, source: str) -> "ConstantCaseLabelTree":
        return ConstantCaseLabelTree(
            kind=TreeKind.CONSTANT_CASE_LABEL,
            expression=expression,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        """TODO"""


@dataclasses.dataclass(slots=True)
class ContinueTree(StatementTree):
    """continue 语句

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/ContinueTree.java
    A tree node for a `continue` statement.

    样例：
    - continue ;
    - continue label ;
    """

    label: Optional[str] = dataclasses.field(kw_only=True)

    @staticmethod
    def create(label: Optional[str],
               start_pos: int, end_pos: int, source: str) -> "ContinueTree":
        return ContinueTree(
            kind=TreeKind.CONTINUE,
            label=label,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        if self.label is None:
            return "continue;"
        return f"continue {self.label};"


@dataclasses.dataclass(slots=True)
class DeconstructionPatternTree(PatternTree):
    """【JDK 21+】TODO 名称待整理

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/DeconstructionPatternTree.java#L35
    A deconstruction pattern tree.
    """

    deconstructor: ExpressionTree = dataclasses.field(kw_only=True)
    nested_patterns: List[PatternTree] = dataclasses.field(kw_only=True)

    @staticmethod
    def create(deconstructor: ExpressionTree, nested_patterns: List[PatternTree],
               start_pos: int, end_pos: int, source: str) -> "DeconstructionPatternTree":
        return DeconstructionPatternTree(
            kind=TreeKind.DECONSTRUCTION_PATTERN,
            deconstructor=deconstructor,
            nested_patterns=nested_patterns,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        """TODO"""


@dataclasses.dataclass(slots=True)
class DoWhileLoopTree(StatementTree):
    """do while 语句

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/DoWhileLoopTree.java
    A tree node for a `do` statement.

    样例：
    do
        statement
    while ( expression );
    """

    condition: ExpressionTree = dataclasses.field(kw_only=True)
    statement: StatementTree = dataclasses.field(kw_only=True)

    @staticmethod
    def create(condition: ExpressionTree,
               statement: StatementTree,
               start_pos: int, end_pos: int, source: str) -> "DoWhileLoopTree":
        return DoWhileLoopTree(
            kind=TreeKind.DO_WHILE_LOOP,
            condition=condition,
            statement=statement,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        return f"do {self.statement.generate()} while ({self.condition.generate()});"


@dataclasses.dataclass(slots=True)
class EmptyStatementTree(StatementTree):
    """空语句

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/EmptyStatementTree.java
    A tree node for an empty (skip) statement.

    样例：;
    """

    @staticmethod
    def create(start_pos: int, end_pos: int, source: str) -> "EmptyStatementTree":
        return EmptyStatementTree(
            kind=TreeKind.EMPTY_STATEMENT,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        return ";"


@dataclasses.dataclass(slots=True)
class EnhancedForLoopTree(StatementTree):
    """增强 for 循环语句

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/EnhancedForLoopTree.java
    A tree node for an "enhanced" `for` loop statement.

    样例：
    for ( variable : expression )
        statement
    """

    variable: VariableTree = dataclasses.field(kw_only=True)
    expression: ExpressionTree = dataclasses.field(kw_only=True)
    statement: StatementTree = dataclasses.field(kw_only=True)

    @staticmethod
    def create(variable: VariableTree,
               expression: ExpressionTree,
               statement: StatementTree,
               start_pos: int, end_pos: int, source: str) -> "EnhancedForLoopTree":
        return EnhancedForLoopTree(
            kind=TreeKind.ENHANCED_FOR_LOOP,
            variable=variable,
            expression=expression,
            statement=statement,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        return (f"for ({self.variable.generate()} : {self.expression.generate()}) \n"
                f"    {self.statement.generate()}")


@dataclasses.dataclass(slots=True)
class ErroneousTree(ExpressionTree):
    """格式错误的表达式

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/ErroneousTree.java
    A tree node to stand in for a malformed expression.
    """

    error_trees: Tree = dataclasses.field(kw_only=True)

    def generate(self) -> str:
        """TODO"""


@dataclasses.dataclass(slots=True)
class ExportsTree(DirectiveTree):
    """模块声明语句中的 exports 指令【JDK 9+】

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/ExportsTree.java
    A tree node for an 'exports' directive in a module declaration.

    样例：
    - exports package-name;
    - exports package-name to module-name;
    """

    package_name: ExpressionTree = dataclasses.field(kw_only=True)
    module_names: List[ExpressionTree] = dataclasses.field(kw_only=True)

    @staticmethod
    def create(package_name: ExpressionTree,
               module_names: List[ExpressionTree],
               start_pos: int, end_pos: int, source: str) -> "ExportsTree":
        return ExportsTree(
            kind=TreeKind.EXPORTS,
            package_name=package_name,
            module_names=module_names,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        """TODO"""


@dataclasses.dataclass(slots=True)
class ExpressionStatementTree(StatementTree):
    """表达式语句

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/ExpressionStatementTree.java
    A tree node for an expression statement.

    样例：expression ;
    """

    expression: ExpressionTree = dataclasses.field(kw_only=True)

    @staticmethod
    def create(expression: ExpressionTree,
               start_pos: int, end_pos: int, source: str) -> "ExpressionStatementTree":
        return ExpressionStatementTree(
            kind=TreeKind.EXPRESSION_STATEMENT,
            expression=expression,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        return f"{self.expression.generate()};"


@dataclasses.dataclass(slots=True)
class ForLoopTree(StatementTree):
    """for 循环语句

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/ForLoopTree.java
    A tree node for a basic {@code for} loop statement.

    样例：
    for ( initializer ; condition ; update )
        statement
    """

    initializer: List[StatementTree] = dataclasses.field(kw_only=True)
    condition: Optional[ExpressionTree] = dataclasses.field(kw_only=True)
    update: List[ExpressionStatementTree] = dataclasses.field(kw_only=True)
    statement: StatementTree = dataclasses.field(kw_only=True)

    @staticmethod
    def create(initializer: initializer,
               condition: Optional[ExpressionTree],
               update: List[ExpressionStatementTree],
               statement: StatementTree,
               start_pos: int, end_pos: int, source: str) -> "ForLoopTree":
        return ForLoopTree(
            kind=TreeKind.FOR_LOOP,
            initializer=initializer,
            condition=condition,
            update=update,
            statement=statement,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        """TODO"""


@dataclasses.dataclass(slots=True)
class IfTree(StatementTree):
    """if 语句

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/IfTree.java
    A tree node for an `if` statement.

    样例：
    if ( condition )
        thenStatement

    if ( condition )
        thenStatement
    else
        elseStatement
    """

    condition: ExpressionTree = dataclasses.field(kw_only=True)
    then_statement: StatementTree = dataclasses.field(kw_only=True)
    else_statement: Optional[StatementTree] = dataclasses.field(kw_only=True)

    @staticmethod
    def create(condition: ExpressionTree,
               then_statement: StatementTree,
               else_statement: Optional[StatementTree],
               start_pos: int, end_pos: int, source: str) -> "IfTree":
        return IfTree(
            kind=TreeKind.IF,
            condition=condition,
            then_statement=then_statement,
            else_statement=else_statement,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        if self.else_statement is None:
            return (f"if ({self.condition.generate()}) \n"
                    f"    {self.then_statement.generate()}")
        return (f"if ({self.condition.generate()}) \n"
                f"    {self.then_statement.generate()} \n"
                f"else \n"
                f"    {self.else_statement.generate()}")


@dataclasses.dataclass(slots=True)
class InstanceOfTree(ExpressionTree):
    """instanceof 表达式

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/InstanceOfTree.java
    A tree node for an `instanceof` expression.
    
    样例：
    expression instanceof type
    expression instanceof type variable-name

    映射逻辑位置：CTree.JCInstanceOf
    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/tools/javac/tree/JCTree.java
    """

    expression: ExpressionTree = dataclasses.field(kw_only=True)
    instance_type: Tree = dataclasses.field(kw_only=True)
    pattern: Optional[PatternTree] = dataclasses.field(kw_only=True)  # 【JDK 16+】

    @staticmethod
    def create(start_pos: int, end_pos: int, source: str,
               expression: ExpressionTree,
               pattern: Tree
               ) -> "InstanceOfTree":
        if isinstance(pattern, PatternTree):
            if isinstance(pattern, BindingPatternTree):
                instance_type = pattern.variable.variable_type
            else:
                instance_type = None
            actual_pattern = pattern
        else:
            instance_type = pattern
            actual_pattern = False
        return InstanceOfTree(
            kind=TreeKind.INTERSECTION_TYPE,
            expression=expression,
            instance_type=instance_type,
            pattern=actual_pattern,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        if self.pattern is None:
            return f"{self.expression.generate()} instanceof {self.instance_type.generate()}"
        return f"{self.expression.generate()} instanceof {self.instance_type.generate()} {self.pattern.generate()}"


@dataclasses.dataclass(slots=True)
class IntersectionTypeTree(Tree):
    """强制类型转换表达式中的交叉类型

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/IntersectionTypeTree.java
    A tree node for an intersection type in a cast expression.
    """

    bounds: List[Tree] = dataclasses.field(kw_only=True)

    @staticmethod
    def create(bounds: List[Tree], start_pos: int, end_pos: int, source: str) -> "IntersectionTypeTree":
        return IntersectionTypeTree(
            kind=TreeKind.INTERSECTION_TYPE,
            bounds=bounds,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        return generate_tree_list(self.bounds, Separator.AMP)


@dataclasses.dataclass(slots=True)
class LabeledStatementTree(StatementTree):
    """包含标签的表达式

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/LabeledStatementTree.java
    A tree node for a labeled statement.

    样例：label : statement
    """

    label: str = dataclasses.field(kw_only=True)
    statement: StatementTree = dataclasses.field(kw_only=True)

    @staticmethod
    def create(label: str, statement: StatementTree,
               start_pos: int, end_pos: int, source: str) -> "LabeledStatementTree":
        return LabeledStatementTree(
            kind=TreeKind.LABELED_STATEMENT,
            label=label,
            statement=statement,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        return f"{self.label} : {self.statement.generate()}"


@dataclasses.dataclass(slots=True)
class LambdaExpressionTree(ExpressionTree):
    """lambda 表达式

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/LambdaExpressionTree.java
    A tree node for a lambda expression.

    样例：
    ()->{}
    (List<String> ls)->ls.size()
    (x,y)-> { return x + y; }
    """

    parameters: List[VariableTree] = dataclasses.field(kw_only=True)
    body: Tree = dataclasses.field(kw_only=True)
    body_kind: LambdaBodyKind = dataclasses.field(kw_only=True)

    @staticmethod
    def create_expression(parameters: List[VariableTree], body: Tree, start_pos: int, end_pos: int,
                          source: str) -> "LambdaExpressionTree":
        return LambdaExpressionTree(
            kind=TreeKind.LAMBDA_EXPRESSION,
            parameters=parameters,
            body=body,
            body_kind=LambdaBodyKind.EXPRESSION,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    @staticmethod
    def create_statement(parameters: List[VariableTree], body: BlockTree, start_pos: int, end_pos: int,
                         source: str) -> "LambdaExpressionTree":
        return LambdaExpressionTree(
            kind=TreeKind.LAMBDA_EXPRESSION,
            parameters=parameters,
            body=body,
            body_kind=LambdaBodyKind.STATEMENT,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        return f"({generate_tree_list(self.parameters, Separator.COMMA)}) -> {self.body.generate()}"


@dataclasses.dataclass(slots=True)
class LiteralTree(ExpressionTree, abc.ABC):
    """字面值

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/LiteralTree.java
    A tree node for a literal expression.
    Use `getKind` to determine the kind of literal.

    样例：value
    """

    @property
    def is_literal(self) -> bool:
        return True


@dataclasses.dataclass(slots=True)
class IntLiteralTree(LiteralTree):
    """整型字面值（包括十进制、八进制、十六进制）"""

    style: IntegerStyle = dataclasses.field(kw_only=True)
    value: int = dataclasses.field(kw_only=True)

    @staticmethod
    def create(style: IntegerStyle, value: int, start_pos: int, end_pos: int, source: str) -> "IntLiteralTree":
        return IntLiteralTree(
            kind=TreeKind.INT_LITERAL,
            style=style,
            value=value,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        return change_int_to_string(self.value, self.style)


@dataclasses.dataclass(slots=True)
class LongLiteralTree(LiteralTree):
    """十进制长整型字面值（包括十进制、八进制、十六进制）"""

    style: IntegerStyle = dataclasses.field(kw_only=True)
    value: int = dataclasses.field(kw_only=True)

    @staticmethod
    def create(style: IntegerStyle, value: int, start_pos: int, end_pos: int, source: str) -> "LongLiteralTree":
        return LongLiteralTree(
            kind=TreeKind.LONG_LITERAL,
            style=style,
            value=value,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        return f"{self.value}L"


@dataclasses.dataclass(slots=True)
class FloatLiteralTree(LiteralTree):
    """单精度浮点数字面值"""

    value: float = dataclasses.field(kw_only=True)

    @staticmethod
    def create(value: float, start_pos: int, end_pos: int, source: str) -> "FloatLiteralTree":
        return FloatLiteralTree(
            kind=TreeKind.FLOAT_LITERAL,
            value=value,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        return f"{self.value}f"


@dataclasses.dataclass(slots=True)
class DoubleLiteralTree(LiteralTree):
    """双精度浮点数字面值"""

    value: float = dataclasses.field(kw_only=True)

    @staticmethod
    def create(value: float, start_pos: int, end_pos: int, source: str) -> "DoubleLiteralTree":
        return DoubleLiteralTree(
            kind=TreeKind.DOUBLE_LITERAL,
            value=value,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        return f"{self.value}"


@dataclasses.dataclass(slots=True)
class TrueLiteralTree(LiteralTree):
    """布尔值真值字面值"""

    @staticmethod
    def create(start_pos: int, end_pos: int, source: str) -> "TrueLiteralTree":
        return TrueLiteralTree(
            kind=TreeKind.BOOLEAN_LITERAL,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        return f"true"


@dataclasses.dataclass(slots=True)
class FalseLiteralTree(LiteralTree):
    """布尔值假值字面值"""

    @staticmethod
    def create(start_pos: int, end_pos: int, source: str) -> "FalseLiteralTree":
        return FalseLiteralTree(
            kind=TreeKind.BOOLEAN_LITERAL,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        return f"false"


@dataclasses.dataclass(slots=True)
class CharacterLiteralTree(LiteralTree):
    """字符字面值"""

    value: str = dataclasses.field(kw_only=True)  # 不包含单引号的字符串

    @staticmethod
    def create(value: str, start_pos: int, end_pos: int, source: str) -> "CharacterLiteralTree":
        return CharacterLiteralTree(
            kind=TreeKind.CHAR_LITERAL,
            value=value,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        return f"'{self.value}'"


@dataclasses.dataclass(slots=True)
class StringLiteralTree(LiteralTree):
    """字符串字面值"""

    style: StringStyle = dataclasses.field(kw_only=True)  # 字面值样式
    value: str = dataclasses.field(kw_only=True)  # 不包含双引号的字符串内容

    @staticmethod
    def create_string(value: str, start_pos: int, end_pos: int, source: str) -> "StringLiteralTree":
        return StringLiteralTree(
            kind=TreeKind.STRING_LITERAL,
            style=StringStyle.STRING,
            value=value,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    @staticmethod
    def create_text_block(value: str, start_pos: int, end_pos: int, source: str) -> "StringLiteralTree":
        return StringLiteralTree(
            kind=TreeKind.STRING_LITERAL,
            style=StringStyle.TEXT_BLOCK,
            value=value,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        if self.style == StringStyle.STRING:
            return f"\"{repr(self.value)}\""
        return f"\"\"\"\n{repr(self.value)}\"\"\""


@dataclasses.dataclass(slots=True)
class NullLiteralTree(LiteralTree):
    """空值字面值"""

    @staticmethod
    def create(start_pos: int, end_pos: int, source: str) -> "NullLiteralTree":
        return NullLiteralTree(
            kind=TreeKind.NULL_LITERAL,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        return f"null"


@dataclasses.dataclass(slots=True)
class MemberReferenceTree(ExpressionTree):
    """成员引用表达式

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/MemberReferenceTree.java
    A tree node for a member reference expression.

    样例：expression :: [ identifier | new ]
    """

    mode: ReferenceMode = dataclasses.field(kw_only=True)
    name: str = dataclasses.field(kw_only=True)
    expression: ExpressionTree = dataclasses.field(kw_only=True)
    type_arguments: List[ExpressionTree] = dataclasses.field(kw_only=True)

    @staticmethod
    def create(mode: ReferenceMode,
               name: str,
               qualifier_expression: ExpressionTree,
               type_arguments: List[ExpressionTree],
               start_pos: int, end_pos: int, source: str) -> "MemberReferenceTree":
        return MemberReferenceTree(
            kind=TreeKind.MEMBER_REFERENCE,
            mode=mode,
            name=name,
            expression=qualifier_expression,
            type_arguments=type_arguments,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        """TODO"""


@dataclasses.dataclass(slots=True)
class MemberSelectTree(ExpressionTree):
    """成员访问表达式

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/MemberSelectTree.java
    A tree node for a member access expression.

    样例：expression . identifier
    """

    expression: ExpressionTree = dataclasses.field(kw_only=True)
    identifier: IdentifierTree = dataclasses.field(kw_only=True)

    @staticmethod
    def create(expression: ExpressionTree, identifier: IdentifierTree,
               start_pos: int, end_pos: int, source: str) -> "MemberSelectTree":
        return MemberSelectTree(
            kind=TreeKind.MEMBER_SELECT,
            expression=expression,
            identifier=identifier,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        return f"{self.expression.generate()}.{self.identifier.generate()}"


@dataclasses.dataclass(slots=True)
class MethodInvocationTree(ExpressionTree):
    """方法调用表达式

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/MethodInvocationTree.java
    A tree node for a method invocation expression.

    样例：
    - identifier ( arguments )
    - this . typeArguments identifier ( arguments )
    """

    type_arguments: List[Tree] = dataclasses.field(kw_only=True)
    method_select: ExpressionTree = dataclasses.field(kw_only=True)
    arguments: List[ExpressionTree] = dataclasses.field(kw_only=True)

    @staticmethod
    def create(type_arguments: List[Tree],
               method_select: ExpressionTree,
               arguments: List[ExpressionTree],
               start_pos: int, end_pos: int, source: str) -> "MethodInvocationTree":
        return MethodInvocationTree(
            kind=TreeKind.METHOD_INVOCATION,
            type_arguments=type_arguments,
            method_select=method_select,
            arguments=arguments,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        """TODO"""


@dataclasses.dataclass(slots=True)
class MethodTree(Tree):
    """声明方法或注解类型元素

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/MethodTree.java
    A tree node for a method or annotation type element declaration.

    样例 1：
    modifiers typeParameters type name
        ( parameters )
        body

    样例 2：
    modifiers type name ( ) default defaultValue
    """

    modifiers: ModifiersTree = dataclasses.field(kw_only=True)
    name: str = dataclasses.field(kw_only=True)
    return_type: Tree = dataclasses.field(kw_only=True)
    type_parameters: List[TypeParameterTree] = dataclasses.field(kw_only=True)
    receiver_parameter: VariableTree = dataclasses.field(kw_only=True)
    parameters: List[VariableTree] = dataclasses.field(kw_only=True)
    throws: List[ExpressionTree] = dataclasses.field(kw_only=True)
    block: BlockTree = dataclasses.field(kw_only=True)
    default_value: Tree = dataclasses.field(kw_only=True)

    @staticmethod
    def create(modifiers: ModifiersTree,
               name: str,
               return_type: Tree,
               type_parameters: List[TypeParameterTree],
               receiver_parameter: Optional[VariableTree],
               parameters: List[VariableTree],
               throws: List[ExpressionTree],
               block: BlockTree,
               default_value: Tree,
               start_pos: int, end_pos: int, source: str) -> "MethodTree":
        return MethodTree(
            kind=TreeKind.METHOD,
            modifiers=modifiers,
            name=name,
            return_type=return_type,
            type_parameters=type_parameters,
            receiver_parameter=receiver_parameter,
            parameters=parameters,
            throws=throws,
            block=block,
            default_value=default_value,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        """TODO"""


@dataclasses.dataclass(slots=True)
class NewArrayTree(ExpressionTree):
    """初始化数组表达式

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/NewArrayTree.java
    A tree node for an expression to create a new instance of an array.

    样例 1：new type dimensions initializers
    样例 2：new type dimensions [ ] initializers
    """

    array_type: Optional[ExpressionTree] = dataclasses.field(kw_only=True)
    dimensions: List[ExpressionTree] = dataclasses.field(kw_only=True)
    initializers: List[ExpressionTree] = dataclasses.field(kw_only=True)
    annotations: Optional[List[AnnotationTree]] = dataclasses.field(kw_only=True, default=None)
    dim_annotations: Optional[List[List[AnnotationTree]]] = dataclasses.field(kw_only=True, default=None)

    @staticmethod
    def create(array_type: Optional[ExpressionTree],
               dimensions: List[ExpressionTree],
               initializers: List[ExpressionTree],
               dim_annotations: Optional[List[List[AnnotationTree]]],
               start_pos: int, end_pos: int, source: str) -> "NewArrayTree":
        return NewArrayTree(
            kind=TreeKind.NEW_ARRAY,
            array_type=array_type,
            dimensions=dimensions,
            initializers=initializers,
            dim_annotations=dim_annotations,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        """TODO"""


@dataclasses.dataclass(slots=True)
class NewClassTree(ExpressionTree):
    """实例化类表达式

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/NewClassTree.java
    A tree node to declare a new instance of a class.

    样例 1:
    new identifier ( )

    样例 2:
    new identifier ( arguments )

    样例 3:
    new typeArguments identifier ( arguments )
        classBody

    样例 4:
    enclosingExpression.new identifier ( arguments )
    """

    enclosing_expression: Optional[ExpressionTree] = dataclasses.field(kw_only=True)
    type_arguments: List[Tree] = dataclasses.field(kw_only=True)
    identifier: ExpressionTree = dataclasses.field(kw_only=True)
    arguments: List[ExpressionTree] = dataclasses.field(kw_only=True)
    class_body: Optional[ClassTree] = dataclasses.field(kw_only=True)

    @staticmethod
    def create(enclosing: Optional[ExpressionTree],
               type_arguments: List[Tree],
               identifier: ExpressionTree,
               arguments: List[ExpressionTree],
               class_body: Optional[ClassTree],
               start_pos: int, end_pos: int, source: str) -> "NewClassTree":
        return NewClassTree(
            kind=TreeKind.NEW_CLASS,
            enclosing_expression=enclosing,
            type_arguments=type_arguments,
            identifier=identifier,
            arguments=arguments,
            class_body=class_body,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        """TODO 待验证分隔符"""
        enclosing_str = f"{self.enclosing_expression.generate()}." if self.enclosing_expression is not None else ""
        body_str = f"\n    {self.class_body.generate()}" if self.class_body is not None else ""
        return (f"{enclosing_str}new "
                f"{generate_tree_list(self.type_arguments, Separator.SPACE)} {self.identifier.generate()} "
                f"( {generate_tree_list(self.arguments, Separator.COMMA)} ){body_str}")


@dataclasses.dataclass(slots=True)
class OpensTree(DirectiveTree):
    """模块声明中的 opens 指令

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/OpensTree.java
    A tree node for an 'opens' directive in a module declaration.

    样例 1:
    opens package-name;

    样例 2:
    opens package-name to module-name;
    """

    package_name: ExpressionTree = dataclasses.field(kw_only=True)
    module_names: List[ExpressionTree] = dataclasses.field(kw_only=True)

    @staticmethod
    def create(package_name: ExpressionTree,
               module_names: List[ExpressionTree],
               start_pos: int, end_pos: int, source: str) -> "OpensTree":
        return OpensTree(
            kind=TreeKind.OPENS,
            package_name=package_name,
            module_names=module_names,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        """TODO"""


@dataclasses.dataclass(slots=True)
class ParameterizedTypeTree(ExpressionTree):
    """包含类型参数的类型表达式

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/ParameterizedTypeTree.java
    A tree node for a type expression involving type parameters.

    样例:
    type < typeArguments >
    """

    type_name: Tree = dataclasses.field(kw_only=True)
    type_arguments: List[Tree] = dataclasses.field(kw_only=True)

    @staticmethod
    def create(type_name: Tree, type_arguments: List[Tree],
               start_pos: int, end_pos: int, source: str) -> "ParameterizedTypeTree":
        return ParameterizedTypeTree(
            kind=TreeKind.PARAMETERIZED_TYPE,
            type_name=type_name,
            type_arguments=type_arguments,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        return f"{self.type_name.generate()}<{generate_tree_list(self.type_arguments, Separator.COMMA)}>"


@dataclasses.dataclass(slots=True)
class ParenthesizedTree(ExpressionTree):
    """括号表达式

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/ParenthesizedTree.java
    A tree node for a parenthesized expression.
    Note: parentheses not be preserved by the parser.

    样例:
    ( expression )
    """

    expression: ExpressionTree = dataclasses.field(kw_only=True)

    @staticmethod
    def create(expression: ExpressionTree, start_pos: int, end_pos: int, source: str) -> "ParenthesizedTree":
        return ParenthesizedTree(
            kind=TreeKind.PARENTHESIZED,
            expression=expression,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        return f"({self.expression.generate()})"


@dataclasses.dataclass(slots=True)
class PatternCaseLabelTree(CaseLabelTree):
    """【JDK 21+】TODO 名称待整理

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/PatternCaseLabelTree.java
    A case label element that refers to an expression
    """

    pattern: PatternTree = dataclasses.field(kw_only=True)

    @staticmethod
    def create(pattern: PatternTree, start_pos: int, end_pos: int, source: str) -> "PatternCaseLabelTree":
        return PatternCaseLabelTree(
            kind=TreeKind.PATTERN_CASE_LABEL,
            pattern=pattern,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    @staticmethod
    def mock() -> "PatternCaseLabelTree":
        return PatternCaseLabelTree(
            kind=TreeKind.PATTERN_CASE_LABEL,
            pattern=AnyPatternTree.mock(),
            start_pos=None,
            end_pos=None,
            source=None
        )

    def generate(self) -> str:
        """TODO"""


@dataclasses.dataclass(slots=True)
class PrimitiveTypeTree(ExpressionTree):
    """原生类型

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/PrimitiveTypeTree.java
    A tree node for a primitive type.

    样例：
    primitiveTypeKind
    """

    type_kind: TypeKind = dataclasses.field(kw_only=True)

    @staticmethod
    def create(type_kind: TypeKind, start_pos: int, end_pos: int, source: str) -> "PrimitiveTypeTree":
        return PrimitiveTypeTree(
            kind=TreeKind.PRIMITIVE_TYPE,
            type_kind=type_kind,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    @staticmethod
    def create_void(start_pos: int, end_pos: int, source: str) -> "PrimitiveTypeTree":
        return PrimitiveTypeTree(
            kind=TreeKind.PRIMITIVE_TYPE,
            type_kind=TypeKind.VOID,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    @staticmethod
    def mock(type_name: str) -> "PrimitiveTypeTree":
        return PrimitiveTypeTree(
            kind=TreeKind.PRIMITIVE_TYPE,
            type_kind=TypeKind[type_name],
            start_pos=None,
            end_pos=None,
            source=None
        )

    def generate(self) -> str:
        return self.type_kind.value


@dataclasses.dataclass(slots=True)
class ProvidesTree(DirectiveTree):
    """模块声明语句的 provides 指令【JDK 9+】

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/ProvidesTree.java
    A tree node for a 'provides' directive in a module declaration.

    样例:
    provides service-name with implementation-name;
    """

    service_name: ExpressionTree = dataclasses.field(kw_only=True)
    implementation_names: List[ExpressionTree] = dataclasses.field(kw_only=True)

    @staticmethod
    def create(service_name: ExpressionTree,
               implementation_names: List[ExpressionTree],
               start_pos: int, end_pos: int, source: str) -> "ProvidesTree":
        return ProvidesTree(
            kind=TreeKind.PROVIDES,
            service_name=service_name,
            implementation_names=implementation_names,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        """TODO"""


@dataclasses.dataclass(slots=True)
class RequiresTree(DirectiveTree):
    """模块声明语句中的 requires 指令【JDK 9+】

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/RequiresTree.java
    A tree node for a 'requires' directive in a module declaration.

    样例 1:
    requires module-name;

    样例 2:
    requires static module-name;

    样例 3:
    requires transitive module-name;
    """

    is_static: bool = dataclasses.field(kw_only=True)
    is_transitive: bool = dataclasses.field(kw_only=True)
    module_name: ExpressionTree = dataclasses.field(kw_only=True)

    @staticmethod
    def create(is_static: bool,
               is_transitive: bool,
               module_name: ExpressionTree,
               start_pos: int, end_pos: int, source: str) -> "RequiresTree":
        return RequiresTree(
            kind=TreeKind.REQUIRES,
            is_static=is_static,
            is_transitive=is_transitive,
            module_name=module_name,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        static_str = " static" if self.is_static is True else ""
        transitive_str = " transitive" if self.is_transitive is True else ""
        return f"requires{static_str}{transitive_str} {self.module_name.generate()}"


@dataclasses.dataclass(slots=True)
class ReturnTree(StatementTree):
    """返回语句

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/ReturnTree.java
    A tree node for a `return` statement.

    样例 1:
    return;

    样例 2:
    return expression ;
    """

    expression: Optional[ExpressionTree] = dataclasses.field(kw_only=True)

    @staticmethod
    def create(expression: ExpressionTree,
               start_pos: int, end_pos: int, source: str) -> "ReturnTree":
        return ReturnTree(
            kind=TreeKind.RETURN,
            expression=expression,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        if self.expression is None:
            return "return;"
        return f"return {self.expression.generate()};"


@dataclasses.dataclass(slots=True)
class SwitchExpressionTree(ExpressionTree):
    """switch 表达式【JDK 14+】

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/SwitchExpressionTree.java
    A tree node for a `switch` expression.

    样例:
    switch ( expression ) {
        cases
    }
    """

    expression: ExpressionTree = dataclasses.field(kw_only=True)
    cases: List[CaseTree] = dataclasses.field(kw_only=True)

    @staticmethod
    def create(expression: ExpressionTree,
               cases: List[CaseTree],
               start_pos: int, end_pos: int, source: str) -> "SwitchExpressionTree":
        return SwitchExpressionTree(
            kind=TreeKind.SWITCH_EXPRESSION,
            expression=expression,
            cases=cases,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        return (f"switch ({self.expression.generate()}) {{ \n"
                f"    {generate_tree_list(self.cases, Separator.SEMI)} \n"
                f"}}")


@dataclasses.dataclass(slots=True)
class SwitchTree(StatementTree):
    """switch 语句

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/SwitchTree.java
    A tree node for a `switch` statement.

    样例:
    switch ( expression ) {
        cases
    }
    """

    expression: ExpressionTree = dataclasses.field(kw_only=True)
    cases: List[CaseTree] = dataclasses.field(kw_only=True)

    @staticmethod
    def create(expression: ExpressionTree,
               cases: List[CaseTree],
               start_pos: int, end_pos: int, source: str) -> "SwitchTree":
        return SwitchTree(
            kind=TreeKind.SWITCH,
            expression=expression,
            cases=cases,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        return (f"switch ({self.expression.generate()}) {{ \n"
                f"    {generate_tree_list(self.cases, Separator.SEMI)} \n"
                f"}}")


@dataclasses.dataclass(slots=True)
class SynchronizedTree(StatementTree):
    """同步代码块语句

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/SynchronizedTree.java
    A tree node for a `synchronized` statement.

    样例:
    synchronized ( expression )
        block
    """

    expression: ExpressionTree = dataclasses.field(kw_only=True)
    block: BlockTree = dataclasses.field(kw_only=True)

    @staticmethod
    def create(expression: ExpressionTree,
               block: BlockTree,
               start_pos: int, end_pos: int, source: str) -> "SynchronizedTree":
        return SynchronizedTree(
            kind=TreeKind.SYNCHRONIZED,
            expression=expression,
            block=block,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        return (f"synchronized ({self.expression.generate()}) \n"
                f"    {self.block.generate()}")


@dataclasses.dataclass(slots=True)
class ThrowTree(StatementTree):
    """throw 语句

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/ThrowTree.java
    A tree node for a `throw` statement.

    样例:
    throw expression;
    """

    expression: ExpressionTree = dataclasses.field(kw_only=True)

    @staticmethod
    def create(expression: ExpressionTree,
               start_pos: int, end_pos: int, source: str) -> "ThrowTree":
        return ThrowTree(
            kind=TreeKind.THROW,
            expression=expression,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        return f"throw {self.expression.generate()};"


@dataclasses.dataclass(slots=True)
class TryTree(StatementTree):
    """try 语句

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/TryTree.java
    A tree node for a `try` statement.

    样例:
    try
        block
    catches
    finally
        finallyBlock
    """

    block: BlockTree = dataclasses.field(kw_only=True)
    catches: List[CatchTree] = dataclasses.field(kw_only=True)
    finally_block: Optional[BlockTree] = dataclasses.field(kw_only=True)
    resources: List[Tree] = dataclasses.field(kw_only=True)

    @staticmethod
    def create(block: BlockTree,
               catches: List[CatchTree],
               finally_block: Optional[BlockTree],
               resources: List[Tree],
               start_pos: int, end_pos: int, source: str) -> "TryTree":
        return TryTree(
            kind=TreeKind.TRY,
            block=block,
            catches=catches,
            finally_block=finally_block,
            resources=resources,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        """TODO"""


@dataclasses.dataclass(slots=True)
class TypeCastTree(ExpressionTree):
    """强制类型转换表达式

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/TypeCastTree.java
    A tree node for a type cast expression.

    样例:
    ( type ) expression
    """

    cast_type: Tree = dataclasses.field(kw_only=True)
    expression: ExpressionTree = dataclasses.field(kw_only=True)

    @staticmethod
    def create(cast_type: Tree, expression: ExpressionTree, start_pos: int, end_pos: int,
               source: str) -> "TypeCastTree":
        return TypeCastTree(
            kind=TreeKind.TYPE_CAST,
            cast_type=cast_type,
            expression=expression,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        return f"({self.cast_type.generate()}){self.expression.generate()}"


@dataclasses.dataclass(slots=True)
class UnaryTree(ExpressionTree):
    """一元表达式

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/UnaryTree.java
    A tree node for postfix and unary expressions.
    Use `getKind` to determine the kind of operator.

    样例 1:
    operator expression

    样例 2:
    expression operator
    """

    expression: ExpressionTree = dataclasses.field(kw_only=True)

    @staticmethod
    def create(kind: TreeKind, expression: ExpressionTree, start_pos: int, end_pos: int, source: str) -> "UnaryTree":
        return UnaryTree(
            kind=kind,
            expression=expression,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        """TODO"""


@dataclasses.dataclass(slots=True)
class UnionTypeTree(Tree):
    """TODO 名称待整理

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/UnionTypeTree.java
    A tree node for a union type expression in a multicatch variable declaration.
    """

    type_alternatives: List[Tree] = dataclasses.field(kw_only=True)

    @staticmethod
    def create(type_alternatives: List[Tree],
               start_pos: int, end_pos: int, source: str) -> "UnionTypeTree":
        return UnionTypeTree(
            kind=TreeKind.UNION_TYPE,
            type_alternatives=type_alternatives,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        """TODO"""


@dataclasses.dataclass(slots=True)
class UsesTree(DirectiveTree):
    """模块声明语句中的 uses 指令【JDK 9+】

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/UsesTree.java
    A tree node for a 'uses' directive in a module declaration.

    样例 1:
    uses service-name;
    """

    service_name: ExpressionTree = dataclasses.field(kw_only=True)

    @staticmethod
    def create(service_name: ExpressionTree,
               start_pos: int, end_pos: int, source: str) -> "UsesTree":
        return UsesTree(
            kind=TreeKind.USES,
            service_name=service_name,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        return f"uses {self.service_name.generate()};"


@dataclasses.dataclass(slots=True)
class WhileLoopTree(StatementTree):
    """while 循环语句

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/WhileLoopTree.java
    A tree node for a `while` loop statement.

    样例 1:
    while ( condition )
        statement
    """

    condition: ExpressionTree = dataclasses.field(kw_only=True)
    statement: StatementTree = dataclasses.field(kw_only=True)

    @staticmethod
    def create(condition: ExpressionTree,
               statement: StatementTree,
               start_pos: int, end_pos: int, source: str) -> "WhileLoopTree":
        return WhileLoopTree(
            kind=TreeKind.WHILE_LOOP,
            condition=condition,
            statement=statement,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        return (f"while ({self.condition.generate()}) \n"
                f"    {self.statement.generate()}")


@dataclasses.dataclass(slots=True)
class WildcardTree(ExpressionTree):
    """通配符

    与 JDK 中 com.sun.source.tree.WildcardTree 接口的继承关系不一致，是因为 con.sun.tools.javac.tree.JCTree 类继承了 JCExpression，详见：
    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/tools/javac/tree/JCTree.java

    JDK 接口源码如下：
    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/WildcardTree.java
    A tree node for a wildcard type argument.
    Use `getKind` to determine the kind of bound.

    样例 1:
    ?

    样例 2:
    ? extends bound

    样例 3:
    ? super bound
    """

    bound: Optional[Tree] = dataclasses.field(kw_only=True)  # 如果是 "?" 则为 None

    @staticmethod
    def create_extends_wildcard(bound: Tree, start_pos: int, end_pos: int, source: str) -> "WildcardTree":
        return WildcardTree(
            kind=TreeKind.EXTENDS_WILDCARD,
            bound=bound,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    @staticmethod
    def create_super_wildcard(bound: Tree, start_pos: int, end_pos: int, source: str) -> "WildcardTree":
        return WildcardTree(
            kind=TreeKind.SUPER_WILDCARD,
            bound=bound,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    @staticmethod
    def create_unbounded_wildcard(start_pos: int, end_pos: int, source: str) -> "WildcardTree":
        return WildcardTree(
            kind=TreeKind.UNBOUNDED_WILDCARD,
            bound=None,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        if self.kind == TreeKind.EXTENDS_WILDCARD:
            return f"? extends {self.bound.generate()}"
        if self.kind == TreeKind.SUPER_WILDCARD:
            return f"? super {self.bound.generate()}"
        return "?"  # TreeKind.UNBOUNDED_WILDCARD


@dataclasses.dataclass(slots=True)
class YieldTree(StatementTree):
    """yield 语句

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/YieldTree.java
    A tree node for a `yield` statement.

    样例 1:
    yield expression;
    """

    value: ExpressionTree = dataclasses.field(kw_only=True)

    @staticmethod
    def create(value: ExpressionTree, start_pos: int, end_pos: int, source: str) -> "YieldTree":
        return YieldTree(
            kind=TreeKind.YIELD,
            value=value,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        return f"yield {self.value.generate()};"

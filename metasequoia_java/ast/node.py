import abc
import dataclasses
from typing import List, Optional

from metasequoia_java.ast.base import CaseLabel
from metasequoia_java.ast.base import Directive
from metasequoia_java.ast.base import Expression
from metasequoia_java.ast.base import Pattern
from metasequoia_java.ast.base import Statement
from metasequoia_java.ast.base import Tree
from metasequoia_java.ast.base import Type
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

__all__ = [
    "AnnotatedType",  # 包含注解的类型
    "Annotation",  # 注解
    "AnyPattern",  # 【JDK 22+】
    "ArrayAccess",  # 访问数组中元素
    "ArrayType",  # 数组类型
    "Assert",  # assert 语句
    "Assignment",  # 赋值表达式
    "Binary",  # 二元表达式
    "BindingPattern",  # 【JDK 16+】
    "Block",  # 代码块
    "Break",  # break 语句
    "Case",  # switch 语句或表达式中的 case 子句
    "Catch",  # try 语句中的 catch 代码块
    "Class",  # 类（class）、接口（interface）、枚举类（enum）、记录类（record）或注解类（annotation type）的声明语句
    "CompilationUnit",  # 表示普通编译单元和模块化编译单元的抽象语法树节点
    "CompoundAssignment",  # 赋值表达式
    "ConditionalExpression",  # 三目表达式
    "ConstantCaseLabel",  #
    "Continue",  # continue 语句
    "DeconstructionPattern",  # 【JDK 21+】
    "DefaultCaseLabel",  # 【JDK 21+】
    "DoWhileLoop",  # do while 语句【JDK 21+】
    "EmptyStatement",  # 空语句
    "EnhancedForLoop",  # 增强 for 循环语句
    "Erroneous",
    "Exports",  # 模块声明语句中的 exports 指令【JDK 9+】
    "ExpressionStatement",  # 表达式语句
    "ForLoop",  # for 循环语句
    "Identifier",  # 标识符
    "If",  # if 语句
    "Import",  # 声明引用
    "InstanceOf",  # instanceof 表达式
    "IntersectionType",  # 强制类型转换表达式中的交叉类型
    "LabeledStatement",  # 包含标签的表达式
    "LambdaExpression",  # lambda 表达式
    "Literal",  # 字面值
    "IntLiteral",  # 整型字面值（包括十进制、八进制、十六进制）
    "LongLiteral",  # 十进制长整型字面值（包括十进制、八进制、十六进制）
    "FloatLiteral",  # 单精度浮点数字面值
    "DoubleLiteral",  # 双精度浮点数字面值
    "TrueLiteral",  # 布尔值真值字面值
    "FalseLiteral",  # 布尔值假值字面值
    "CharacterLiteral",  # 字符字面值
    "StringLiteral",  # 字符串字面值
    "NullLiteral",  # 空值字面值
    "MemberReference",  # 成员引用表达式
    "MemberSelect",  # 成员访问表达式
    "MethodInvocation",  # 方法调用表达式
    "Method",  # 声明方法或注解类型元素
    "Modifiers",  # 用于声明表达式的修饰符，包括注解
    "Module",  # 声明模块【JDK 9+】
    "NewArray",  # 初始化数组表达式
    "NewClass",  # 实例化类表达式
    "Opens",  # 模块声明中的 opens 指令
    "Package",  # 声明包【JDK 9+】
    "ParameterizedType",  # 包含类型参数的类型表达式
    "Parenthesized",  # 括号表达式
    "PatternCaseLabel",  # 【JDK 21+】
    "PrimitiveType",  # 原生类型
    "Provides",  # 模块声明语句的 provides 指令【JDK 9+】
    "Requires",  # 模块声明语句中的 requires 指令【JDK 9+】
    "Return",  # 返回语句
    "SwitchExpression",  # switch 表达式【JDK 14+】
    "Switch",  # switch 语句
    "Synchronized",  # 同步代码块语句
    "Throw",  # throw 语句
    "Try",  # try 语句
    "TypeCast",  # 强制类型转换表达式
    "TypeParameter",  # 类型参数列表
    "Unary",  # 一元表达式
    "UnionType",  #
    "Uses",  # 模块声明语句中的 uses 指令【JDK 9+】
    "Variable",  # 声明变量
    "WhileLoop",  # while 循环语句
    "Wildcard",  # 通配符
    "Yield",  # yield 语句
]


@dataclasses.dataclass(slots=True)
class DefaultCaseLabel(CaseLabel):
    """【JDK 21+】TODO 名称待整理

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/DefaultCaseLabelTree.java
    A case label that marks `default` in `case null, default`.
    """

    @staticmethod
    def create(start_pos: int, end_pos: int, source: str) -> "DefaultCaseLabel":
        return DefaultCaseLabel(
            kind=TreeKind.DEFAULT_CASE_LABEL,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        """TODO"""


@dataclasses.dataclass(slots=True)
class Annotation(Expression):
    """注解

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/AnnotationTree.java
    A tree node for an annotation.

    样例：
    - @annotationType
    - @annotationType ( arguments )
    """

    annotation_type: Tree = dataclasses.field(kw_only=True)
    arguments: List[Expression] = dataclasses.field(kw_only=True)

    @staticmethod
    def create_annotation(annotation_type: Tree,
                          arguments: List[Expression],
                          start_pos: int, end_pos: int, source: str) -> "Annotation":
        return Annotation(
            kind=TreeKind.ANNOTATION,
            annotation_type=annotation_type,
            arguments=arguments,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    @staticmethod
    def create_type_annotation(annotation_type: Tree,
                               arguments: List[Expression],
                               start_pos: int, end_pos: int, source: str) -> "Annotation":
        return Annotation(
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
class AnnotatedType(Type):
    """包含注解的类型

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/AnnotatedTypeTree.java
    A tree node for an annotated type.

    样例：
    - @annotationType String
    - @annotationType ( arguments ) Date
    """

    annotations: List[Annotation] = dataclasses.field(kw_only=True)
    underlying_type: Expression = dataclasses.field(kw_only=True)

    @staticmethod
    def create(annotations: List[Annotation], underlying_type: Expression,
               start_pos: int, end_pos: int, source: str) -> "AnnotatedType":
        return AnnotatedType(
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
class AnyPattern(Pattern):
    """【JDK 22+】TODO 名称待整理

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/AnyPatternTree.java
    A tree node for a binding pattern that matches a pattern with a variable of any name and a type of the match
    candidate; an unnamed pattern.

    使用下划线 `_` 的样例：
    if (r instanceof R(_)) {}
    """

    @staticmethod
    def create(start_pos: int, end_pos: int, source: str) -> "AnyPattern":
        return AnyPattern(
            kind=TreeKind.ANY_PATTERN,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    @staticmethod
    def mock() -> "AnyPattern":
        return AnyPattern(
            kind=TreeKind.ANY_PATTERN,
            start_pos=None,
            end_pos=None,
            source=None
        )

    def generate(self) -> str:
        """TODO"""


@dataclasses.dataclass(slots=True)
class ArrayAccess(Expression):
    """访问数组中元素

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/ArrayAccessTree.java
    A tree node for an array access expression.

    样例：
    - expression[index]
    """

    expression: Expression = dataclasses.field(kw_only=True)
    index: Expression = dataclasses.field(kw_only=True)

    @staticmethod
    def create(expression: Expression, index: Expression,
               start_pos: int, end_pos: int, source: str) -> "ArrayAccess":
        return ArrayAccess(
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
class ArrayType(Type):
    """数组类型

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/ArrayTypeTree.java
    A tree node for an array type.

    样例：
    - type[]
    """

    expression: Expression = dataclasses.dataclass(slots=True)

    @staticmethod
    def create(expression: Expression,
               start_pos: int, end_pos: int, source: str) -> "ArrayType":
        return ArrayType(
            kind=TreeKind.ARRAY_TYPE,
            expression=expression,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        return f"{self.expression.generate()}[]"


@dataclasses.dataclass(slots=True)
class Assert(Statement):
    """assert 语句

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/AssertTree.java
    A tree node for an `assert` statement.

    样例：
    - assert condition ;
    - assert condition : detail ;
    """

    assertion: Expression = dataclasses.field(kw_only=True)
    message: Optional[Expression] = dataclasses.field(kw_only=True)

    @staticmethod
    def create(assertion: Expression,
               message: Optional[Expression],
               start_pos: int, end_pos: int, source: str) -> "Assert":
        return Assert(
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
class Assignment(Expression):
    """赋值表达式

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/AssignmentTree.java
    A tree node for an assignment expression.

    样例：
    - variable = expression
    """

    variable: Expression = dataclasses.field(kw_only=True)
    expression: Expression = dataclasses.field(kw_only=True)

    @staticmethod
    def create(variable: Expression,
               expression: Expression,
               start_pos: int, end_pos: int, source: str) -> "Assignment":
        return Assignment(
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
class Binary(Expression):
    """二元表达式

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/BinaryTree.java
    A tree node for a binary expression.
    Use `getKind` to determine the kind of operator.

    样例：
    - leftOperand operator rightOperand
    """

    left_operand: Expression = dataclasses.field(kw_only=True)
    right_operand: Expression = dataclasses.field(kw_only=True)

    @staticmethod
    def create(start_pos: int, end_pos: int, source: str,
               kind: TreeKind,
               left_operand: Expression,
               right_operand: Expression) -> "Binary":
        return Binary(
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
class Modifiers(Tree):
    """用于声明表达式的修饰符，包括注解

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/ModifiersTree.java
    A tree node for the modifiers, including annotations, for a declaration.

    样例：
    - flags
    - flags annotations
    """

    flags: List[Modifier] = dataclasses.field(kw_only=True)
    annotations: List[Annotation] = dataclasses.field(kw_only=True)

    @staticmethod
    def create(flags: List[Modifier],
               annotations: Optional[List[Annotation]],
               start_pos: int, end_pos: int, source: str) -> "Modifiers":
        if annotations is None:
            annotations = []
        return Modifiers(
            kind=TreeKind.MODIFIERS,
            flags=flags,
            annotations=annotations,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    @staticmethod
    def create_empty() -> "Modifiers":
        """创建没有任何修饰符的 ModifiersTree 节点，且该节点没有实际的位置和代码"""
        return Modifiers(
            kind=TreeKind.MODIFIERS,
            flags=[],
            annotations=[],
            start_pos=None,
            end_pos=None,
            source=None
        )

    @staticmethod
    def mock() -> "Modifiers":
        return Modifiers(
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
class Variable(Statement):
    """声明变量

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/VariableTree.java
    A tree node for a variable declaration.

    样例：
    - modifiers type name = initializer ;
    - modifiers type qualified-name.this
    """

    modifiers: Modifiers = dataclasses.field(kw_only=True)
    name: Optional[str] = dataclasses.field(kw_only=True, default=None)
    name_expression: Optional[Expression] = dataclasses.field(kw_only=True, default=None)
    variable_type: Tree = dataclasses.field(kw_only=True)  # 研究这个类型是否可以变为 Type
    initializer: Optional[Expression] = dataclasses.field(kw_only=True)

    @staticmethod
    def create_by_name(modifiers: Modifiers,
                       name: Optional[str],
                       variable_type: Tree,
                       initializer: Optional[Expression],
                       start_pos: int, end_pos: int, source: str) -> "Variable":
        return Variable(
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
    def create_by_name_expression(modifiers: Modifiers, name_expression: Optional[Expression],
                                  variable_type: Tree,
                                  start_pos: int, end_pos: int, source: str) -> "Variable":
        return Variable(
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
class BindingPattern(Pattern):
    """【JDK 16+】TODO 名称待整理

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/BindingPatternTree.java
    A binding pattern tree
    """

    variable: Variable = dataclasses.field(kw_only=True)

    @staticmethod
    def create(variable: Variable, start_pos: int, end_pos: int, source: str) -> "BindingPattern":
        return BindingPattern(
            kind=TreeKind.VARIABLE,
            variable=variable,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        """TODO"""


@dataclasses.dataclass(slots=True)
class Block(Statement):
    """代码块

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/BlockTree.java
    A tree node for a statement block.

    样例：
    - { }
    - { statements }
    - static { statements }
    """

    is_static: bool = dataclasses.field(kw_only=True)
    statements: List[Statement] = dataclasses.field(kw_only=True)

    @staticmethod
    def create(is_static: bool, statements: List[Statement], start_pos: int, end_pos: int,
               source: str) -> "Block":
        return Block(
            kind=TreeKind.BLOCK,
            is_static=is_static,
            statements=statements,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    @staticmethod
    def mock() -> "Block":
        return Block(
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
class Break(Statement):
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
               start_pos: int, end_pos: int, source: str) -> "Break":
        return Break(
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
class Case(Tree):
    """switch 语句或表达式中的 case 子句

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/CaseTree.java
    A tree node for a `case` in a `switch` statement or expression.

    样例：
    case expression :
        statements
    default :
        statements
    """

    expressions: Optional[List[Expression]] = dataclasses.field(kw_only=True, default=None)  # @Deprecated
    labels: List[CaseLabel] = dataclasses.field(kw_only=True)  # 【JDK 21+】
    guard: Expression = dataclasses.field(kw_only=True)  # 【JDK 21+】
    statements: List[Statement] = dataclasses.field(kw_only=True)
    body: Optional[Tree] = dataclasses.field(kw_only=True)  # 【JDK 14+】
    case_kind: CaseKind = dataclasses.field(kw_only=True)  # 【JDK 14+】

    @staticmethod
    def create_rule(start_pos: int, end_pos: int, source: str,
                    labels: List[CaseLabel], guard: Expression,
                    statements: List[Statement], body: Optional[Tree]) -> "Case":
        return Case(
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
                         labels: List[CaseLabel], guard: Expression,
                         statements: List[Statement], body: Optional[Tree]) -> "Case":
        return Case(
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
class Catch(Tree):
    """try 语句中的 catch 代码块

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/CatchTree.java
    A tree node for a `catch` block in a `try` statement.

    样例：
    catch ( parameter )
        block
    """

    parameter: Variable = dataclasses.field(kw_only=True)
    block: Block = dataclasses.field(kw_only=True)

    @staticmethod
    def create(parameter: Variable,
               block: Block,
               start_pos: int, end_pos: int, source: str) -> "Catch":
        return Catch(
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
class Identifier(Expression):
    """标识符

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/IdentifierTree.java
    A tree node for an identifier expression.

    样例：name
    """

    name: str = dataclasses.field(kw_only=True)

    @staticmethod
    def create(name: str, start_pos: int, end_pos: int, source: str) -> "Identifier":
        return Identifier(
            kind=TreeKind.IDENTIFIER,
            name=name,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    @staticmethod
    def mock() -> "Identifier":
        return Identifier(
            kind=TreeKind.IDENTIFIER,
            name="Mock",
            start_pos=None,
            end_pos=None,
            source=None
        )

    def generate(self) -> str:
        return self.name


@dataclasses.dataclass(slots=True)
class TypeParameter(Tree):
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
    annotations: List[Annotation] = dataclasses.field(kw_only=True)

    @staticmethod
    def create(name: str, bounds: List[Tree], annotations: List[Annotation],
               start_pos: int, end_pos: int, source: str) -> "TypeParameter":
        return TypeParameter(
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
class Class(Statement):
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

    modifiers: Modifiers = dataclasses.field(kw_only=True)
    name: Optional[str] = dataclasses.field(kw_only=True)  # 如果为匿名类则为 None
    type_parameters: List[TypeParameter] = dataclasses.field(kw_only=True)
    extends_clause: Optional[Tree] = dataclasses.field(kw_only=True)  # 如果没有继承关系则为 None
    implements_clause: List[Tree] = dataclasses.field(kw_only=True)
    permits_clause: Optional[List[Tree]] = dataclasses.field(kw_only=True)  # 【JDK 17+】
    members: List[Tree] = dataclasses.field(kw_only=True)

    @staticmethod
    def create(modifiers: Modifiers,
               name: str,
               type_parameters: List[TypeParameter],
               extends_clause: Optional[Tree],
               implements_clause: List[Tree],
               permits_clause: Optional[List[Tree]],
               members: List[Tree],
               start_pos: int, end_pos: int, source: str) -> "Class":
        return Class(
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
    def create_anonymous_class(modifiers: Modifiers,
                               members: List[Tree],
                               start_pos: int, end_pos: int, source: str) -> "Class":
        return Class(
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

    def get_extends_and_implements(self) -> List[Tree]:
        """获取继承的类和实现的接口的列表"""
        result = []
        if self.extends_clause is not None:
            result.append(self.extends_clause)
        result.extend(self.implements_clause)
        return result

    def get_method_list(self) -> List["Method"]:
        """根据方法名获取 Method 对象"""
        method_list = []
        for member in self.members:
            if isinstance(member, Method):
                method_list.append(member)
        return method_list

    def get_method_by_name(self, method_name: str) -> Optional["Method"]:
        """根据方法名获取当前 Class 对象中的 Method 对象"""
        for member in self.members:
            if isinstance(member, Method) and member.name == method_name:
                return member
        return None

    def get_variable_list(self) -> List["Variable"]:
        """获取类属性的列表"""
        variable_list = []
        for member in self.members:
            if isinstance(member, Variable):
                variable_list.append(member)
        return variable_list

    def get_variable_by_name(self, variable_name: str) -> Optional["Variable"]:
        """获取类属性"""
        for member in self.members:
            if isinstance(member, Variable) and member.name == variable_name:
                return member
        return None

    def get_sub_class_name_list(self) -> List[str]:
        """获取子类的列表"""
        class_name_list = []
        for declaration in self.members:
            if isinstance(declaration, Class):
                class_name_list.append(declaration.name)
        return class_name_list


@dataclasses.dataclass(slots=True)
class Module(Tree):
    """声明模块【JDK 9+】

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/ModuleTree.java
    A tree node for a module declaration.

    样例：
    annotations
    [open] module module-name {
        directives
    }
    """

    annotations: List[Annotation] = dataclasses.field(kw_only=True)
    module_kind: ModuleKind = dataclasses.field(kw_only=True)
    name: Expression = dataclasses.field(kw_only=True)
    directives: List[Directive] = dataclasses.field(kw_only=True)

    @staticmethod
    def create(annotations: List[Annotation],
               module_kind: ModuleKind,
               name: Expression,
               directives: List[Directive],
               start_pos: int, end_pos: int, source: str) -> "Module":
        return Module(
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
class Package(Tree):
    """声明包【JDK 9+】

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/PackageTree.java
    Represents the package declaration.
    """

    annotations: List[Annotation] = dataclasses.field(kw_only=True)
    package_name: Expression = dataclasses.field(kw_only=True)

    @staticmethod
    def create(annotations: List[Annotation],
               package_name: Expression,
               start_pos: int, end_pos: int, source: str) -> "Package":
        return Package(
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
class Import(Tree):
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
               start_pos: int, end_pos: int, source: str) -> "Import":
        return Import(
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
                      start_pos: int, end_pos: int, source: str) -> "Import":
        return Import(
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
class CompilationUnit(Tree):
    """表示普通编译单元和模块编译单元的抽象语法树节点

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/CompilationUnitTree.java
    Represents the abstract syntax tree for ordinary compilation units and modular compilation units.

    TODO 增加 sourceFile、LineMap 的属性
    """

    module: Module = dataclasses.field(kw_only=True)  # 【JDK 17+】
    package: Package = dataclasses.field(kw_only=True)
    imports: List[Import] = dataclasses.field(kw_only=True)
    type_declarations: List[Tree] = dataclasses.field(kw_only=True)

    @staticmethod
    def create(module: Module,
               package: Package,
               imports: List[Import],
               type_declarations: List[Tree],
               start_pos: int, end_pos: int, source: str) -> "CompilationUnit":
        return CompilationUnit(
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
    def package_name(self) -> Expression:
        return self.package.package_name

    @property
    def package_annotations(self) -> List[Annotation]:
        return self.package.annotations

    def generate(self) -> str:
        """TODO"""

    def get_class_name_list(self) -> List[str]:
        """获取 file 中包含的类名的列表"""
        class_name_list = []
        for declaration in self.type_declarations:
            if isinstance(declaration, Class):
                class_name_list.append(declaration.name)
        return class_name_list

    def get_public_class(self) -> Optional[Class]:
        """获取文件中的公有类，如果没有则返回 None"""
        for class_declaration in self.get_class_declaration_list():
            if Modifier.PUBLIC in class_declaration.modifiers.flags:
                return class_declaration
        return None

    def get_class_declaration_list(self) -> List[Class]:
        """获取文件中的类对象，如果没有则返回空列表"""
        class_declaration_list = []
        for declaration in self.type_declarations:
            if isinstance(declaration, Class):
                class_declaration_list.append(declaration)
        return class_declaration_list

    def get_class_by_name(self, class_name: str) -> Optional[Class]:
        """根据类名获取类的抽象语法树节点"""
        for declaration in self.type_declarations:
            if isinstance(declaration, Class) and declaration.name == class_name:
                return declaration
        return None

    def get_sub_class_by_name(self, class_name: str) -> Optional[Class]:
        """根据子类名获取类的抽象语法树节点"""
        now_level_list = self.type_declarations
        class_node: Optional[Class] = None
        for now_level_class_name in class_name.split("."):
            class_node = None
            for declaration in now_level_list:
                if isinstance(declaration, Class) and declaration.name == now_level_class_name:
                    class_node = declaration
                    now_level_list = declaration.members
                    break
            if class_node is False:
                return None
        return class_node


@dataclasses.dataclass(slots=True)
class CompoundAssignment(Expression):
    """赋值表达式

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/CompoundAssignmentTree.java
    A tree node for compound assignment operator.
    Use `getKind` to determine the kind of operator.

    样例：
    - variable operator expression
    """

    variable: Expression = dataclasses.field(kw_only=True)
    expression: Expression = dataclasses.field(kw_only=True)

    @staticmethod
    def create(kind: TreeKind,
               variable: Expression,
               expression: Expression,
               start_pos: int, end_pos: int, source: str) -> "CompoundAssignment":
        return CompoundAssignment(
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
class ConditionalExpression(Expression):
    """三目表达式

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/ConditionalExpressionTree.java
    A tree node for the conditional operator `? :`.

    样例：condition ? trueExpression : falseExpression
    """

    condition: Expression = dataclasses.field(kw_only=True)
    true_expression: Expression = dataclasses.field(kw_only=True)
    false_expression: Expression = dataclasses.field(kw_only=True)

    @staticmethod
    def create(condition: Expression,
               true_expression: Expression,
               false_expression: Expression,
               start_pos: int, end_pos: int, source: str) -> "ConditionalExpression":
        return ConditionalExpression(
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
class ConstantCaseLabel(CaseLabel):
    """TODO 名称待整理

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/ConstantCaseLabelTree.java
    A case label element that refers to a constant expression
    """

    expression: Expression = dataclasses.field(kw_only=True)

    @staticmethod
    def create(expression: Expression,
               start_pos: int, end_pos: int, source: str) -> "ConstantCaseLabel":
        return ConstantCaseLabel(
            kind=TreeKind.CONSTANT_CASE_LABEL,
            expression=expression,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        """TODO"""


@dataclasses.dataclass(slots=True)
class Continue(Statement):
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
               start_pos: int, end_pos: int, source: str) -> "Continue":
        return Continue(
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
class DeconstructionPattern(Pattern):
    """【JDK 21+】TODO 名称待整理

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/DeconstructionPatternTree.java#L35
    A deconstruction pattern tree.
    """

    deconstructor: Expression = dataclasses.field(kw_only=True)
    nested_patterns: List[Pattern] = dataclasses.field(kw_only=True)

    @staticmethod
    def create(deconstructor: Expression, nested_patterns: List[Pattern],
               start_pos: int, end_pos: int, source: str) -> "DeconstructionPattern":
        return DeconstructionPattern(
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
class DoWhileLoop(Statement):
    """do while 语句

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/DoWhileLoopTree.java
    A tree node for a `do` statement.

    样例：
    do
        statement
    while ( expression );
    """

    condition: Expression = dataclasses.field(kw_only=True)
    statement: Statement = dataclasses.field(kw_only=True)

    @staticmethod
    def create(condition: Expression,
               statement: Statement,
               start_pos: int, end_pos: int, source: str) -> "DoWhileLoop":
        return DoWhileLoop(
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
class EmptyStatement(Statement):
    """空语句

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/EmptyStatementTree.java
    A tree node for an empty (skip) statement.

    样例：;
    """

    @staticmethod
    def create(start_pos: int, end_pos: int, source: str) -> "EmptyStatement":
        return EmptyStatement(
            kind=TreeKind.EMPTY_STATEMENT,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        return ";"


@dataclasses.dataclass(slots=True)
class EnhancedForLoop(Statement):
    """增强 for 循环语句

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/EnhancedForLoopTree.java
    A tree node for an "enhanced" `for` loop statement.

    样例：
    for ( variable : expression )
        statement
    """

    variable: Variable = dataclasses.field(kw_only=True)
    expression: Expression = dataclasses.field(kw_only=True)
    statement: Statement = dataclasses.field(kw_only=True)

    @staticmethod
    def create(variable: Variable,
               expression: Expression,
               statement: Statement,
               start_pos: int, end_pos: int, source: str) -> "EnhancedForLoop":
        return EnhancedForLoop(
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
class Erroneous(Expression):
    """格式错误的表达式

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/ErroneousTree.java
    A tree node to stand in for a malformed expression.
    """

    error_trees: Tree = dataclasses.field(kw_only=True)

    def generate(self) -> str:
        """TODO"""


@dataclasses.dataclass(slots=True)
class Exports(Directive):
    """模块声明语句中的 exports 指令【JDK 9+】

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/ExportsTree.java
    A tree node for an 'exports' directive in a module declaration.

    样例：
    - exports package-name;
    - exports package-name to module-name;
    """

    package_name: Expression = dataclasses.field(kw_only=True)
    module_names: List[Expression] = dataclasses.field(kw_only=True)

    @staticmethod
    def create(package_name: Expression,
               module_names: List[Expression],
               start_pos: int, end_pos: int, source: str) -> "Exports":
        return Exports(
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
class ExpressionStatement(Statement):
    """表达式语句

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/ExpressionStatementTree.java
    A tree node for an expression statement.

    样例：expression ;
    """

    expression: Expression = dataclasses.field(kw_only=True)

    @staticmethod
    def create(expression: Expression,
               start_pos: int, end_pos: int, source: str) -> "ExpressionStatement":
        return ExpressionStatement(
            kind=TreeKind.EXPRESSION_STATEMENT,
            expression=expression,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        return f"{self.expression.generate()};"


@dataclasses.dataclass(slots=True)
class ForLoop(Statement):
    """for 循环语句

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/ForLoopTree.java
    A tree node for a basic {@code for} loop statement.

    样例：
    for ( initializer ; condition ; update )
        statement
    """

    initializer: List[Statement] = dataclasses.field(kw_only=True)
    condition: Optional[Expression] = dataclasses.field(kw_only=True)
    update: List[ExpressionStatement] = dataclasses.field(kw_only=True)
    statement: Statement = dataclasses.field(kw_only=True)

    @staticmethod
    def create(initializer: initializer,
               condition: Optional[Expression],
               update: List[ExpressionStatement],
               statement: Statement,
               start_pos: int, end_pos: int, source: str) -> "ForLoop":
        return ForLoop(
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
class If(Statement):
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

    condition: Expression = dataclasses.field(kw_only=True)
    then_statement: Statement = dataclasses.field(kw_only=True)
    else_statement: Optional[Statement] = dataclasses.field(kw_only=True)

    @staticmethod
    def create(condition: Expression,
               then_statement: Statement,
               else_statement: Optional[Statement],
               start_pos: int, end_pos: int, source: str) -> "If":
        return If(
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
class InstanceOf(Expression):
    """instanceof 表达式

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/InstanceOfTree.java
    A tree node for an `instanceof` expression.
    
    样例：
    expression instanceof type
    expression instanceof type variable-name

    映射逻辑位置：CTree.JCInstanceOf
    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/tools/javac/tree/JCTree.java
    """

    expression: Expression = dataclasses.field(kw_only=True)
    instance_type: Tree = dataclasses.field(kw_only=True)
    pattern: Optional[Pattern] = dataclasses.field(kw_only=True)  # 【JDK 16+】

    @staticmethod
    def create(start_pos: int, end_pos: int, source: str,
               expression: Expression,
               pattern: Tree
               ) -> "InstanceOf":
        if isinstance(pattern, Pattern):
            if isinstance(pattern, BindingPattern):
                instance_type = pattern.variable.variable_type
            else:
                instance_type = None
            actual_pattern = pattern
        else:
            instance_type = pattern
            actual_pattern = None
        return InstanceOf(
            kind=TreeKind.INSTANCE_OF,
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
class IntersectionType(Tree):
    """强制类型转换表达式中的交叉类型

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/IntersectionTypeTree.java
    A tree node for an intersection type in a cast expression.
    """

    bounds: List[Tree] = dataclasses.field(kw_only=True)

    @staticmethod
    def create(bounds: List[Tree], start_pos: int, end_pos: int, source: str) -> "IntersectionType":
        return IntersectionType(
            kind=TreeKind.INTERSECTION_TYPE,
            bounds=bounds,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        return generate_tree_list(self.bounds, Separator.AMP)


@dataclasses.dataclass(slots=True)
class LabeledStatement(Statement):
    """包含标签的表达式

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/LabeledStatementTree.java
    A tree node for a labeled statement.

    样例：label : statement
    """

    label: str = dataclasses.field(kw_only=True)
    statement: Statement = dataclasses.field(kw_only=True)

    @staticmethod
    def create(label: str, statement: Statement,
               start_pos: int, end_pos: int, source: str) -> "LabeledStatement":
        return LabeledStatement(
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
class LambdaExpression(Expression):
    """lambda 表达式

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/LambdaExpressionTree.java
    A tree node for a lambda expression.

    样例：
    ()->{}
    (List<String> ls)->ls.size()
    (x,y)-> { return x + y; }
    """

    parameters: List[Variable] = dataclasses.field(kw_only=True)
    body: Tree = dataclasses.field(kw_only=True)
    body_kind: LambdaBodyKind = dataclasses.field(kw_only=True)

    @staticmethod
    def create_expression(parameters: List[Variable], body: Tree, start_pos: int, end_pos: int,
                          source: str) -> "LambdaExpression":
        return LambdaExpression(
            kind=TreeKind.LAMBDA_EXPRESSION,
            parameters=parameters,
            body=body,
            body_kind=LambdaBodyKind.EXPRESSION,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    @staticmethod
    def create_statement(parameters: List[Variable], body: Block, start_pos: int, end_pos: int,
                         source: str) -> "LambdaExpression":
        return LambdaExpression(
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
class Literal(Expression, abc.ABC):
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
class IntLiteral(Literal):
    """整型字面值（包括十进制、八进制、十六进制）"""

    style: IntegerStyle = dataclasses.field(kw_only=True)
    value: int = dataclasses.field(kw_only=True)

    @staticmethod
    def create(style: IntegerStyle, value: int, start_pos: int, end_pos: int, source: str) -> "IntLiteral":
        return IntLiteral(
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
class LongLiteral(Literal):
    """十进制长整型字面值（包括十进制、八进制、十六进制）"""

    style: IntegerStyle = dataclasses.field(kw_only=True)
    value: int = dataclasses.field(kw_only=True)

    @staticmethod
    def create(style: IntegerStyle, value: int, start_pos: int, end_pos: int, source: str) -> "LongLiteral":
        return LongLiteral(
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
class FloatLiteral(Literal):
    """单精度浮点数字面值"""

    value: float = dataclasses.field(kw_only=True)

    @staticmethod
    def create(value: float, start_pos: int, end_pos: int, source: str) -> "FloatLiteral":
        return FloatLiteral(
            kind=TreeKind.FLOAT_LITERAL,
            value=value,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        return f"{self.value}f"


@dataclasses.dataclass(slots=True)
class DoubleLiteral(Literal):
    """双精度浮点数字面值"""

    value: float = dataclasses.field(kw_only=True)

    @staticmethod
    def create(value: float, start_pos: int, end_pos: int, source: str) -> "DoubleLiteral":
        return DoubleLiteral(
            kind=TreeKind.DOUBLE_LITERAL,
            value=value,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        return f"{self.value}"


@dataclasses.dataclass(slots=True)
class TrueLiteral(Literal):
    """布尔值真值字面值"""

    @staticmethod
    def create(start_pos: int, end_pos: int, source: str) -> "TrueLiteral":
        return TrueLiteral(
            kind=TreeKind.BOOLEAN_LITERAL,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        return f"true"


@dataclasses.dataclass(slots=True)
class FalseLiteral(Literal):
    """布尔值假值字面值"""

    @staticmethod
    def create(start_pos: int, end_pos: int, source: str) -> "FalseLiteral":
        return FalseLiteral(
            kind=TreeKind.BOOLEAN_LITERAL,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        return f"false"


@dataclasses.dataclass(slots=True)
class CharacterLiteral(Literal):
    """字符字面值"""

    value: str = dataclasses.field(kw_only=True)  # 不包含单引号的字符串

    @staticmethod
    def create(value: str, start_pos: int, end_pos: int, source: str) -> "CharacterLiteral":
        return CharacterLiteral(
            kind=TreeKind.CHAR_LITERAL,
            value=value,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        return f"'{self.value}'"


@dataclasses.dataclass(slots=True)
class StringLiteral(Literal):
    """字符串字面值"""

    style: StringStyle = dataclasses.field(kw_only=True)  # 字面值样式
    value: str = dataclasses.field(kw_only=True)  # 不包含双引号的字符串内容

    @staticmethod
    def create_string(value: str, start_pos: int, end_pos: int, source: str) -> "StringLiteral":
        return StringLiteral(
            kind=TreeKind.STRING_LITERAL,
            style=StringStyle.STRING,
            value=value,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    @staticmethod
    def create_text_block(value: str, start_pos: int, end_pos: int, source: str) -> "StringLiteral":
        return StringLiteral(
            kind=TreeKind.STRING_LITERAL,
            style=StringStyle.TEXT_BLOCK,
            value=value,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def get_string_value(self) -> str:
        return self.value

    def generate(self) -> str:
        if self.style == StringStyle.STRING:
            return f"\"{repr(self.value)}\""
        return f"\"\"\"\n{repr(self.value)}\"\"\""


@dataclasses.dataclass(slots=True)
class NullLiteral(Literal):
    """空值字面值"""

    @staticmethod
    def create(start_pos: int, end_pos: int, source: str) -> "NullLiteral":
        return NullLiteral(
            kind=TreeKind.NULL_LITERAL,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        return f"null"


@dataclasses.dataclass(slots=True)
class MemberReference(Expression):
    """成员引用表达式

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/MemberReferenceTree.java
    A tree node for a member reference expression.

    样例：expression :: [ identifier | new ]
    """

    mode: ReferenceMode = dataclasses.field(kw_only=True)
    name: str = dataclasses.field(kw_only=True)
    expression: Expression = dataclasses.field(kw_only=True)
    type_arguments: Optional[List[Expression]] = dataclasses.field(kw_only=True)

    @staticmethod
    def create(mode: ReferenceMode,
               name: str,
               qualifier_expression: Expression,
               type_arguments: List[Expression],
               start_pos: int, end_pos: int, source: str) -> "MemberReference":
        return MemberReference(
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
class MemberSelect(Expression):
    """成员访问表达式

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/MemberSelectTree.java
    A tree node for a member access expression.

    样例：expression . identifier
    """

    expression: Expression = dataclasses.field(kw_only=True)
    identifier: Identifier = dataclasses.field(kw_only=True)

    @staticmethod
    def create(expression: Expression, identifier: Identifier,
               start_pos: int, end_pos: int, source: str) -> "MemberSelect":
        return MemberSelect(
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
class MethodInvocation(Expression):
    """方法调用表达式

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/MethodInvocationTree.java
    A tree node for a method invocation expression.

    样例：
    - identifier ( arguments )
    - this . typeArguments identifier ( arguments )
    """

    type_arguments: List[Tree] = dataclasses.field(kw_only=True)  # 泛型
    method_select: Expression = dataclasses.field(kw_only=True)  # 方法名
    arguments: List[Expression] = dataclasses.field(kw_only=True)  # 参数

    @staticmethod
    def create(type_arguments: List[Tree],
               method_select: Expression,
               arguments: List[Expression],
               start_pos: int, end_pos: int, source: str) -> "MethodInvocation":
        return MethodInvocation(
            kind=TreeKind.METHOD_INVOCATION,
            type_arguments=type_arguments,
            method_select=method_select,
            arguments=arguments,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        if self.type_arguments:
            type_arguments = "<" + generate_tree_list(self.type_arguments, sep=Separator.COMMA) + ">"
        else:
            type_arguments = ""
        arguments = generate_tree_list(self.arguments, sep=Separator.COMMA)
        return f"{self.method_select.generate()}{type_arguments}({arguments})"


@dataclasses.dataclass(slots=True)
class Method(Tree):
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

    modifiers: Modifiers = dataclasses.field(kw_only=True)
    name: str = dataclasses.field(kw_only=True)
    return_type: Tree = dataclasses.field(kw_only=True)
    type_parameters: List[TypeParameter] = dataclasses.field(kw_only=True)
    receiver_parameter: Variable = dataclasses.field(kw_only=True)
    parameters: List[Variable] = dataclasses.field(kw_only=True)
    throws: List[Expression] = dataclasses.field(kw_only=True)
    block: Block = dataclasses.field(kw_only=True)
    default_value: Tree = dataclasses.field(kw_only=True)

    @staticmethod
    def create(modifiers: Modifiers,
               name: str,
               return_type: Tree,
               type_parameters: List[TypeParameter],
               receiver_parameter: Optional[Variable],
               parameters: List[Variable],
               throws: List[Expression],
               block: Block,
               default_value: Tree,
               start_pos: int, end_pos: int, source: str) -> "Method":
        return Method(
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
class NewArray(Expression):
    """初始化数组表达式

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/NewArrayTree.java
    A tree node for an expression to create a new instance of an array.

    样例 1：new type dimensions initializers
    样例 2：new type dimensions [ ] initializers
    """

    array_type: Optional[Expression] = dataclasses.field(kw_only=True)
    dimensions: List[Expression] = dataclasses.field(kw_only=True)
    initializers: List[Expression] = dataclasses.field(kw_only=True)
    annotations: Optional[List[Annotation]] = dataclasses.field(kw_only=True, default=None)
    dim_annotations: Optional[List[List[Annotation]]] = dataclasses.field(kw_only=True, default=None)

    @staticmethod
    def create(array_type: Optional[Expression],
               dimensions: List[Expression],
               initializers: List[Expression],
               dim_annotations: Optional[List[List[Annotation]]],
               start_pos: int, end_pos: int, source: str) -> "NewArray":
        return NewArray(
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
class NewClass(Expression):
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

    enclosing_expression: Optional[Expression] = dataclasses.field(kw_only=True)
    type_arguments: List[Tree] = dataclasses.field(kw_only=True)
    identifier: Expression = dataclasses.field(kw_only=True)
    arguments: List[Expression] = dataclasses.field(kw_only=True)
    class_body: Optional[Class] = dataclasses.field(kw_only=True)

    @staticmethod
    def create(enclosing: Optional[Expression],
               type_arguments: List[Tree],
               identifier: Expression,
               arguments: List[Expression],
               class_body: Optional[Class],
               start_pos: int, end_pos: int, source: str) -> "NewClass":
        return NewClass(
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
class Opens(Directive):
    """模块声明中的 opens 指令

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/OpensTree.java
    A tree node for an 'opens' directive in a module declaration.

    样例 1:
    opens package-name;

    样例 2:
    opens package-name to module-name;
    """

    package_name: Expression = dataclasses.field(kw_only=True)
    module_names: List[Expression] = dataclasses.field(kw_only=True)

    @staticmethod
    def create(package_name: Expression,
               module_names: List[Expression],
               start_pos: int, end_pos: int, source: str) -> "Opens":
        return Opens(
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
class ParameterizedType(Type):
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
               start_pos: int, end_pos: int, source: str) -> "ParameterizedType":
        return ParameterizedType(
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
class Parenthesized(Expression):
    """括号表达式

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/ParenthesizedTree.java
    A tree node for a parenthesized expression.
    Note: parentheses not be preserved by the parser.

    样例:
    ( expression )
    """

    expression: Expression = dataclasses.field(kw_only=True)

    @staticmethod
    def create(expression: Expression, start_pos: int, end_pos: int, source: str) -> "Parenthesized":
        return Parenthesized(
            kind=TreeKind.PARENTHESIZED,
            expression=expression,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        return f"({self.expression.generate()})"


@dataclasses.dataclass(slots=True)
class PatternCaseLabel(CaseLabel):
    """【JDK 21+】TODO 名称待整理

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/PatternCaseLabelTree.java
    A case label element that refers to an expression
    """

    pattern: Pattern = dataclasses.field(kw_only=True)

    @staticmethod
    def create(pattern: Pattern, start_pos: int, end_pos: int, source: str) -> "PatternCaseLabel":
        return PatternCaseLabel(
            kind=TreeKind.PATTERN_CASE_LABEL,
            pattern=pattern,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    @staticmethod
    def mock() -> "PatternCaseLabel":
        return PatternCaseLabel(
            kind=TreeKind.PATTERN_CASE_LABEL,
            pattern=AnyPattern.mock(),
            start_pos=None,
            end_pos=None,
            source=None
        )

    def generate(self) -> str:
        """TODO"""


@dataclasses.dataclass(slots=True)
class PrimitiveType(Type):
    """原生类型

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/PrimitiveTypeTree.java
    A tree node for a primitive type.

    样例：
    primitiveTypeKind
    """

    type_kind: TypeKind = dataclasses.field(kw_only=True)

    @staticmethod
    def create(type_kind: TypeKind, start_pos: int, end_pos: int, source: str) -> "PrimitiveType":
        return PrimitiveType(
            kind=TreeKind.PRIMITIVE_TYPE,
            type_kind=type_kind,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    @staticmethod
    def create_void(start_pos: int, end_pos: int, source: str) -> "PrimitiveType":
        return PrimitiveType(
            kind=TreeKind.PRIMITIVE_TYPE,
            type_kind=TypeKind.VOID,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    @staticmethod
    def mock() -> "PrimitiveType":
        return PrimitiveType(
            kind=TreeKind.PRIMITIVE_TYPE,
            type_kind=TypeKind.MOCK,
            start_pos=None,
            end_pos=None,
            source=None
        )

    def generate(self) -> str:
        return self.type_kind.value


@dataclasses.dataclass(slots=True)
class Provides(Directive):
    """模块声明语句的 provides 指令【JDK 9+】

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/ProvidesTree.java
    A tree node for a 'provides' directive in a module declaration.

    样例:
    provides service-name with implementation-name;
    """

    service_name: Expression = dataclasses.field(kw_only=True)
    implementation_names: List[Expression] = dataclasses.field(kw_only=True)

    @staticmethod
    def create(service_name: Expression,
               implementation_names: List[Expression],
               start_pos: int, end_pos: int, source: str) -> "Provides":
        return Provides(
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
class Requires(Directive):
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
    module_name: Expression = dataclasses.field(kw_only=True)

    @staticmethod
    def create(is_static: bool,
               is_transitive: bool,
               module_name: Expression,
               start_pos: int, end_pos: int, source: str) -> "Requires":
        return Requires(
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
class Return(Statement):
    """返回语句

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/ReturnTree.java
    A tree node for a `return` statement.

    样例 1:
    return;

    样例 2:
    return expression ;
    """

    expression: Optional[Expression] = dataclasses.field(kw_only=True)

    @staticmethod
    def create(expression: Expression,
               start_pos: int, end_pos: int, source: str) -> "Return":
        return Return(
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
class SwitchExpression(Expression):
    """switch 表达式【JDK 14+】

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/SwitchExpressionTree.java
    A tree node for a `switch` expression.

    样例:
    switch ( expression ) {
        cases
    }
    """

    expression: Expression = dataclasses.field(kw_only=True)
    cases: List[Case] = dataclasses.field(kw_only=True)

    @staticmethod
    def create(expression: Expression,
               cases: List[Case],
               start_pos: int, end_pos: int, source: str) -> "SwitchExpression":
        return SwitchExpression(
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
class Switch(Statement):
    """switch 语句

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/SwitchTree.java
    A tree node for a `switch` statement.

    样例:
    switch ( expression ) {
        cases
    }
    """

    expression: Expression = dataclasses.field(kw_only=True)
    cases: List[Case] = dataclasses.field(kw_only=True)

    @staticmethod
    def create(expression: Expression,
               cases: List[Case],
               start_pos: int, end_pos: int, source: str) -> "Switch":
        return Switch(
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
class Synchronized(Statement):
    """同步代码块语句

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/SynchronizedTree.java
    A tree node for a `synchronized` statement.

    样例:
    synchronized ( expression )
        block
    """

    expression: Expression = dataclasses.field(kw_only=True)
    block: Block = dataclasses.field(kw_only=True)

    @staticmethod
    def create(expression: Expression,
               block: Block,
               start_pos: int, end_pos: int, source: str) -> "Synchronized":
        return Synchronized(
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
class Throw(Statement):
    """throw 语句

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/ThrowTree.java
    A tree node for a `throw` statement.

    样例:
    throw expression;
    """

    expression: Expression = dataclasses.field(kw_only=True)

    @staticmethod
    def create(expression: Expression,
               start_pos: int, end_pos: int, source: str) -> "Throw":
        return Throw(
            kind=TreeKind.THROW,
            expression=expression,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        return f"throw {self.expression.generate()};"


@dataclasses.dataclass(slots=True)
class Try(Statement):
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

    block: Block = dataclasses.field(kw_only=True)
    catches: List[Catch] = dataclasses.field(kw_only=True)
    finally_block: Optional[Block] = dataclasses.field(kw_only=True)
    resources: List[Tree] = dataclasses.field(kw_only=True)

    @staticmethod
    def create(block: Block,
               catches: List[Catch],
               finally_block: Optional[Block],
               resources: List[Tree],
               start_pos: int, end_pos: int, source: str) -> "Try":
        return Try(
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
class TypeCast(Expression):
    """强制类型转换表达式

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/TypeCastTree.java
    A tree node for a type cast expression.

    样例:
    ( type ) expression
    """

    cast_type: Tree = dataclasses.field(kw_only=True)
    expression: Expression = dataclasses.field(kw_only=True)

    @staticmethod
    def create(cast_type: Tree, expression: Expression, start_pos: int, end_pos: int,
               source: str) -> "TypeCast":
        return TypeCast(
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
class Unary(Expression):
    """一元表达式

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/UnaryTree.java
    A tree node for postfix and unary expressions.
    Use `getKind` to determine the kind of operator.

    样例 1:
    operator expression

    样例 2:
    expression operator
    """

    expression: Expression = dataclasses.field(kw_only=True)

    @staticmethod
    def create(kind: TreeKind, expression: Expression, start_pos: int, end_pos: int, source: str) -> "Unary":
        return Unary(
            kind=kind,
            expression=expression,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        """TODO"""


@dataclasses.dataclass(slots=True)
class UnionType(Type):
    """TODO 名称待整理

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/UnionTypeTree.java
    A tree node for a union type expression in a multicatch variable declaration.
    """

    type_alternatives: List[Tree] = dataclasses.field(kw_only=True)

    @staticmethod
    def create(type_alternatives: List[Tree],
               start_pos: int, end_pos: int, source: str) -> "UnionType":
        return UnionType(
            kind=TreeKind.UNION_TYPE,
            type_alternatives=type_alternatives,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        """TODO"""


@dataclasses.dataclass(slots=True)
class Uses(Directive):
    """模块声明语句中的 uses 指令【JDK 9+】

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/UsesTree.java
    A tree node for a 'uses' directive in a module declaration.

    样例 1:
    uses service-name;
    """

    service_name: Expression = dataclasses.field(kw_only=True)

    @staticmethod
    def create(service_name: Expression,
               start_pos: int, end_pos: int, source: str) -> "Uses":
        return Uses(
            kind=TreeKind.USES,
            service_name=service_name,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        return f"uses {self.service_name.generate()};"


@dataclasses.dataclass(slots=True)
class WhileLoop(Statement):
    """while 循环语句

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/WhileLoopTree.java
    A tree node for a `while` loop statement.

    样例 1:
    while ( condition )
        statement
    """

    condition: Expression = dataclasses.field(kw_only=True)
    statement: Statement = dataclasses.field(kw_only=True)

    @staticmethod
    def create(condition: Expression,
               statement: Statement,
               start_pos: int, end_pos: int, source: str) -> "WhileLoop":
        return WhileLoop(
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
class Wildcard(Expression):
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
    def create_extends_wildcard(bound: Tree, start_pos: int, end_pos: int, source: str) -> "Wildcard":
        return Wildcard(
            kind=TreeKind.EXTENDS_WILDCARD,
            bound=bound,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    @staticmethod
    def create_super_wildcard(bound: Tree, start_pos: int, end_pos: int, source: str) -> "Wildcard":
        return Wildcard(
            kind=TreeKind.SUPER_WILDCARD,
            bound=bound,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    @staticmethod
    def create_unbounded_wildcard(start_pos: int, end_pos: int, source: str) -> "Wildcard":
        return Wildcard(
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
class Yield(Statement):
    """yield 语句

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/YieldTree.java
    A tree node for a `yield` statement.

    样例 1:
    yield expression;
    """

    value: Expression = dataclasses.field(kw_only=True)

    @staticmethod
    def create(value: Expression, start_pos: int, end_pos: int, source: str) -> "Yield":
        return Yield(
            kind=TreeKind.YIELD,
            value=value,
            start_pos=start_pos,
            end_pos=end_pos,
            source=source
        )

    def generate(self) -> str:
        return f"yield {self.value.generate()};"

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
    "IntersectionTypeTree",  # 交互类型
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

    type: Tree = dataclasses.dataclass(slots=True)

    def generate(self) -> str:
        return f"{self.type.generate()}[]"


@dataclasses.dataclass(slots=True)
class AssertTree(StatementTree):
    """assert 语句

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/AssertTree.java
    A tree node for an `assert` statement.

    样例：
    - assert condition ;
    - assert condition : detail ;
    """

    condition: ExpressionTree = dataclasses.field(kw_only=True)
    detail: Optional[ExpressionTree] = dataclasses.field(kw_only=True)

    def generate(self) -> str:
        if self.detail is not None:
            return f"assert {self.condition.generate()} : {self.detail.generate()} ;"
        return f"assert {self.condition.generate()} ;"


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

    def generate(self) -> str:
        if len(self.annotations) > 0:
            return (f"{generate_enum_list(self.flags, Separator.SPACE)} "
                    f"{generate_tree_list(self.annotations, Separator.SPACE)}")
        return f"{generate_enum_list(self.flags, Separator.SPACE)}"


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
    name: str = dataclasses.field(kw_only=True)
    name_expression: ExpressionTree = dataclasses.field(kw_only=True)
    type: Tree = dataclasses.field(kw_only=True)
    initializer: ExpressionTree = dataclasses.field(kw_only=True)

    def generate(self) -> str:
        """TODO"""


@dataclasses.dataclass(slots=True)
class BindingPatternTree(PatternTree):
    """【JDK 16+】TODO 名称待整理

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/BindingPatternTree.java
    A binding pattern tree
    """

    variable: VariableTree = dataclasses.field(kw_only=True)

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

    expressions: List[ExpressionTree] = dataclasses.field(kw_only=True)
    labels: List[CaseLabelTree] = dataclasses.field(kw_only=True)  # 【JDK 21+】
    guard: ExpressionTree = dataclasses.field(kw_only=True)  # 【JDK 21+】
    statements: List[StatementTree] = dataclasses.field(kw_only=True)
    body: Optional[Tree] = dataclasses.field(kw_only=True)  # 【JDK 14+】
    case_kind: CaseKind = dataclasses.field(kw_only=True)  # 【JDK 14+】

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

    def generate(self) -> str:
        return f"catch ({self.parameter.generate()}) {self.block.generate()}"


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
    simple_name: str = dataclasses.field(kw_only=True)
    type_parameters: List[TypeParameterTree] = dataclasses.field(kw_only=True)
    extends_clause: Tree = dataclasses.field(kw_only=True)
    implements_clause: Tree = dataclasses.field(kw_only=True)
    permits_clause: List[Tree] = dataclasses.field(kw_only=True)  # 【JDK 17+】
    members: List[Tree] = dataclasses.field(kw_only=True)

    def generate(self) -> str:
        """TODO"""


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
    module_type: ModuleKind = dataclasses.field(kw_only=True)
    name: ExpressionTree = dataclasses.field(kw_only=True)
    directives: List[DirectiveTree] = dataclasses.field(kw_only=True)

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
    module: bool = dataclasses.field(kw_only=True)
    qualified_identifier: Tree = dataclasses.field(kw_only=True)

    def generate(self) -> str:
        """TODO"""


@dataclasses.dataclass(slots=True)
class CompilationUnitTree(Tree):
    """表示普通编译单元和模块化编译单元的抽象语法树节点

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/CompilationUnitTree.java
    Represents the abstract syntax tree for ordinary compilation units and modular compilation units.

    TODO 增加 sourceFile、LineMap 的属性
    """

    module: ModuleTree = dataclasses.field(kw_only=True)  # 【JDK 17+】
    package_annotations: List[AnnotationTree] = dataclasses.field(kw_only=True)
    package_name: ExpressionTree = dataclasses.field(kw_only=True)
    package: PackageTree = dataclasses.field(kw_only=True)
    imports: List[ImportTree] = dataclasses.field(kw_only=True)
    type_decls: List[Tree] = dataclasses.field(kw_only=True)

    def generate(self) -> str:
        """TODO"""


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

    def generate(self) -> str:
        return f"{self.condition.generate()} ? {self.true_expression.generate()} : {self.false_expression.generate()}"


@dataclasses.dataclass(slots=True)
class ConstantCaseLabelTree(CaseLabelTree):
    """TODO 名称待整理

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/ConstantCaseLabelTree.java
    A case label element that refers to a constant expression
    """

    constant_expression: ExpressionTree = dataclasses.field(kw_only=True)

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
    statement: ExpressionTree = dataclasses.field(kw_only=True)

    def generate(self) -> str:
        return f"do {self.statement.generate()} while ({self.condition.generate()});"


@dataclasses.dataclass(slots=True)
class EmptyStatementTree(StatementTree):
    """空语句

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/EmptyStatementTree.java
    A tree node for an empty (skip) statement.

    样例：;
    """

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

    def generate(self) -> str:
        return (f"for ({self.variable.generate()} : {self.expression.generate()}) \n"
                f"    {self.statement.generate()}")


@dataclasses.dataclass(slots=True)
class ErroneousTree(ExpressionTree):
    """TODO 名称待整理

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
    condition: ExpressionTree = dataclasses.field(kw_only=True)
    update: List[ExpressionStatementTree] = dataclasses.field(kw_only=True)
    statement: StatementTree = dataclasses.field(kw_only=True)

    def generate(self) -> str:
        """TODO"""


@dataclasses.dataclass(slots=True)
class IdentifierTree(ExpressionTree):
    """标识符

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/IdentifierTree.java
    A tree node for an identifier expression.

    样例：name
    """

    name: str = dataclasses.field(kw_only=True)

    def generate(self) -> str:
        return self.name


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
    """

    expression: ExpressionTree = dataclasses.field(kw_only=True)
    type: Tree = dataclasses.field(kw_only=True)
    pattern: Optional[PatternTree] = dataclasses.field(kw_only=True)  # 【JDK 16+】

    def generate(self) -> str:
        if self.pattern is None:
            return f"{self.expression.generate()} instanceof {self.type.generate()}"
        return f"{self.expression.generate()} instanceof {self.type.generate()} {self.pattern.generate()}"


@dataclasses.dataclass(slots=True)
class IntersectionTypeTree(Tree):
    """交叉类型

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/IntersectionTypeTree.java
    A tree node for an intersection type in a cast expression.
    """

    bounds: List[Tree] = dataclasses.field(kw_only=True)

    def generate(self) -> str:
        """TODO"""


@dataclasses.dataclass(slots=True)
class LabeledStatementTree(StatementTree):
    """包含标签的表达式

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/LabeledStatementTree.java
    A tree node for a labeled statement.

    样例：label : statement
    """

    label: str = dataclasses.field(kw_only=True)
    statement: StatementTree = dataclasses.field(kw_only=True)

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

    def generate(self) -> str:
        return f"({generate_tree_list(self.parameters, Separator.COMMA)}) -> {self.body.generate()}"


@dataclasses.dataclass(slots=True)
class LiteralTree(Tree, abc.ABC):
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

    def generate(self) -> str:
        return change_int_to_string(self.value, self.style)


@dataclasses.dataclass(slots=True)
class LongLiteralTree(LiteralTree):
    """十进制长整型字面值（包括十进制、八进制、十六进制）"""

    style: IntegerStyle = dataclasses.field(kw_only=True)
    value: int = dataclasses.field(kw_only=True)

    def generate(self) -> str:
        return f"{self.value}L"


@dataclasses.dataclass(slots=True)
class FloatLiteralTree(LiteralTree):
    """单精度浮点数字面值"""

    value: float = dataclasses.field(kw_only=True)

    def generate(self) -> str:
        return f"{self.value}f"


@dataclasses.dataclass(slots=True)
class DoubleLiteralTree(LiteralTree):
    """双精度浮点数字面值"""

    value: float = dataclasses.field(kw_only=True)

    def generate(self) -> str:
        return f"{self.value}"


@dataclasses.dataclass(slots=True)
class TrueLiteralTree(LiteralTree):
    """布尔值真值字面值"""

    def generate(self) -> str:
        return f"true"


@dataclasses.dataclass(slots=True)
class FalseLiteralTree(LiteralTree):
    """布尔值假值字面值"""

    def generate(self) -> str:
        return f"false"


@dataclasses.dataclass(slots=True)
class CharacterLiteralTree(LiteralTree):
    """字符字面值"""

    value: str = dataclasses.field(kw_only=True)  # 不包含单引号的字符串

    def generate(self) -> str:
        return f"'{self.value}'"


@dataclasses.dataclass(slots=True)
class StringLiteralTree(LiteralTree):
    """字符串字面值"""

    style: StringStyle = dataclasses.field(kw_only=True)  # 字面值样式
    value: str = dataclasses.field(kw_only=True)  # 不包含双引号的字符串内容

    def generate(self) -> str:
        if self.style == StringStyle.STRING:
            return f"\"{repr(self.value)}\""
        return f"\"\"\"\n{repr(self.value)}\"\"\""


@dataclasses.dataclass(slots=True)
class NullLiteralTree(LiteralTree):
    """空值字面值"""

    def generate(self) -> str:
        return f"null"


@dataclasses.dataclass(slots=True)
class MemberReferenceTree(ExpressionTree):
    """成员引用表达式

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/MemberReferenceTree.java
    A tree node for a member reference expression.

    样例：expression # [ identifier | new ]
    """

    mode: ReferenceMode = dataclasses.field(kw_only=True)
    qualifier_expression: ExpressionTree = dataclasses.field(kw_only=True)
    name: str = dataclasses.field(kw_only=True)
    type_arguments: List[ExpressionTree] = dataclasses.field(kw_only=True)

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
    identifier: str = dataclasses.field(kw_only=True)

    def generate(self) -> str:
        return f"{self.expression.generate()}.{self.identifier}"


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

    def generate(self) -> str:
        """TODO"""


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
    throws: List[ExpressionTree] = dataclasses.field(kw_only=True)
    default_value: Tree = dataclasses.field(kw_only=True)

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

    type: Tree = dataclasses.field(kw_only=True)
    dimensions: List[ExpressionTree] = dataclasses.field(kw_only=True)
    initializers: List[ExpressionTree] = dataclasses.field(kw_only=True)
    annotations: List[AnnotationTree] = dataclasses.field(kw_only=True)
    dim_annotations: List[List[AnnotationTree]] = dataclasses.field(kw_only=True)

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
    module_name: List[ExpressionTree] = dataclasses.field(kw_only=True)

    def generate(self) -> str:
        """TODO"""


@dataclasses.dataclass(slots=True)
class ParameterizedTypeTree(Tree):
    """包含类型参数的类型表达式

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/ParameterizedTypeTree.java
    A tree node for a type expression involving type parameters.

    样例:
    type < typeArguments >
    """

    type: Tree = dataclasses.field(kw_only=True)
    type_arguments: List[Tree] = dataclasses.field(kw_only=True)

    def generate(self) -> str:
        return f"{self.type.generate()}<{generate_tree_list(self.type_arguments, Separator.COMMA)}>"


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

    def generate(self) -> str:
        return f"({self.expression.generate()})"


@dataclasses.dataclass(slots=True)
class PatternCaseLabelTree(CaseLabelTree):
    """【JDK 21+】TODO 名称待整理

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/PatternCaseLabelTree.java
    A case label element that refers to an expression
    """

    pattern: PatternTree = dataclasses.field(kw_only=True)

    def generate(self) -> str:
        """TODO"""


@dataclasses.dataclass(slots=True)
class PrimitiveTypeTree(Tree):
    """原生类型

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/PrimitiveTypeTree.java
    A tree node for a primitive type.

    样例：
    primitiveTypeKind
    """

    primitive_type_kind: TypeKind = dataclasses.field(kw_only=True)

    def generate(self) -> str:
        return self.primitive_type_kind.value


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

    type: Tree = dataclasses.field(kw_only=True)
    expression: ExpressionTree = dataclasses.field(kw_only=True)

    def generate(self) -> str:
        return f"({self.type.generate()}){self.expression.generate()}"


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

    def generate(self) -> str:
        """TODO"""


@dataclasses.dataclass(slots=True)
class UnionTypeTree(Tree):
    """TODO 名称待整理

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/UnionTypeTree.java
    A tree node for a union type expression in a multicatch variable declaration.
    """

    type_alternatives: List[Tree] = dataclasses.field(kw_only=True)

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

    def generate(self) -> str:
        return (f"while ({self.condition.generate()}) \n"
                f"    {self.statement.generate()}")


@dataclasses.dataclass(slots=True)
class WildcardTree(ExpressionTree):
    """通配符

    与 JDK 中 com.sun.source.tree.WildcardTree 接口的继承关系不一致，是因为 con.sun.tools.javac.tree.JCTree 类继承了 JCExpression，详见：
    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/tools/javac/tree/JCTree.java

    【JDK 接口源码】https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/WildcardTree.java
    A tree node for a wildcard type argument.
    Use `getKind` to determine the kind of bound.

    样例 1:
    ?

    样例 2:
    ? extends bound

    样例 3:
    ? super bound
    """

    bound: Tree = dataclasses.field(kw_only=True)

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

    def generate(self) -> str:
        return f"yield {self.value.generate()};"

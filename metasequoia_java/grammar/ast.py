import abc
import dataclasses
import enum
from typing import List, Optional

from metasequoia_java.grammar.ast_kind import TreeKind
from metasequoia_java.grammar.constants import CaseKind
from metasequoia_java.grammar.constants import IntegerStyle
from metasequoia_java.grammar.constants import ModuleKind
from metasequoia_java.grammar.constants import StringStyle
from metasequoia_java.grammar.element import Modifier
from metasequoia_java.grammar.utils import change_int_to_string

__all__ = [
    # ------------------------------ 抽象语法树节点的抽象基类 ------------------------------
    "Tree",  # 抽象语法树节点的抽象基类

    # ------------------------------ 抽象语法树节点的抽象类 ------------------------------
    "ExpressionTree",  # 各类表达式节点的抽象基类
    "PatternTree",  # 【JDK 16+】
    "AnyPatternTree",  # 【JDK 22+】
    "StatementTree",  # 各类语句节点的抽象基类
    "CaseLabelTree",  # 【JDK 21+】
    "DirectiveTree",  # 模块中所有指令的超类型【JDK 9+】
    "DefaultCaseLabelTree",  # 【JDK 21+】

    # ------------------------------ 抽象语法树节点的实体类 ------------------------------
    "AnnotationTree",  # 注解
    "AnnotatedTypeTree",  # 包含注解的类型
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
    "DoWhileLoopTree",  # do while 语句【JDK 21+】
    "EmptyStatementTree",  # 空语句
    "EnhancedForLoopTree",  # 增强 for 循环语句
    "ErroneousTree",
    "ExportsTree",  # 模块声明语句中的 exports 指令【JDK 9+】
    "ImportTree",  # 声明引用
    "ModuleTree",  # 声明模块【JDK 9+】
    "PackageTree",  # 声明包【JDK 9+】
    "TypeParameterTree",  # 类型参数列表
    "VariableTree",  # 声明变量

    # ------------------------------ Chapter 3 : Lexical Structure ------------------------------
    "Literal",
    "IntLiteral",  # 十进制整型字面值
    "LongLiteral",  # 十进制长整型字面值
    "FloatLiteral",  # 十进制单精度浮点数字面值
    "DoubleLiteral",  # 十进制双精度浮点数字面值
    "CharacterLiteral",  # 字符字面值
    "StringLiteral",  # 字符串字面值
    "TrueLiteral",  # 布尔值真值字面值
    "FalseLiteral",  # 布尔值假值字面值
    "NullLiteral",  # 空值字面值
]

COMMA = ","
SPACE = " "
SEMI = " "


# ------------------------------ 抽象基类 ------------------------------

@dataclasses.dataclass(slots=True)
class Tree(abc.ABC):
    """抽象语法树节点的抽象基类

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/Tree.java
    Common interface for all nodes in an abstract syntax tree.
    """

    kind: TreeKind = dataclasses.field(kw_only=True)  # 节点类型
    source: Optional[str] = dataclasses.field(kw_only=True)  # 原始代码

    @property
    def is_literal(self) -> bool:
        return False

    @abc.abstractmethod
    def generate(self) -> str:
        """生成当前节点元素的标准格式代码"""


@dataclasses.dataclass(slots=True)
class ExpressionTree(Tree, abc.ABC):
    """各类表达式节点的抽象基类

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/ExpressionTree.java
    A tree node used as the base class for the different types of expressions.
    """


@dataclasses.dataclass(slots=True)
class PatternTree(Tree, abc.ABC):
    """【JDK 16+】TODO 名称待整理

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/PatternTree.java
    A tree node used as the base class for the different kinds of patterns.
    """


@dataclasses.dataclass(slots=True)
class AnyPatternTree(PatternTree, abc.ABC):
    """【JDK 22+】TODO 名称待整理

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/AnyPatternTree.java
    A tree node for a binding pattern that matches a pattern with a variable of any name and a type of the match
    candidate; an unnamed pattern.

    使用下划线 `_` 的样例：
    if (r instanceof R(_)) {}
    """


@dataclasses.dataclass(slots=True)
class StatementTree(Tree, abc.ABC):
    """各类语句节点的抽象基类

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/StatementTree.java
    A tree node used as the base class for the different kinds of statements.
    """


@dataclasses.dataclass(slots=True)
class CaseLabelTree(Tree, abc.ABC):
    """TODO 名称待整理

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/CaseLabelTree.java
    A marker interface for Trees that may be used as CaseTree labels.
    """


@dataclasses.dataclass(slots=True)
class DirectiveTree(Tree, abc.ABC):
    """模块中所有指令的超类型【JDK 9+】

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/DirectiveTree.java
    A super-type for all the directives in a ModuleTree.
    """


@dataclasses.dataclass(slots=True)
class DefaultCaseLabelTree(Tree, abc.ABC):
    """【JDK 21+】TODO 名称待整理

    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/DefaultCaseLabelTree.java
    A case label that marks `default` in `case null, default`.
    """


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
            return f"@{self.annotation_type.generate()}({generate_tree_list(self.arguments, COMMA)})"
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
        return f"{generate_tree_list(self.annotations, SPACE)} {self.underlying_type.generate()}"


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
            return f"{generate_enum_list(self.flags, SPACE)} {generate_tree_list(self.annotations, SPACE)}"
        return f"{generate_enum_list(self.flags, SPACE)}"


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
        return f"{static_str}{{{generate_tree_list(self.statements, SEMI)}}}"


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


# ------------------------------------------------------------------------------------------


@dataclasses.dataclass(slots=True)
class Literal(Tree, abc.ABC):

    @property
    def is_literal(self) -> bool:
        return True


@dataclasses.dataclass(slots=True)
class IntLiteral(Literal):
    """整型字面值（包括十进制、八进制、十六进制）"""

    style: IntegerStyle = dataclasses.field(kw_only=True)
    value: int = dataclasses.field(kw_only=True)

    def generate(self) -> str:
        return change_int_to_string(self.value, self.style)


@dataclasses.dataclass(slots=True)
class LongLiteral(Literal):
    """十进制长整型字面值"""

    style: IntegerStyle = dataclasses.field(kw_only=True)
    value: int = dataclasses.field(kw_only=True)

    def generate(self) -> str:
        return f"{self.value}L"


@dataclasses.dataclass(slots=True)
class FloatLiteral(Literal):
    """十进制单精度浮点数字面值"""

    value: float = dataclasses.field(kw_only=True)

    def generate(self) -> str:
        return f"{self.value}f"


@dataclasses.dataclass(slots=True)
class DoubleLiteral(Literal):
    """十进制双精度浮点数字面值"""

    value: float = dataclasses.field(kw_only=True)

    def generate(self) -> str:
        return f"{self.value}"


@dataclasses.dataclass(slots=True)
class TrueLiteral(Literal):
    """布尔值真值字面值"""

    def generate(self) -> str:
        return f"true"


@dataclasses.dataclass(slots=True)
class FalseLiteral(Literal):
    """布尔值假值字面值"""

    def generate(self) -> str:
        return f"false"


@dataclasses.dataclass(slots=True)
class CharacterLiteral(Literal):
    """字符字面值"""

    value: str = dataclasses.field(kw_only=True)  # 不包含单引号的字符串

    def generate(self) -> str:
        return f"'{self.value}'"


@dataclasses.dataclass(slots=True)
class StringLiteral(Literal):
    """字符串字面值"""

    style: StringStyle = dataclasses.field(kw_only=True)  # 字面值样式
    value: str = dataclasses.field(kw_only=True)  # 不包含双引号的字符串内容

    def generate(self) -> str:
        if self.style == StringStyle.STRING:
            return f"\"{repr(self.value)}\""
        return f"\"\"\"\n{repr(self.value)}\"\"\""


@dataclasses.dataclass(slots=True)
class NullLiteral(Literal):
    """空值字面值"""

    def generate(self) -> str:
        return f"null"


def generate_tree_list(elems: List[Tree], sep: str):
    """将抽象语法树节点的列表生成代码"""
    return sep.join(elem.generate() for elem in elems)


def generate_enum_list(elems: List[enum.Enum], sep: str):
    """将枚举值的列表生成代码"""
    return sep.join(elem.value for elem in elems)

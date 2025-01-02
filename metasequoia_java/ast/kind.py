"""
抽象语法树的节点类型
"""

import enum

__all__ = [
    "TreeKind"
]


class TreeKind(enum.Enum):
    """抽象语法树节点类型

    使用与 JDK 源码中抽象语法树接口相同的节点，JDK 源码如下：
    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/source/tree/Tree.java
    """

    ANNOTATED_TYPE = enum.auto()  # AnnotatedTypeTree
    ANNOTATION = enum.auto()  # AnnotationTree
    TYPE_ANNOTATION = enum.auto()  # AnnotationTree
    ARRAY_ACCESS = enum.auto()  # ArrayAccessTree
    ARRAY_TYPE = enum.auto()  # ArrayTypeTree
    ASSERT = enum.auto()  # AssertTree
    ASSIGNMENT = enum.auto()  # AssignmentTree
    BLOCK = enum.auto()  # BlockTree
    BREAK = enum.auto()  # BreakTree
    CASE = enum.auto()  # CaseTree
    CATCH = enum.auto()  # CatchTree
    CLASS = enum.auto()  # ClassTree
    COMPILATION_UNIT = enum.auto()  # CompilationUnitTree
    CONDITIONAL_EXPRESSION = enum.auto()  # ConditionalExpressionTree
    CONTINUE = enum.auto()  # ContinueTree
    DO_WHILE_LOOP = enum.auto()  # DoWhileLoopTree
    ENHANCED_FOR_LOOP = enum.auto()  # EnhancedForLoopTree
    EXPRESSION_STATEMENT = enum.auto()  # ExpressionStatementTree
    MEMBER_SELECT = enum.auto()  # MemberSelectTree
    MEMBER_REFERENCE = enum.auto()  # MemberReferenceTree
    FOR_LOOP = enum.auto()  # ForLoopTree
    IDENTIFIER = enum.auto()  # IdentifierTree
    IF = enum.auto()  # IfTree
    IMPORT = enum.auto()  # ImportTree
    INSTANCE_OF = enum.auto()  # InstanceOfTree
    LABELED_STATEMENT = enum.auto()  # LabeledStatementTree
    METHOD = enum.auto()  # MethodTree
    METHOD_INVOCATION = enum.auto()  # MethodInvocationTree
    MODIFIERS = enum.auto()  # ModifiersTree
    NEW_ARRAY = enum.auto()  # NewArrayTree
    NEW_CLASS = enum.auto()  # NewClassTree
    LAMBDA_EXPRESSION = enum.auto()  # LambdaExpressionTree
    PACKAGE = enum.auto()  # PackageTree
    PARENTHESIZED = enum.auto()  # ParenthesizedTree
    ANY_PATTERN = enum.auto()  # AnyPatternTree
    BINDING_PATTERN = enum.auto()  # BindingPatternTree
    DEFAULT_CASE_LABEL = enum.auto()  # DefaultCaseLabelTree
    CONSTANT_CASE_LABEL = enum.auto()  # ConstantCaseLabelTree
    PATTERN_CASE_LABEL = enum.auto()  # PatternCaseLabelTree
    DECONSTRUCTION_PATTERN = enum.auto()  # DeconstructionPatternTree
    PRIMITIVE_TYPE = enum.auto()  # PrimitiveTypeTree
    RETURN = enum.auto()  # ReturnTree
    EMPTY_STATEMENT = enum.auto()  # EmptyStatementTree
    SWITCH = enum.auto()  # SwitchTree
    SWITCH_EXPRESSION = enum.auto()  # SwitchExpressionTree
    SYNCHRONIZED = enum.auto()  # SynchronizedTree
    THROW = enum.auto()  # ThrowTree
    TRY = enum.auto()  # TryTree
    PARAMETERIZED_TYPE = enum.auto()  # ParameterizedTypeTree
    UNION_TYPE = enum.auto()  # UnionTypeTree
    INTERSECTION_TYPE = enum.auto()  # IntersectionTypeTree
    TYPE_CAST = enum.auto()  # TypeCastTree
    TYPE_PARAMETER = enum.auto()  # TypeParameterTree
    VARIABLE = enum.auto()  # VariableTree
    WHILE_LOOP = enum.auto()  # WhileLoopTree
    POSTFIX_INCREMENT = enum.auto()  # UnaryTree ++
    POSTFIX_DECREMENT = enum.auto()  # UnaryTree --
    PREFIX_INCREMENT = enum.auto()  # UnaryTree ++
    PREFIX_DECREMENT = enum.auto()  # UnaryTree --
    UNARY_PLUS = enum.auto()  # UnaryTree +
    UNARY_MINUS = enum.auto()  # UnaryTree -
    BITWISE_COMPLEMENT = enum.auto()  # UnaryTree ~
    LOGICAL_COMPLEMENT = enum.auto()  # UnaryTree !
    MULTIPLY = enum.auto()  # BinaryTree *
    DIVIDE = enum.auto()  # BinaryTree /
    REMAINDER = enum.auto()  # BinaryTree %
    PLUS = enum.auto()  # BinaryTree +
    MINUS = enum.auto()  # BinaryTree -
    LEFT_SHIFT = enum.auto()  # BinaryTree <<
    RIGHT_SHIFT = enum.auto()  # BinaryTree >>
    UNSIGNED_RIGHT_SHIFT = enum.auto()  # BinaryTree >>>
    LESS_THAN = enum.auto()  # BinaryTree <
    GREATER_THAN = enum.auto()  # BinaryTree >
    LESS_THAN_EQUAL = enum.auto()  # BinaryTree <=
    GREATER_THAN_EQUAL = enum.auto()  # BinaryTree >=
    EQUAL_TO = enum.auto()  # BinaryTree ==
    NOT_EQUAL_TO = enum.auto()  # BinaryTree !=
    AND = enum.auto()  # BinaryTree &
    XOR = enum.auto()  # BinaryTree ^
    OR = enum.auto()  # BinaryTree |
    CONDITIONAL_AND = enum.auto()  # BinaryTree &&
    CONDITIONAL_OR = enum.auto()  # BinaryTree ||
    MULTIPLY_ASSIGNMENT = enum.auto()  # CompoundAssignmentTree *=
    DIVIDE_ASSIGNMENT = enum.auto()  # CompoundAssignmentTree /=
    REMAINDER_ASSIGNMENT = enum.auto()  # CompoundAssignmentTree %=
    PLUS_ASSIGNMENT = enum.auto()  # CompoundAssignmentTree +=
    MINUS_ASSIGNMENT = enum.auto()  # CompoundAssignmentTree -=
    LEFT_SHIFT_ASSIGNMENT = enum.auto()  # CompoundAssignmentTree <<=
    RIGHT_SHIFT_ASSIGNMENT = enum.auto()  # CompoundAssignmentTree >>=
    UNSIGNED_RIGHT_SHIFT_ASSIGNMENT = enum.auto()  # CompoundAssignmentTree >>>=
    AND_ASSIGNMENT = enum.auto()  # CompoundAssignmentTree &=
    XOR_ASSIGNMENT = enum.auto()  # CompoundAssignmentTree &=
    OR_ASSIGNMENT = enum.auto()  # CompoundAssignmentTree |=
    INT_LITERAL = enum.auto()  # LiteralTree
    LONG_LITERAL = enum.auto()  # LiteralTree
    FLOAT_LITERAL = enum.auto()  # LiteralTree
    DOUBLE_LITERAL = enum.auto()  # LiteralTree
    BOOLEAN_LITERAL = enum.auto()  # LiteralTree
    CHAR_LITERAL = enum.auto()  # LiteralTree
    STRING_LITERAL = enum.auto()  # LiteralTree
    NULL_LITERAL = enum.auto()  # LiteralTree
    UNBOUNDED_WILDCARD = enum.auto()  # WildcardTree
    EXTENDS_WILDCARD = enum.auto()  # WildcardTree
    SUPER_WILDCARD = enum.auto()  # WildcardTree
    ERRONEOUS = enum.auto()  # ErroneousTree
    INTERFACE = enum.auto()  # ClassTree
    ENUM = enum.auto()  # ClassTree
    ANNOTATION_TYPE = enum.auto()  # ClassTree
    MODULE = enum.auto()  # ModuleTree
    EXPORTS = enum.auto()  # ExportsTree
    OPENS = enum.auto()  # OpensTree
    PROVIDES = enum.auto()  # ProvidesTree
    RECORD = enum.auto()  # ClassTree
    REQUIRES = enum.auto()  # RequiresTree
    USES = enum.auto()  # UsesTree
    OTHER = enum.auto()
    YIELD = enum.auto()  # YieldTree

    MOCK = enum.auto()

"""
语法解析器
"""

from typing import List, Optional

from metasequoia_java import ast
from metasequoia_java.ast.constants import INT_LITERAL_STYLE_HASH
from metasequoia_java.ast.constants import LONG_LITERAL_STYLE_HASH
from metasequoia_java.ast.constants import StringStyle
from metasequoia_java.ast.kind import TreeKind
from metasequoia_java.lexical import LexicalFSM
from metasequoia_java.lexical import Token
from metasequoia_java.lexical import TokenKind


class JavaSyntaxError(Exception):
    """Java 语法错误"""


class JavaParser:
    """
    【对应 JDK 源码位置】
    https://github.com/openjdk/jdk/blob/master/src/jdk.compiler/share/classes/com/sun/tools/javac/parser/JavacParser.java
    """

    def __init__(self, lexer: LexicalFSM):
        self._lexer = lexer
        self._token: Optional[Token] = None
        self._next_token()

    def _next_token(self):
        self._token = self._lexer.lex()

    def _accept(self, kind: TokenKind):
        if self._token.kind == kind:
            self._next_token()
        else:
            raise JavaSyntaxError(f"expect {kind}, but get {self._token.kind}")

    # ------------------------------ Chapter 3 : Lexical Structure ------------------------------

    def identifier(self) -> str:
        """解析 Identifier 元素

        JDK 文档地址：https://docs.oracle.com/javase/specs/jls/se22/html/jls-3.html
        Identifier:
          IdentifierChars but not a ReservedKeyword or BooleanLiteral or NullLiteral
        """
        if self._token.kind != TokenKind.IDENTIFIER:
            raise JavaSyntaxError(f"{self._token.source} 不能作为 Identifier")
        value = self._token.name
        self._next_token()
        return value

    def type_name(self) -> str:
        """解析 TypeIdentifier 元素

        【对应 JDK 源码】JavacParser.typeName
        JDK 文档地址：https://docs.oracle.com/javase/specs/jls/se22/html/jls-3.html
        TypeIdentifier:
          Identifier but not permits, record, sealed, var, or yield
        """
        if self._token.kind != TokenKind.IDENTIFIER:
            raise JavaSyntaxError(f"expect type_identifier, but get {self._token.source}")
        if self._token.name in {"permits", "record", "sealed", "var", "yield"}:
            raise JavaSyntaxError(f"expect type_identifier, but get {self._token.name}")
        value = self._token.name
        self._next_token()
        return value

    def unqualified_method_identifier(self) -> str:
        """解析 UnqualifiedMethodIdentifier 元素

        JDK 文档地址：https://docs.oracle.com/javase/specs/jls/se22/html/jls-3.html
        UnqualifiedMethodIdentifier:
          Identifier but not yield
        """
        if self._token.kind != TokenKind.IDENTIFIER:
            raise JavaSyntaxError(f"{self._token.source} 不能作为 UnqualifiedMethodIdentifier")
        if self._token.name in {"yield"}:
            raise JavaSyntaxError(f"{self._token.name} 不能作为 UnqualifiedMethodIdentifier")
        value = self._token.name
        self._next_token()
        return value

    def literal(self) -> ast.LiteralTree:
        """解析 Literal 元素

        JDK 文档地址：https://docs.oracle.com/javase/specs/jls/se22/html/jls-3.html
        Literal:
          IntegerLiteral
          FloatingPointLiteral
          BooleanLiteral
          CharacterLiteral
          StringLiteral
          TextBlock
          NullLiteral
        """
        if self._token.kind in {TokenKind.INT_OCT_LITERAL, TokenKind.INT_DEC_LITERAL, TokenKind.INT_HEX_LITERAL}:
            return ast.IntLiteralTree(
                kind=TreeKind.INT_LITERAL,
                style=INT_LITERAL_STYLE_HASH[self._token.kind],
                value=self._token.int_value(),
                source=self._token.source
            )
        if self._token.kind in {TokenKind.LONG_OCT_LITERAL, TokenKind.LONG_DEC_LITERAL, TokenKind.LONG_HEX_LITERAL}:
            return ast.LongLiteralTree(
                kind=TreeKind.LONG_LITERAL,
                style=LONG_LITERAL_STYLE_HASH[self._token.kind],
                value=self._token.int_value(),
                source=self._token.source
            )
        if self._token.kind == TokenKind.FLOAT_LITERAL:
            return ast.FloatLiteralTree(
                kind=TreeKind.FLOAT_LITERAL,
                value=self._token.float_value(),
                source=self._token.source
            )
        if self._token.kind == TokenKind.DOUBLE_LITERAL:
            return ast.DoubleLiteralTree(
                kind=TreeKind.DOUBLE_LITERAL,
                value=self._token.float_value(),
                source=self._token.source
            )
        if self._token.kind == TokenKind.TRUE:
            return ast.TrueLiteralTree(
                kind=TreeKind.BOOLEAN_LITERAL,
                source=self._token.source
            )
        if self._token.kind == TokenKind.FALSE:
            return ast.FalseLiteralTree(
                kind=TreeKind.BOOLEAN_LITERAL,
                source=self._token.source
            )
        if self._token.kind == TokenKind.CHAR_LITERAL:
            return ast.CharacterLiteralTree(
                kind=TreeKind.CHAR_LITERAL,
                value=self._token.char_value(),
                source=self._token.source
            )
        if self._token.kind == TokenKind.STRING_LITERAL:
            return ast.StringLiteralTree(
                kind=TreeKind.STRING_LITERAL,
                style=StringStyle.STRING,
                value=self._token.string_value(),
                source=self._token.source
            )
        if self._token.kind == TokenKind.TEXT_BLOCK:
            return ast.StringLiteralTree(
                kind=TreeKind.STRING_LITERAL,
                style=StringStyle.TEXT_BLOCK,
                value=self._token.string_value(),
                source=self._token.source
            )
        if self._token.kind == TokenKind.NULL:
            return ast.NullLiteralTree(
                kind=TreeKind.NULL_LITERAL,
                source=self._token.source
            )
        raise JavaSyntaxError(f"{self._token.source} 不是字面值")

    def parse_type(self,
                   allow_var: bool = False,
                   annotations: Optional[List[ast.AnnotationTree]] = None
                   ) -> ast.ExpressionTree:
        """类型

        Parameters
        ----------
        allow_var : bool, default = False
            TODO 待补充含义
        annotations : Optional[List[ast.AnnotationTree]], default = None
            已经解析的注解

        【对应 JDK 源码】JavacParser.parseType
        """
        if annotations is None:
            annotations = self.type_annotations_opt()

        result = self.unannotated_type(allow_var=allow_var)

        # TODO 待确定是否需要实现类似 insertAnnotationsToMostInner 的逻辑
        if annotations:
            return ast.AnnotatedTypeTree(
                kind=TreeKind.ANNOTATION_TYPE,
                annotations=annotations,
                underlying_type=result,
                source=None
            )
        return result

    def type_parameters_opt(self, parse_empty: bool = False) -> List[ast.TypeParameterTree]:
        """可选的多个类型参数

        Parameters
        ----------
        parse_empty : bool, default = False
            是否解析空参数

        【对应 JDK 源码】JavacParser.typeParametersOpt
        TypeParametersOpt = ["<" TypeParameter {"," TypeParameter} ">"]

        TODO 待补充单元测试
        """
        if self._token.kind != TokenKind.LT:
            return []

        self._next_token()
        if parse_empty is True and self._token.kind == TokenKind.GT:
            self._accept(TokenKind.GT)
            return []

        ty_params: List[ast.TypeParameterTree] = [self.type_parameter()]
        while self._token.kind == TokenKind.COMMA:
            self._next_token()
            ty_params.append(self.type_parameter())
        self._accept(TokenKind.GT)
        return ty_params

    def type_parameter(self) -> ast.TypeParameterTree:
        """类型参数

        【对应 JDK 源码】JavacParser.typeParameter
        TypeParameter = [Annotations] TypeVariable [TypeParameterBound]
        TypeParameterBound = EXTENDS Type {"&" Type}
        TypeVariable = Ident

        TODO 待补充单元测试
        """
        annotations: List[ast.AnnotationTree] = self.type_annotations_opt()
        name: str = self.type_name()
        bounds: List[ast.ExpressionTree] = []
        if self._token.kind == TokenKind.EXTENDS:
            self._next_token()
            bounds.append(self.parse_type())
            while self._token.kind == TokenKind.AMP:
                self._next_token()
                bounds.append(self.parse_type())
        return ast.TypeParameterTree(
            kind=TreeKind.TYPE_PARAMETER,
            name=name,
            bounds=bounds,
            annotations=annotations,
            source=None
        )

    def type_arguments_opt(self) -> Optional[List[ast.ExpressionTree]]:
        """可选的多个类型实参

        【对应 JDK 源码】JavacParser.typeArgumentsOpt
        TypeArgumentsOpt = [ TypeArguments ]

        TODO 待补充单元测试
        """
        if self._token.kind != TokenKind.LT:
            return None
        return self.type_arguments()

    def type_arguments(self) -> List[ast.ExpressionTree]:
        """多个类型实参

        【对应 JDK 源码】JavacParser.typeArguments
        TypeArguments  = "<" TypeArgument {"," TypeArgument} ">"

        TODO 待补充单元测试
        """
        if self._token.kind != TokenKind.LT:
            raise JavaSyntaxError(f"expect TokenKind.LT in type_arguments, but find {self._token.kind}")

        self._next_token()
        if self._token.kind == TokenKind.GT:
            return []

        args = [self.type_argument()]  # TODO 补充 isMode(EXPR) 的判断逻辑
        while self._token.kind == TokenKind.COMMA:
            self._next_token()
            args.append(self.type_argument())  # TODO 补充 isMode(EXPR) 的判断逻辑

        if self._token.kind in {TokenKind.GT_GT, TokenKind.GT_EQ, TokenKind.GT_GT_GT, TokenKind.GT_GT_EQ,
                                TokenKind.GT_GT_GT_EQ}:
            self._token = self._lexer.split()
        elif self._token.kind == TokenKind.GT:
            self._next_token()
        else:
            raise JavaSyntaxError(f"expect GT or COMMA in type_arguments, but find {self._token.kind}")

        return args

    def type_argument(self) -> ast.ExpressionTree:
        """类型实参

        【对应 JDK 源码】JavacParser.typeArgument
        TypeArgument = Type
                     | [Annotations] "?"
                     | [Annotations] "?" EXTENDS Type {"&" Type}
                     | [Annotations] "?" SUPER Type

        样例 1: List<String>
        样例 2: List<?>
        样例 3: List<? extends Number>
        样例 4: List<? super Integer>
        样例 5: List<@NonNull String>
        样例 6: List<? extends Number & Comparable<?>>

        TODO 待补充单元测试
        """
        annotations: List[ast.AnnotationTree] = self.type_annotations_opt()
        if self._token.kind != TokenKind.QUES:
            return self.parse_type(False, annotations)
        self._next_token()
        if self._token.kind == TokenKind.EXTENDS:
            self._next_token()
            wildcard = ast.WildcardTree(
                kind=TreeKind.EXTENDS_WILDCARD,
                bound=self.parse_type(),
                source=None
            )
        elif self._token.kind == TokenKind.SUPER:
            self._next_token()
            wildcard = ast.WildcardTree(
                kind=TreeKind.SUPER_WILDCARD,
                bound=self.parse_type(),
                source=None
            )
        elif self._token.kind == TokenKind.GT:
            wildcard = ast.WildcardTree(
                kind=TreeKind.UNBOUNDED_WILDCARD,
                bound=self.parse_type(),
                source=None
            )
        else:
            raise JavaSyntaxError(f"类型实参语法错误")

        if annotations:
            return ast.AnnotatedTypeTree(
                kind=TreeKind.ANNOTATION_TYPE,
                annotations=annotations,
                underlying_type=wildcard,
                source=None
            )
        return wildcard

    def type_annotations_opt(self) -> List[ast.AnnotationTree]:
        """TODO"""

    def unannotated_type(self, allow_var: bool = False) -> ast.ExpressionTree:
        """解析不包含注解的类型"""

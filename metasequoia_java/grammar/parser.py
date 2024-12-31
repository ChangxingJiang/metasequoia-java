"""
语法解析器
"""

from typing import Any, Dict, List, Optional

from metasequoia_java import ast
from metasequoia_java.ast.constants import INT_LITERAL_STYLE_HASH
from metasequoia_java.ast.constants import LONG_LITERAL_STYLE_HASH
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
        self._text = lexer.text
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

    def _info_include(self, start_pos: int) -> Dict[str, Any]:
        """根据开始位置 start_pos 和当前 token 的结束位置（即包含当前 token），获取当前节点的源代码和位置信息"""
        end_pos = self._token.end_pos
        return {
            "source": self._text[start_pos: end_pos],
            "start_pos": start_pos,
            "end_pos": end_pos
        }

    def _info_exclude(self, start_pos: int) -> Dict[str, Any]:
        """根据开始位置 start_pos 和当前 token 的开始位置（即不包含当前 token），获取当前节点的源代码和位置信息"""
        end_pos = self._token.pos
        return {
            "source": self._text[start_pos: end_pos],
            "start_pos": start_pos,
            "end_pos": end_pos
        }

    # ------------------------------ Chapter 3 : Lexical Structure ------------------------------

    def identifier(self) -> ast.IdentifierTree:
        """解析 Identifier 元素

        JDK 文档地址：https://docs.oracle.com/javase/specs/jls/se22/html/jls-3.html
        Identifier:
          IdentifierChars but not a ReservedKeyword or BooleanLiteral or NullLiteral

        【对应 JDK 源码】JavacParser.ident
        """
        if self._token.kind != TokenKind.IDENTIFIER:
            raise JavaSyntaxError(f"{self._token.source} 不能作为 Identifier")

        pos = self._token.pos
        name = self._token.name
        self._next_token()
        return ast.IdentifierTree.create(
            name=name,
            **self._info_exclude(pos)
        )

    def type_name(self) -> ast.IdentifierTree:
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

        pos = self._token.pos
        name = self._token.name
        self._next_token()
        return ast.IdentifierTree.create(
            name=name,
            **self._info_exclude(pos)
        )

    def unqualified_method_identifier(self) -> ast.IdentifierTree:
        """解析 UnqualifiedMethodIdentifier 元素

        JDK 文档地址：https://docs.oracle.com/javase/specs/jls/se22/html/jls-3.html
        UnqualifiedMethodIdentifier:
          Identifier but not yield
        """
        if self._token.kind != TokenKind.IDENTIFIER:
            raise JavaSyntaxError(f"{self._token.source} 不能作为 UnqualifiedMethodIdentifier")
        if self._token.name in {"yield"}:
            raise JavaSyntaxError(f"{self._token.name} 不能作为 UnqualifiedMethodIdentifier")

        pos = self._token.pos
        name = self._token.name
        self._next_token()
        return ast.IdentifierTree.create(
            name=name,
            **self._info_exclude(pos)
        )

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
        pos = self._token.pos
        if self._token.kind in {TokenKind.INT_OCT_LITERAL, TokenKind.INT_DEC_LITERAL, TokenKind.INT_HEX_LITERAL}:
            return ast.IntLiteralTree.create(
                style=INT_LITERAL_STYLE_HASH[self._token.kind],
                value=self._token.int_value(),
                **self._info_include(pos)
            )
        if self._token.kind in {TokenKind.LONG_OCT_LITERAL, TokenKind.LONG_DEC_LITERAL, TokenKind.LONG_HEX_LITERAL}:
            return ast.LongLiteralTree.create(
                style=LONG_LITERAL_STYLE_HASH[self._token.kind],
                value=self._token.int_value(),
                **self._info_include(pos)
            )
        if self._token.kind == TokenKind.FLOAT_LITERAL:
            return ast.FloatLiteralTree.create(
                value=self._token.float_value(),
                **self._info_include(pos)
            )
        if self._token.kind == TokenKind.DOUBLE_LITERAL:
            return ast.DoubleLiteralTree.create(
                value=self._token.float_value(),
                **self._info_include(pos)
            )
        if self._token.kind == TokenKind.TRUE:
            return ast.TrueLiteralTree.create(
                **self._info_include(pos)
            )
        if self._token.kind == TokenKind.FALSE:
            return ast.FalseLiteralTree.create(
                **self._info_include(pos)
            )
        if self._token.kind == TokenKind.CHAR_LITERAL:
            return ast.CharacterLiteralTree.create(
                value=self._token.char_value(),
                **self._info_include(pos)
            )
        if self._token.kind == TokenKind.STRING_LITERAL:
            return ast.StringLiteralTree.create_string(
                value=self._token.string_value(),
                **self._info_include(pos)
            )
        if self._token.kind == TokenKind.TEXT_BLOCK:
            return ast.StringLiteralTree.create_text_block(
                value=self._token.string_value(),
                **self._info_include(pos)
            )
        if self._token.kind == TokenKind.NULL:
            return ast.NullLiteralTree.create(
                **self._info_include(pos)
            )
        raise JavaSyntaxError(f"{self._token.source} 不是字面值")

    def parse_type(self,
                   allow_var: bool = False,
                   annotations: Optional[List[ast.AnnotationTree]] = None,
                   pos: Optional[int] = None
                   ) -> ast.ExpressionTree:
        """类型

        Parameters
        ----------
        pos : Optional[int], default = None
            默认开始位置
        allow_var : bool, default = False
            TODO 待补充含义
        annotations : Optional[List[ast.AnnotationTree]], default = None
            已经解析的注解

        【对应 JDK 源码】JavacParser.parseType

        TODO 待补充单元测试
        """
        if pos is None:
            pos = self._token.pos
        if annotations is None:
            annotations = self.type_annotations_opt()

        result = self.unannotated_type(allow_var=allow_var)

        # TODO 待确定是否需要实现类似 insertAnnotationsToMostInner 的逻辑
        if annotations:
            return ast.AnnotatedTypeTree.create(
                annotations=annotations,
                underlying_type=result,
                **self._info_include(pos)
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
        pos = self._token.pos
        annotations: List[ast.AnnotationTree] = self.type_annotations_opt()
        name: ast.IdentifierTree = self.type_name()
        bounds: List[ast.ExpressionTree] = []
        if self._token.kind == TokenKind.EXTENDS:
            self._next_token()
            bounds.append(self.parse_type())
            while self._token.kind == TokenKind.AMP:
                self._next_token()
                bounds.append(self.parse_type())
        return ast.TypeParameterTree.create(
            name=name,
            bounds=bounds,
            annotations=annotations,
            **self._info_include(pos)
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

        TODO 待补充单元测试（等待 parse_type、type_annotations_opt）
        """
        pos_1 = self._token.pos
        annotations: List[ast.AnnotationTree] = self.type_annotations_opt()
        if self._token.kind != TokenKind.QUES:
            return self.parse_type(False, annotations)
        pos_2 = self._token.pos
        self._next_token()
        if self._token.kind == TokenKind.EXTENDS:
            self._next_token()
            wildcard = ast.WildcardTree.create_extends_wildcard(
                bound=self.parse_type(),
                **self._info_include(pos_2)
            )
        elif self._token.kind == TokenKind.SUPER:
            self._next_token()
            wildcard = ast.WildcardTree.create_super_wildcard(
                bound=self.parse_type(),
                **self._info_include(pos_2)
            )
        elif self._token.kind == TokenKind.GT:
            wildcard = ast.WildcardTree.create_unbounded_wildcard(
                bound=self.parse_type(),
                **self._info_include(pos_2)
            )
        else:
            raise JavaSyntaxError(f"类型实参语法错误")

        if annotations:
            return ast.AnnotatedTypeTree.create(
                annotations=annotations,
                underlying_type=wildcard,
                **self._info_include(pos_1)
            )
        return wildcard

    def type_annotations_opt(self) -> List[ast.AnnotationTree]:
        """TODO"""

    def unannotated_type(self, allow_var: bool = False) -> ast.ExpressionTree:
        """解析不包含注解的类型

        【对应 JDK 源码】JavacParser.unannotatedType

        TODO 待增加 allowVar 相关逻辑
        TODO 待增加单元测试
        """
        result = self.term()
        if result.kind == TokenKind.IDENTIFIER and result.source in {"var", "yield", "record", "sealed", "permits"}:
            raise JavaSyntaxError(f"expect unannotated_type, but get {result.kind}")
        # TODO 待增加 TYPEARRAY 相关逻辑
        return result

    def qualident(self, allow_annotations: bool):
        """解析名称

        对应 JDK 文档中的：ModuleName, PackageName

        【对应 JDK 源码】JavacParser.qualident
        Qualident = Ident { DOT [Annotations] Ident }

        TODO 补充单元测试：allow_annotations = True
        """
        pos = self._token.pos
        expression: ast.ExpressionTree = self.identifier()
        while self._token.kind == TokenKind.DOT:
            self._next_token()
            type_annotations = self.type_annotations_opt() if allow_annotations is True else None
            identifier: ast.IdentifierTree = self.identifier()
            expression = ast.MemberSelectTree.create(
                expression=expression,
                identifier=identifier,
                **self._info_include(pos)
            )
            if type_annotations:
                expression = ast.AnnotatedTypeTree.create(
                    annotations=type_annotations,
                    underlying_type=expression,
                    **self._info_include(pos)
                )
        return expression

    def term(self) -> ast.ExpressionTree:
        """TODO 名称待整理

        【对应 JDK 源码】JavacParser.term
        """

    def term3(self) -> ast.ExpressionTree:
        """解析第 3 层级语法元素

        【对应 JDK 源码】JavacParser.term3
        Expression3    = PrefixOp Expression3
                       | "(" Expr | TypeNoParams ")" Expression3
                       | Primary {Selector} {PostfixOp}

        Primary        = "(" Expression ")"
                       | Literal
                       | [TypeArguments] THIS [Arguments]
                       | [TypeArguments] SUPER SuperSuffix
                       | NEW [TypeArguments] Creator
                       | "(" Arguments ")" "->" ( Expression | Block )
                       | Ident "->" ( Expression | Block )
                       | [Annotations] Ident { "." [Annotations] Ident }
                       | Expression3 MemberReferenceSuffix
                         [ [Annotations] "[" ( "]" BracketsOpt "." CLASS | Expression "]" )
                         | Arguments
                         | "." ( CLASS | THIS | [TypeArguments] SUPER Arguments | NEW [TypeArguments] InnerCreator )
                         ]
                       | BasicType BracketsOpt "." CLASS

        PrefixOp       = "++" | "--" | "!" | "~" | "+" | "-"
        PostfixOp      = "++" | "--"
        Type3          = Ident { "." Ident } [TypeArguments] {TypeSelector} BracketsOpt
                       | BasicType
        TypeNoParams3  = Ident { "." Ident } BracketsOpt
        Selector       = "." [TypeArguments] Ident [Arguments]
                       | "." THIS
                       | "." [TypeArguments] SUPER SuperSuffix
                       | "." NEW [TypeArguments] InnerCreator
                       | "[" Expression "]"
        TypeSelector   = "." Ident [TypeArguments]
        SuperSuffix    = Arguments | "." Ident [Arguments]

        TODO 补充单元测试（匹配 type_arguments 的场景）
        TODO 补充单元测试（type_argument 场景）
        """
        pos = self._token.pos
        type_args = self.type_arguments_opt()

        # 类型实参
        if self._token.kind == TokenKind.QUES:
            # TODO 增加 isMode 的逻辑
            return self.type_argument()

        # 一元表达式
        if self._token.kind in {TokenKind.PLUS_PLUS, TokenKind.SUB_SUB, TokenKind.BANG, TokenKind.TILDE, TokenKind.PLUS,
                                TokenKind.SUB}:
            # TODO 增加 isMode 的逻辑
            if type_args is not None:
                raise JavaSyntaxError("语法不合法")
            tk = self._token.kind
            self._next_token()
            if tk == TokenKind.SUB and self._token.kind in {TokenKind.INT_DEC_LITERAL, TokenKind.LONG_DEC_LITERAL}:
                return self.term3_rest(self.literal(), type_args)
            else:
                expression = self.term3()
                return ast.UnaryTree.create(
                    operator=tk,
                    expression=expression,
                    **self._info_include(pos)
                )

    def term3_rest(self, t: ast.ExpressionTree, type_args: Optional[List[ast.ExpressionTree]]) -> ast.ExpressionTree:
        """解析第 3 层级语法元素的剩余部分"""


if __name__ == "__main__":
    print(JavaParser(LexicalFSM("-1")).term3())

"""
语法解析器
"""

from typing import Any, Dict, List, Optional

from metasequoia_java import ast
from metasequoia_java.ast.constants import INT_LITERAL_STYLE_HASH
from metasequoia_java.ast.constants import LONG_LITERAL_STYLE_HASH
from metasequoia_java.grammar.parans_result import ParensResult
from metasequoia_java.grammar.parser_mode import ParserMode
from metasequoia_java.grammar.token_set import LAX_IDENTIFIER
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
        self._token: Optional[Token] = self._lexer.token(0)

        self.mode: ParserMode = ParserMode.NULL  # 当前解析模式
        self.last_mode: ParserMode = ParserMode.NULL  # 上一个解析模式

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

    # ------------------------------ 解析模式相关方法 ------------------------------

    def set_mode(self, mode: ParserMode):
        self.mode = mode

    def set_last_mode(self, mode: ParserMode):
        self.last_mode = mode

    def is_mode(self, mode: ParserMode):
        return self.mode & mode

    def was_type_mode(self):
        return self.last_mode & ParserMode.TYPE

    def select_expr_mode(self):
        self.set_mode((self.mode & ParserMode.NO_LAMBDA) | ParserMode.EXPR)  # 如果当前 mode 有 NO_LAMBDA 则保留，并添加 EXPR

    def select_type_mode(self):
        self.set_mode((self.mode & ParserMode.NO_LAMBDA) | ParserMode.TYPE)  # 如果当前 mode 有 NO_LAMBDA 则保留，并添加 TYPE

    # ------------------------------ Chapter 3 : Lexical Structure ------------------------------

    def ident(self) -> ast.IdentifierTree:
        """解析 Identifier 元素

        [JDK Code] JavacParser.ident

        JDK 文档地址：https://docs.oracle.com/javase/specs/jls/se22/html/jls-3.html
        Identifier:
          IdentifierChars but not a ReservedKeyword or BooleanLiteral or NullLiteral
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

        [JDK Code] JavacParser.typeName
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
        """解析字面值

        [Jdk Code] JavacParser.literal

        [JDK Document] https://docs.oracle.com/javase/specs/jls/se22/html/jls-3.html#jls-Literal
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

        [JDK Code] JavacParser.parseType

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

        [JDK Code] JavacParser.typeParametersOpt
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

        [JDK Code] JavacParser.typeParameter
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

        [JDK Code] JavacParser.typeArgumentsOpt
        TypeArgumentsOpt = [ TypeArguments ]

        TODO 待补充单元测试
        """
        if self._token.kind != TokenKind.LT:
            return None
        return self.type_arguments(False)

    def type_arguments(self, diamond_allowed: bool) -> List[ast.ExpressionTree]:
        """多个类型实参

        [JDK Code] JavacParser.typeArguments
        TypeArguments  = "<" TypeArgument {"," TypeArgument} ">"

        TODO 待补充单元测试
        """
        if self._token.kind != TokenKind.LT:
            raise JavaSyntaxError(f"expect TokenKind.LT in type_arguments, but find {self._token.kind}")

        self._next_token()
        if self._token.kind == TokenKind.GT and diamond_allowed:
            self.set_mode(self.mode | ParserMode.DIAMOND)
            self._next_token()
            return []

        args = [self.type_argument() if not self.is_mode(ParserMode.EXPR) else self.parse_type()]
        while self._token.kind == TokenKind.COMMA:
            self._next_token()
            args.append(self.type_argument() if not self.is_mode(ParserMode.EXPR) else self.parse_type())

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

        [JDK Code] JavacParser.typeArgument
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

        [JDK Code] JavacParser.unannotatedType

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

        [JDK Code] JavacParser.qualident
        Qualident = Ident { DOT [Annotations] Ident }

        TODO 补充单元测试：allow_annotations = True
        """
        pos = self._token.pos
        expression: ast.ExpressionTree = self.ident()
        while self._token.kind == TokenKind.DOT:
            self._next_token()
            type_annotations = self.type_annotations_opt() if allow_annotations is True else None
            identifier: ast.IdentifierTree = self.ident()
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

        [JDK Code] JavacParser.term
        """

    def parse_intersection_type(self, pos: int, first_type: ast.ExpressionTree):
        """解析 CAST 语句中的交叉类型

        [JDK Document] https://docs.oracle.com/javase/specs/jls/se22/html/jls-4.html#jls-AdditionalBound
        AdditionalBound:
          & InterfaceType

        [JDK Code] JavacParser.parseIntersectionType
        """
        bounds = [first_type]
        while self._token.kind == TokenKind.AMP:
            self._accept(TokenKind.AMP)
            bounds.append(self.parse_type())
        if len(bounds) > 1:
            return ast.IntersectionTypeTree.create(
                bounds=bounds,
                **self._info_include(pos)
            )
        return first_type

    def term3(self) -> ast.ExpressionTree:
        """解析第 3 层级语法元素

        [JDK Code] JavacParser.term3
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
        # [JDK Document] https://docs.oracle.com/javase/specs/jls/se22/html/jls-15.html#jls-UnaryExpression
        # UnaryExpression:
        #   PreIncrementExpression
        #   PreDecrementExpression
        #   + UnaryExpression
        #   - UnaryExpression
        #   UnaryExpressionNotPlusMinus
        #
        # PreIncrementExpression:
        #   ++ UnaryExpression
        #
        # PreDecrementExpression:
        #   -- UnaryExpression
        #
        # UnaryExpressionNotPlusMinus:
        #   PostfixExpression
        #   ~ UnaryExpression
        #   ! UnaryExpression
        #   CastExpression (不包含)
        #   SwitchExpression (不包含)
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

        # 括号表达式：
        if self._token.kind == TokenKind.LPAREN:
            # TODO 增加 isMode 的逻辑
            if type_args is not None:
                raise JavaSyntaxError("语法不合法")
            pres: ParensResult = self.analyze_parens()

            # [JDK Document] https://docs.oracle.com/javase/specs/jls/se22/html/jls-15.html#jls-CastExpression
            # CastExpression:
            #   ( PrimitiveType ) UnaryExpression
            #   ( ReferenceType {AdditionalBound} ) UnaryExpressionNotPlusMinus
            #   ( ReferenceType {AdditionalBound} ) LambdaExpression
            if pres == ParensResult.CAST:
                self._accept(TokenKind.LPAREN)
                cast_type = self.parse_intersection_type(pos, self.parse_type())
                self._accept(TokenKind.RPAREN)
                expression = self.term3()
                return ast.TypeCastTree(
                    cast_type=cast_type,
                    expression=expression,
                    **self._info_include(pos)
                )

            # if pres in {ParensResult.IMPLICIT_LAMBDA, ParensResult.EXPLICIT_LAMBDA}:

    def term3_rest(self, t: ast.ExpressionTree, type_args: Optional[List[ast.ExpressionTree]]) -> ast.ExpressionTree:
        """解析第 3 层级语法元素的剩余部分"""

    def analyze_parens(self) -> ParensResult:
        """分析括号中的内容

        [JDK Code] JavacParser.analyzeParens
        """
        depth = 0
        is_type = False
        lookahead = 0
        default_result = ParensResult.PARENS
        while True:
            tk = self._lexer.token(lookahead).kind
            print(tk)
            if tk == TokenKind.COMMA:
                is_type = True
            elif tk in {TokenKind.EXTENDS, TokenKind.SUPER, TokenKind.DOT, TokenKind.AMP}:
                continue  # 跳过
            elif tk == TokenKind.QUES:
                if self._lexer.token(lookahead + 1).kind in {TokenKind.EXTENDS, TokenKind.SUPER}:
                    is_type = True  # wildcards
            elif tk in {TokenKind.BYTE, TokenKind.SHORT, TokenKind.INT, TokenKind.LONG, TokenKind.FLOAT,
                        TokenKind.FLOAT, TokenKind.DOUBLE, TokenKind.BOOLEAN, TokenKind.CHAR, TokenKind.VOID}:
                if self._lexer.token(lookahead + 1).kind == TokenKind.RPAREN:
                    # Type, ')' -> cast
                    return ParensResult.CAST
                if self._lexer.token(lookahead + 1).kind in LAX_IDENTIFIER:
                    # Type, Identifier/'_'/'assert'/'enum' -> explicit lambda
                    return ParensResult.EXPLICIT_LAMBDA
            elif tk == TokenKind.LPAREN:
                if lookahead != 0:
                    # // '(' in a non-starting position -> parens
                    return ParensResult.PARENS
                if self._lexer.token(lookahead + 1).kind == TokenKind.RPAREN:
                    # // '(', ')' -> explicit lambda
                    return ParensResult.EXPLICIT_LAMBDA
            elif tk == TokenKind.RPAREN:
                if is_type is True:
                    return ParensResult.CAST
                if self._lexer.token(lookahead + 1).kind in {
                    TokenKind.CASE, TokenKind.TILDE, TokenKind.LPAREN, TokenKind.THIS, TokenKind.SUPER,
                    TokenKind.INT_OCT_LITERAL, TokenKind.INT_DEC_LITERAL, TokenKind.INT_HEX_LITERAL,
                    TokenKind.LONG_OCT_LITERAL, TokenKind.LONG_DEC_LITERAL, TokenKind.LONG_HEX_LITERAL,
                    TokenKind.FLOAT_LITERAL, TokenKind.DOUBLE_LITERAL, TokenKind.CHAR_LITERAL, TokenKind.STRING_LITERAL,
                    TokenKind.STRING_FRAGMENT, TokenKind.TRUE, TokenKind.FALSE, TokenKind.NULL, TokenKind.NEW,
                    TokenKind.IDENTIFIER, TokenKind.ASSERT, TokenKind.ENUM, TokenKind.UNDERSCORE, TokenKind.SWITCH,
                    TokenKind.BYTE, TokenKind.SHORT, TokenKind.CHAR, TokenKind.INT, TokenKind.LONG, TokenKind.FLOAT,
                    TokenKind.DOUBLE, TokenKind.BOOLEAN, TokenKind.VOID
                }:
                    return ParensResult.CAST
                return default_result
            elif tk in LAX_IDENTIFIER:
                print("LAX_IDENTIFIER:", self._lexer.token(lookahead + 1).kind)
                if self._lexer.token(lookahead + 1).kind in LAX_IDENTIFIER:
                    # Identifier, Identifier/'_'/'assert'/'enum' -> explicit lambda
                    return ParensResult.EXPLICIT_LAMBDA
                if (self._lexer.token(lookahead + 1).kind == TokenKind.RPAREN
                        and self._lexer.token(lookahead + 2).kind == TokenKind.ARROW):
                    # // Identifier, ')' '->' -> implicit lambda
                    # TODO 待增加 isMode 的逻辑
                    return ParensResult.IMPLICIT_LAMBDA
                if depth == 0 and self._lexer.token(lookahead + 1).kind == TokenKind.COMMA:
                    default_result = ParensResult.IMPLICIT_LAMBDA
                is_type = False
            elif tk in {TokenKind.FINAL, TokenKind.ELLIPSIS}:
                return ParensResult.EXPLICIT_LAMBDA
            elif tk == TokenKind.MONKEYS_AT:
                is_type = True
                lookahead = self.skip_annotation(lookahead)
            elif tk == TokenKind.LBRACKET:
                if self.peek_token(lookahead, TokenKind.RBRACKET, LAX_IDENTIFIER):
                    # '[', ']', Identifier/'_'/'assert'/'enum' -> explicit lambda
                    return ParensResult.EXPLICIT_LAMBDA
                if self.peek_token(lookahead, TokenKind.RBRACKET, TokenKind.RPAREN):
                    # '[', ']', ')' -> cast
                    return ParensResult.CAST
                if self.peek_token(lookahead, TokenKind.RBRACKET, TokenKind.AMP):
                    # '[', ']', '&' -> cast (intersection type)
                    return ParensResult.CAST
                if self.peek_token(lookahead, TokenKind.RBRACKET):
                    is_type = True
                    lookahead += 1
                else:
                    return ParensResult.PARENS
            elif tk == TokenKind.LT:
                depth += 1
            elif tk in {TokenKind.GT_GT_GT, TokenKind.GT_GT, TokenKind.GT}:
                if tk == TokenKind.GT_GT_GT:
                    depth -= 3
                elif tk == TokenKind.GT_GT:
                    depth -= 2
                elif tk == TokenKind.GT:
                    depth -= 1
                if depth == 0:
                    if self.peek_token(lookahead, TokenKind.RPAREN) or self.peek_token(lookahead, TokenKind.AMP):
                        # '>', ')' -> cast
                        # '>', '&' -> cast
                        return ParensResult.CAST
                    if self.peek_token(lookahead, LAX_IDENTIFIER, TokenKind.COMMA):
                        # '>', Identifier/'_'/'assert'/'enum', ',' -> explicit lambda
                        return ParensResult.EXPLICIT_LAMBDA
                    if self.peek_token(lookahead, LAX_IDENTIFIER, TokenKind.RPAREN, TokenKind.ARROW):
                        # '>', Identifier/'_'/'assert'/'enum', ')', '->' -> explicit lambda
                        return ParensResult.EXPLICIT_LAMBDA
                    if self.peek_token(lookahead, TokenKind.ELLIPSIS):
                        # '>', '...' -> explicit lambda
                        return ParensResult.EXPLICIT_LAMBDA
                    is_type = True
                elif depth < 0:
                    # unbalanced '<', '>' - not a generic type
                    return ParensResult.PARENS
            else:
                return default_result

            lookahead += 1

    def skip_annotation(self, lookahead: int) -> int:
        """跳过从当前位置之后第 lookahead 个 Token 开始的注解，返回跳过后的 lookahead（此时 lookahead 指向注解的最后一个元素）

        样例："@ interface xxx"，参数的 lookahead 指向 "@"，返回的 lookahead 指向 "interface"

        [JDK Code] JavacParser.skipAnnotation
        """
        lookahead += 1  # 跳过 @
        while self.peek_token(lookahead, TokenKind.DOT):
            lookahead += 2

        if not self.peek_token(lookahead, TokenKind.LPAREN):
            return lookahead
        lookahead += 1  # 跳过标识符

        nesting = 0  # 嵌套的括号层数（左括号比右括号多的数量）
        while True:
            tk = self._lexer.token(lookahead).kind
            print(tk, nesting)
            if tk == TokenKind.EOF:
                return lookahead
            if tk == TokenKind.LPAREN:
                nesting += 1
            if tk == TokenKind.RPAREN:
                nesting -= 1
                if nesting == 0:
                    return lookahead
            lookahead += 1

    def peek_token(self, lookahead: int, *kinds: TokenKind):
        """检查从当前位置之后的地 lookahead 开始的元素与 kinds 是否匹配"""
        for i, kind in enumerate(kinds):
            if not self._lexer.token(lookahead + i + 1).kind in kind:
                return False
        return True


if __name__ == "__main__":
    print(JavaParser(LexicalFSM("(int)")).term3())

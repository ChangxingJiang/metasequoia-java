"""
语法解析器
"""

from typing import Any, Dict, List, Optional

from metasequoia_java import ast
from metasequoia_java.ast import TreeKind
from metasequoia_java.ast.constants import INT_LITERAL_STYLE_HASH
from metasequoia_java.ast.constants import LONG_LITERAL_STYLE_HASH
from metasequoia_java.ast.element import Modifier
from metasequoia_java.grammar import enums
from metasequoia_java.grammar import hash
from metasequoia_java.grammar.parans_result import ParensResult
from metasequoia_java.grammar.parser_mode import ParserMode as Mode
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
        self.text = lexer.text
        self.lexer = lexer
        self.last_token: Optional[Token] = None  # 上一个 Token
        self.token: Optional[Token] = self.lexer.token(0)  # 当前 Token

        self.mode: Mode = Mode.NULL  # 当前解析模式
        self.last_mode: Mode = Mode.NULL  # 上一个解析模式

        # 如果 permit_type_annotations_push_back 为假，那么当解析器遇到额外的注解时会直接抛出错误；否则会将额外的注解存入 type_annotations_push_back 变量中
        self.permit_type_annotations_push_back: bool = False
        self.type_annotations_pushed_back: List[ast.AnnotationTree] = []

        # 如果 allow_this_ident 为真，则允许将 "this" 视作标识符
        self.allow_this_ident: Optional[bool] = None

        # 方法接收的第一个 this 参数类型
        self.receiver_param: Optional[ast.VariableTree] = None

    def next_token(self):
        self.lexer.next_token()
        self.last_token, self.token = self.token, self.lexer.token(0)

    def peek_token(self, lookahead: int, *kinds: TokenKind):
        """检查从当前位置之后的地 lookahead 开始的元素与 kinds 是否匹配"""
        for i, kind in enumerate(kinds):
            if not self.lexer.token(lookahead + i + 1).kind in kind:
                return False
        return True

    def accept(self, kind: TokenKind):
        if self.token.kind == kind:
            self.next_token()
        else:
            raise JavaSyntaxError(f"expect TokenKind {kind.name}({kind.value}), "
                                  f"but get {self.token.kind.name}({self.token.kind.value})")

    def _info_include(self, start_pos: Optional[int]) -> Dict[str, Any]:
        """根据开始位置 start_pos 和当前 token 的结束位置（即包含当前 token），获取当前节点的源代码和位置信息"""
        if start_pos is None:
            return {"source": None, "start_pos": None, "end_pos": None}
        end_pos = self.token.end_pos
        return {
            "source": self.text[start_pos: end_pos],
            "start_pos": start_pos,
            "end_pos": end_pos
        }

    def _info_exclude(self, start_pos: Optional[int]) -> Dict[str, Any]:
        """根据开始位置 start_pos 和当前 token 的开始位置（即不包含当前 token），获取当前节点的源代码和位置信息"""
        if start_pos is None:
            return {"source": None, "start_pos": None, "end_pos": None}
        end_pos = self.last_token.end_pos
        return {
            "source": self.text[start_pos: end_pos],
            "start_pos": start_pos,
            "end_pos": end_pos
        }

    # ------------------------------ 解析模式相关方法 ------------------------------

    def set_mode(self, mode: Mode):
        self.mode = mode

    def set_last_mode(self, mode: Mode):
        self.last_mode = mode

    def is_mode(self, mode: Mode):
        return self.mode & mode

    def was_type_mode(self):
        return self.last_mode & Mode.TYPE

    def select_expr_mode(self):
        self.set_mode((self.mode & Mode.NO_LAMBDA) | Mode.EXPR)  # 如果当前 mode 有 NO_LAMBDA 则保留，并添加 EXPR

    def select_type_mode(self):
        self.set_mode((self.mode & Mode.NO_LAMBDA) | Mode.TYPE)  # 如果当前 mode 有 NO_LAMBDA 则保留，并添加 TYPE

    # ------------------------------ 报错信息相关方法 ------------------------------

    def syntax_error(self, pos: int, message: str):
        """报告语法错误"""
        raise JavaSyntaxError(f"报告语法错误: pos={pos}, message={message}")

    def illegal(self, pos: Optional[int] = None):
        """报告表达式或类型的非法开始 Token"""
        if pos is None:
            pos = self.token.pos
        if self.is_mode(Mode.EXPR):
            self.syntax_error(pos, "IllegalStartOfExpr")
        else:
            self.syntax_error(pos, "IllegalStartOfType")

    # ------------------------------ Chapter 3 : Lexical Structure ------------------------------

    def ident_or_underscore(self) -> str:
        """标识符或下划线

        [JDK Code] JavacParser.identOrUnderscore
        """
        return self.ident()

    def ident(self) -> str:
        """标识符的名称

        [JDK Document] https://docs.oracle.com/javase/specs/jls/se22/html/jls-19.html
        Identifier:
          IdentifierChars but not a ReservedKeyword or BooleanLiteral or NullLiteral

        [JDK Code] JavacParser.ident

        Examples
        --------
        >>> JavaParser(LexicalFSM("abc")).ident()
        'abc'
        """
        if self.token.kind == TokenKind.IDENTIFIER:
            name = self.token.name
            self.next_token()
            return name
        if self.token.kind == TokenKind.ASSERT:
            self.syntax_error(self.token.pos, f"AssertAsIdentifier")
        if self.token.kind == TokenKind.ENUM:
            self.syntax_error(self.token.pos, f"EnumAsIdentifier")
        if self.token.kind == TokenKind.THIS:
            if self.allow_this_ident:
                name = self.token.name
                self.next_token()
                return name
            else:
                self.syntax_error(self.token.pos, f"ThisAsIdentifier")
        if self.token.kind == TokenKind.UNDERSCORE:
            name = self.token.name
            self.next_token()
            return name
        self.accept(TokenKind.IDENTIFIER)
        raise JavaSyntaxError(f"{self.token.source} 不能作为 Identifier")

    def qualident(self, allow_annos: bool):
        """多个用 DOT 分隔的标识符

        [JDK Document]
        ModuleName:
          Identifier
          ModuleName . Identifier

        PackageName:
          Identifier
          PackageName . Identifier

        [JDK Code] JavacParser.qualident
        Qualident = Ident { DOT [Annotations] Ident }

        Examples
        --------
        >>> JavaParser(LexicalFSM("abc.def")).qualident(False).kind
        <TreeKind.MEMBER_SELECT: 19>
        >>> JavaParser(LexicalFSM("abc.def")).qualident(False).source
        'abc.def'

        TODO 补充单元测试：allow_annotations = True
        """
        pos = self.token.pos
        expression: ast.ExpressionTree = ast.IdentifierTree.create(
            name=self.ident(),
            **self._info_exclude(pos)
        )
        while self.token.kind == TokenKind.DOT:
            self.next_token()
            type_annotations = self.type_annotations_opt() if allow_annos is True else None
            identifier: ast.IdentifierTree = ast.IdentifierTree.create(
                name=self.ident(),
                **self._info_exclude(pos)
            )
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

    def type_name(self) -> ast.IdentifierTree:
        """解析 TypeIdentifier 元素

        [JDK Document] https://docs.oracle.com/javase/specs/jls/se22/html/jls-19.html
        TypeIdentifier:
          Identifier but not permits, record, sealed, var, or yield

        [JDK Code] JavacParser.typeName
        """
        if self.token.kind != TokenKind.IDENTIFIER:
            raise JavaSyntaxError(f"expect type_identifier, but get {self.token.source}")
        if self.token.name in {"permits", "record", "sealed", "var", "yield"}:
            raise JavaSyntaxError(f"expect type_identifier, but get {self.token.name}")

        pos = self.token.pos
        name = self.token.name
        self.next_token()
        return ast.IdentifierTree.create(
            name=name,
            **self._info_exclude(pos)
        )

    def unqualified_method_identifier(self) -> ast.IdentifierTree:
        """解析 UnqualifiedMethodIdentifier 元素

        [JDK Document] https://docs.oracle.com/javase/specs/jls/se22/html/jls-19.html
        UnqualifiedMethodIdentifier:
          Identifier but not yield
        """
        if self.token.kind != TokenKind.IDENTIFIER:
            raise JavaSyntaxError(f"{self.token.source} 不能作为 UnqualifiedMethodIdentifier")
        if self.token.name in {"yield"}:
            raise JavaSyntaxError(f"{self.token.name} 不能作为 UnqualifiedMethodIdentifier")

        pos = self.token.pos
        name = self.token.name
        self.next_token()
        return ast.IdentifierTree.create(
            name=name,
            **self._info_exclude(pos)
        )

    def literal(self) -> ast.LiteralTree:
        """解析字面值

        [JDK Document] https://docs.oracle.com/javase/specs/jls/se22/html/jls-19.html
        Literal:
          IntegerLiteral
          FloatingPointLiteral
          BooleanLiteral
          CharacterLiteral
          StringLiteral
          TextBlock
          NullLiteral

        [Jdk Code] JavacParser.literal
        """
        pos = self.token.pos
        if self.token.kind in {TokenKind.INT_OCT_LITERAL, TokenKind.INT_DEC_LITERAL, TokenKind.INT_HEX_LITERAL}:
            return ast.IntLiteralTree.create(
                style=INT_LITERAL_STYLE_HASH[self.token.kind],
                value=self.token.int_value(),
                **self._info_include(pos)
            )
        if self.token.kind in {TokenKind.LONG_OCT_LITERAL, TokenKind.LONG_DEC_LITERAL, TokenKind.LONG_HEX_LITERAL}:
            return ast.LongLiteralTree.create(
                style=LONG_LITERAL_STYLE_HASH[self.token.kind],
                value=self.token.int_value(),
                **self._info_include(pos)
            )
        if self.token.kind == TokenKind.FLOAT_LITERAL:
            return ast.FloatLiteralTree.create(
                value=self.token.float_value(),
                **self._info_include(pos)
            )
        if self.token.kind == TokenKind.DOUBLE_LITERAL:
            return ast.DoubleLiteralTree.create(
                value=self.token.float_value(),
                **self._info_include(pos)
            )
        if self.token.kind == TokenKind.TRUE:
            return ast.TrueLiteralTree.create(
                **self._info_include(pos)
            )
        if self.token.kind == TokenKind.FALSE:
            return ast.FalseLiteralTree.create(
                **self._info_include(pos)
            )
        if self.token.kind == TokenKind.CHAR_LITERAL:
            return ast.CharacterLiteralTree.create(
                value=self.token.char_value(),
                **self._info_include(pos)
            )
        if self.token.kind == TokenKind.STRING_LITERAL:
            return ast.StringLiteralTree.create_string(
                value=self.token.string_value(),
                **self._info_include(pos)
            )
        if self.token.kind == TokenKind.TEXT_BLOCK:
            return ast.StringLiteralTree.create_text_block(
                value=self.token.string_value(),
                **self._info_include(pos)
            )
        if self.token.kind == TokenKind.NULL:
            return ast.NullLiteralTree.create(
                **self._info_include(pos)
            )
        raise JavaSyntaxError(f"{self.token.source} 不是字面值")

    def parse_expression(self) -> ast.ExpressionTree:
        """表达式（可以是表达式或类型）

        [JDK Code] JavacParser.parseExpression
        """
        return self.term(Mode.EXPR)

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
            pos = self.token.pos
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
        if self.token.kind != TokenKind.LT:
            return []

        self.next_token()
        if parse_empty is True and self.token.kind == TokenKind.GT:
            self.accept(TokenKind.GT)
            return []

        ty_params: List[ast.TypeParameterTree] = [self.type_parameter()]
        while self.token.kind == TokenKind.COMMA:
            self.next_token()
            ty_params.append(self.type_parameter())
        self.accept(TokenKind.GT)
        return ty_params

    def type_parameter(self) -> ast.TypeParameterTree:
        """类型参数

        [JDK Code] JavacParser.typeParameter
        TypeParameter = [Annotations] TypeVariable [TypeParameterBound]
        TypeParameterBound = EXTENDS Type {"&" Type}
        TypeVariable = Ident

        TODO 待补充单元测试
        """
        pos = self.token.pos
        annotations: List[ast.AnnotationTree] = self.type_annotations_opt()
        name: ast.IdentifierTree = self.type_name()
        bounds: List[ast.ExpressionTree] = []
        if self.token.kind == TokenKind.EXTENDS:
            self.next_token()
            bounds.append(self.parse_type())
            while self.token.kind == TokenKind.AMP:
                self.next_token()
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
        if self.token.kind != TokenKind.LT:
            return None
        return self.type_arguments(False)

    def type_arguments(self, diamond_allowed: bool) -> List[ast.ExpressionTree]:
        """多个类型实参

        [JDK Code] JavacParser.typeArguments
        TypeArguments  = "<" TypeArgument {"," TypeArgument} ">"

        TODO 待补充单元测试
        """
        if self.token.kind != TokenKind.LT:
            raise JavaSyntaxError(f"expect TokenKind.LT in type_arguments, but find {self.token.kind}")

        self.next_token()
        if self.token.kind == TokenKind.GT and diamond_allowed:
            self.set_mode(self.mode | Mode.DIAMOND)
            self.next_token()
            return []

        args = [self.type_argument() if not self.is_mode(Mode.EXPR) else self.parse_type()]
        while self.token.kind == TokenKind.COMMA:
            self.next_token()
            args.append(self.type_argument() if not self.is_mode(Mode.EXPR) else self.parse_type())

        if self.token.kind in {TokenKind.GT_GT, TokenKind.GT_EQ, TokenKind.GT_GT_GT, TokenKind.GT_GT_EQ,
                               TokenKind.GT_GT_GT_EQ}:
            self.token = self.lexer.split()
        elif self.token.kind == TokenKind.GT:
            self.next_token()
        else:
            raise JavaSyntaxError(f"expect GT or COMMA in type_arguments, but find {self.token.kind}")

        return args

    def type_argument(self) -> ast.ExpressionTree:
        """类型实参

        [JDK Document] https://docs.oracle.com/javase/specs/jls/se22/html/jls-19.html
        TypeArgument:
          ReferenceType
          Wildcard

        Wildcard:
          {Annotation} ? [WildcardBounds]

        WildcardBounds:
          extends ReferenceType
          super ReferenceType

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
        pos_1 = self.token.pos
        annotations: List[ast.AnnotationTree] = self.type_annotations_opt()
        if self.token.kind != TokenKind.QUES:
            return self.parse_type(False, annotations)
        pos_2 = self.token.pos
        self.next_token()
        if self.token.kind == TokenKind.EXTENDS:
            self.next_token()
            wildcard = ast.WildcardTree.create_extends_wildcard(
                bound=self.parse_type(),
                **self._info_include(pos_2)
            )
        elif self.token.kind == TokenKind.SUPER:
            self.next_token()
            wildcard = ast.WildcardTree.create_super_wildcard(
                bound=self.parse_type(),
                **self._info_include(pos_2)
            )
        elif self.token.kind == TokenKind.GT:
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
        return []

    def unannotated_type(self, allow_var: bool = False) -> ast.ExpressionTree:
        """解析不包含注解的类型

        [JDK Code] JavacParser.unannotatedType

        TODO 待增加 allowVar 相关逻辑
        TODO 待增加单元测试
        """
        self.next_token()  # TODO 临时返回 Mock 结果
        return ast.PrimitiveTypeTree.mock("INT")  # TODO 临时返回 Mock 结果

        result = self.term()
        if result.kind == TokenKind.IDENTIFIER and result.source in {"var", "yield", "record", "sealed", "permits"}:
            raise JavaSyntaxError(f"expect unannotated_type, but get {result.kind}")
        # TODO 待增加 TYPEARRAY 相关逻辑
        return result

    def term(self, new_mode: int) -> ast.ExpressionTree:
        """TODO 名称待整理

        [JDK Code] JavacParser.term
        """

    def parse_intersection_type(self, pos: int, first_type: ast.ExpressionTree):
        """解析 CAST 语句中的交叉类型

        [JDK Document] https://docs.oracle.com/javase/specs/jls/se22/html/jls-19.html
        AdditionalBound:
          & InterfaceType

        [JDK Code] JavacParser.parseIntersectionType
        """
        bounds = [first_type]
        while self.token.kind == TokenKind.AMP:
            self.accept(TokenKind.AMP)
            bounds.append(self.parse_type())
        if len(bounds) > 1:
            return ast.IntersectionTypeTree.create(
                bounds=bounds,
                **self._info_include(pos)
            )
        return first_type

    def term_rest(self, expression: ast.ExpressionTree) -> ast.ExpressionTree:
        """解析第 0 层级语法元素的剩余部分"""
        return expression  # TODO 待开发方法逻辑

    def term_1_rest(self, expression: ast.ExpressionTree) -> ast.ExpressionTree:
        """解析第 1 层级语法元素的剩余部分"""
        return expression  # TODO 待开发方法逻辑

    def term_2_rest(self, expression: ast.ExpressionTree, min_prec: int) -> ast.ExpressionTree:
        """解析第 2 层级语法元素的剩余部分"""
        return expression  # TODO 待开发方法逻辑

    def term_3(self) -> ast.ExpressionTree:
        """解析第 3 层级语法元素

        [JDK Document] https://docs.oracle.com/javase/specs/jls/se22/html/jls-19.html（不包含在代码中已单独注释的语义组）


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

        TODO 待补充单元测试：类型实参
        TODO 待补充单元测试：类型实参

        Examples
        --------
        >>> JavaParser(LexicalFSM("++a")).term_3().kind.name
        'PREFIX_INCREMENT'
        >>> JavaParser(LexicalFSM("(int)")).term_3().kind.name
        'TYPE_CAST'
        >>> JavaParser(LexicalFSM("(x, y)->{ return x + y; }")).term_3().kind.name
        'LAMBDA_EXPRESSION'
        """
        pos = self.token.pos
        type_args = self.type_arguments_opt()

        # 类型实参
        if self.token.kind == TokenKind.QUES:
            if self.is_mode(Mode.TYPE) and self.is_mode(Mode.TYPE_ARG) and not self.is_mode(Mode.NO_PARAMS):
                self.select_type_mode()
                return self.type_argument()
            self.illegal()

        # 一元表达式
        # [JDK Document] https://docs.oracle.com/javase/specs/jls/se22/html/jls-19.html
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
        #   CastExpression 【不包含】
        #   SwitchExpression 【不包含】
        if self.token.kind in {TokenKind.PLUS_PLUS, TokenKind.SUB_SUB, TokenKind.BANG, TokenKind.TILDE, TokenKind.PLUS,
                               TokenKind.SUB}:
            if type_args is not None and self.is_mode(Mode.EXPR):
                self.syntax_error(pos, "Illegal")  # TODO 待增加说明信息
            tk = self.token.kind
            self.next_token()
            self.select_expr_mode()
            if tk == TokenKind.SUB and self.token.kind in {TokenKind.INT_DEC_LITERAL, TokenKind.LONG_DEC_LITERAL}:
                self.select_expr_mode()
                return self.term_3_rest(self.literal(), type_args)

            expression = self.term_3()
            return ast.UnaryTree.create(
                operator=tk,
                expression=expression,
                **self._info_include(pos)
            )

        if self.token.kind == TokenKind.LPAREN:
            if type_args is not None and self.is_mode(Mode.EXPR):
                raise JavaSyntaxError("语法不合法")
            pres: ParensResult = self.analyze_parens()

            # [JDK Document] https://docs.oracle.com/javase/specs/jls/se22/html/jls-19.html
            # CastExpression:
            #   ( PrimitiveType ) UnaryExpression
            #   ( ReferenceType {AdditionalBound} ) UnaryExpressionNotPlusMinus
            #   ( ReferenceType {AdditionalBound} ) LambdaExpression
            if pres == ParensResult.CAST:
                self.accept(TokenKind.LPAREN)
                self.select_type_mode()
                cast_type = self.parse_intersection_type(pos, self.parse_type())
                self.accept(TokenKind.RPAREN)
                self.select_expr_mode()
                expression = self.term_3()
                return ast.TypeCastTree.create(
                    cast_type=cast_type,
                    expression=expression,
                    **self._info_include(pos)
                )

            # lambda 表达式
            if pres == ParensResult.IMPLICIT_LAMBDA:
                expression = self.lambda_expression_or_statement(True, False, pos)
            elif pres == ParensResult.EXPLICIT_LAMBDA:
                expression = self.lambda_expression_or_statement(True, True, pos)

            # 括号表达式
            else:  # ParensResult.PARENS
                self.accept(TokenKind.LPAREN)
                self.select_expr_mode()
                expression = self.term_rest(self.term_1_rest(self.term_2_rest(self.term_3(),
                                                                              enums.OperatorPrecedence.OR_PREC)))
                self.accept(TokenKind.RPAREN)
                expression = ast.ParenthesizedTree.create(
                    expression=expression,
                    **self._info_exclude(pos)
                )
            return self.term_3_rest(expression, type_args)

        if self.token.kind == TokenKind.THIS:
            if self.is_mode(Mode.EXPR):
                self.select_expr_mode()
                expression = ast.IdentifierTree.create(
                    name="this",
                    **self._info_include(pos)
                )
                self.next_token()
                if type_args is None:
                    self.type_arguments_opt()

    def term_3_rest(self, expression: ast.ExpressionTree,
                    type_args: Optional[List[ast.ExpressionTree]]) -> ast.ExpressionTree:
        """解析第 3 层级语法元素的剩余部分"""
        return expression  # TODO 待开发方法逻辑

    def analyze_parens(self) -> ParensResult:
        """分析括号中的内容

        [JDK Code] JavacParser.analyzeParens
        """
        depth = 0
        is_type = False
        lookahead = 0
        default_result = ParensResult.PARENS
        while True:
            tk = self.lexer.token(lookahead).kind
            if tk == TokenKind.COMMA:
                is_type = True
            elif tk in {TokenKind.EXTENDS, TokenKind.SUPER, TokenKind.DOT, TokenKind.AMP}:
                continue  # 跳过
            elif tk == TokenKind.QUES:
                if self.lexer.token(lookahead + 1).kind in {TokenKind.EXTENDS, TokenKind.SUPER}:
                    is_type = True  # wildcards
            elif tk in {TokenKind.BYTE, TokenKind.SHORT, TokenKind.INT, TokenKind.LONG, TokenKind.FLOAT,
                        TokenKind.FLOAT, TokenKind.DOUBLE, TokenKind.BOOLEAN, TokenKind.CHAR, TokenKind.VOID}:
                if self.lexer.token(lookahead + 1).kind == TokenKind.RPAREN:
                    # Type, ')' -> cast
                    return ParensResult.CAST
                if self.lexer.token(lookahead + 1).kind in LAX_IDENTIFIER:
                    # Type, Identifier/'_'/'assert'/'enum' -> explicit lambda
                    return ParensResult.EXPLICIT_LAMBDA
            elif tk == TokenKind.LPAREN:
                if lookahead != 0:
                    # // '(' in a non-starting position -> parens
                    return ParensResult.PARENS
                if self.lexer.token(lookahead + 1).kind == TokenKind.RPAREN:
                    # // '(', ')' -> explicit lambda
                    return ParensResult.EXPLICIT_LAMBDA
            elif tk == TokenKind.RPAREN:
                if is_type is True:
                    return ParensResult.CAST
                if self.lexer.token(lookahead + 1).kind in {
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
                if self.lexer.token(lookahead + 1).kind in LAX_IDENTIFIER:
                    # Identifier, Identifier/'_'/'assert'/'enum' -> explicit lambda
                    return ParensResult.EXPLICIT_LAMBDA
                if (self.lexer.token(lookahead + 1).kind == TokenKind.RPAREN
                        and self.lexer.token(lookahead + 2).kind == TokenKind.ARROW):
                    # // Identifier, ')' '->' -> implicit lambda
                    # TODO 待增加 isMode 的逻辑
                    return ParensResult.IMPLICIT_LAMBDA
                if depth == 0 and self.lexer.token(lookahead + 1).kind == TokenKind.COMMA:
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
            tk = self.lexer.token(lookahead).kind
            if tk == TokenKind.EOF:
                return lookahead
            if tk == TokenKind.LPAREN:
                nesting += 1
            if tk == TokenKind.RPAREN:
                nesting -= 1
                if nesting == 0:
                    return lookahead
            lookahead += 1

    def lambda_expression_or_statement(self, has_parens: bool, explicit_params: bool, pos: int) -> ast.ExpressionTree:
        """lambda 表达式或 lambda 语句

        [JDK Document] https://docs.oracle.com/javase/specs/jls/se22/html/jls-19.html
        LambdaExpression:
          LambdaParameters -> LambdaBody

        [JDK Code] JavacParser.lambdaExpressionOrStatement

        TODO 考虑是否需要增加 lambda 表达式中显式、隐式混用的场景（LambdaClassifier 的逻辑）

        Examples
        --------
        >>> result1 = JavaParser(LexicalFSM("()->{}")).lambda_expression_or_statement(True, False, 0)
        >>> result1.kind.name
        'LAMBDA_EXPRESSION'
        >>> result1 = JavaParser(LexicalFSM("(int x)->x + 3")).lambda_expression_or_statement(True, True, 0)
        >>> result1.kind.name
        'LAMBDA_EXPRESSION'
        >>> result1 = JavaParser(LexicalFSM("(x, y)->{ return x + y; }")).lambda_expression_or_statement(True, False, 0)
        >>> result1.kind.name
        'LAMBDA_EXPRESSION'
        """
        if explicit_params is True:
            parameters = self.formal_parameters(True, False)
        else:
            parameters = self.implicit_parameters(has_parens)
        return self.lambda_expression_or_statement_rest(parameters, pos)

    def lambda_expression_or_statement_rest(self, parameters: List[ast.VariableTree], pos: int) -> ast.ExpressionTree:
        """lambda 表达式或 lambda 语句除参数外的剩余部分

        [JDK Document] https://docs.oracle.com/javase/specs/jls/se22/html/jls-19.html
        LambdaBody:
          Expression
          Block

        [JDK Code] JavacParser.lambdaExpressionOrStatementRest
        """
        self.accept(TokenKind.ARROW)
        if self.token.kind == TokenKind.LBRACE:
            return self.lambda_statement(parameters, pos, self.token.pos)
        return self.lambda_expression(parameters, pos)

    def lambda_statement(self, parameters: List[ast.VariableTree], pos: int, pos2: int) -> ast.ExpressionTree:
        """lambda 语句的语句部分

        [JDK Code] JavacParser.lambdaStatement
        """
        block: ast.BlockTree = self.block(pos2, 0)
        return ast.LambdaExpressionTree.create_statement(
            parameters=parameters,
            body=block,
            **self._info_exclude(pos)
        )

    def lambda_expression(self, parameters: List[ast.VariableTree], pos: int) -> ast.ExpressionTree:
        """lambda 表达式的表达式部分

        [JDK Code] JavacParser.lambdaExpression
        """
        expr: ast.ExpressionTree = self.parse_expression()
        return ast.LambdaExpressionTree.create_expression(
            parameters=parameters,
            body=expr,
            **self._info_exclude(pos)
        )

    def brackets_opt(self, expression: ast.ExpressionTree, annotations: Optional[List[ast.AnnotationTree]] = None):
        """可选的数组标记（空方括号）

        [JDK Document] https://docs.oracle.com/javase/specs/jls/se22/html/jls-19.html
        Dims:
          {Annotation} [ ] {{Annotation} [ ]}

        [JDK Code] JavacParser.bracketsOpt
        BracketsOpt = { [Annotations] "[" "]" }*

        Examples
        --------
        >>> JavaParser(LexicalFSM(" = 5")).brackets_opt(ast.IdentifierTree.mock(name="ident"))
        IdentifierTree(kind=<TreeKind.IDENTIFIER: 22>, source=None, start_pos=None, end_pos=None, name='ident')
        >>> JavaParser(LexicalFSM("[] = 5")).brackets_opt(ast.IdentifierTree.mock(name="ident")).source
        '[]'
        >>> JavaParser(LexicalFSM("[][] = 5")).brackets_opt(ast.IdentifierTree.mock(name="ident")).source
        '[][]'
        """
        if annotations is None:
            annotations = []

        next_level_annotations: List[ast.AnnotationTree] = self.type_annotations_opt()
        if self.token.kind == TokenKind.LBRACKET:
            pos = self.token.pos
            self.next_token()
            expression = self.brackets_opt_cont(expression, pos, next_level_annotations)
        elif len(next_level_annotations) > 0:
            if self.permit_type_annotations_push_back is True:
                self.type_annotations_pushed_back = next_level_annotations
            else:
                return self.illegal(next_level_annotations[0].start_pos)

        if len(annotations) > 0:
            return ast.AnnotatedTypeTree.create(
                annotations=annotations,
                underlying_type=expression,
                **self._info_include(self.token.pos)
            )
        return expression

    def brackets_opt_cont(self, expression: ast.ExpressionTree, pos: int, annotations: List[ast.AnnotationTree]):
        """构造数组类型对象"""
        self.accept(TokenKind.RBRACKET)
        expression = self.brackets_opt(expression)
        expression = ast.ArrayTypeTree.create(
            expression=expression,
            **self._info_exclude(pos)
        )
        if len(annotations):
            expression = ast.AnnotatedTypeTree.create(
                annotations=annotations,
                underlying_type=expression,
                **self._info_exclude(pos)
            )
        return expression

    def block(self, pos: int, flags: int) -> ast.BlockTree:
        """解析代码块

        [JDK Code] JavacParser.block
        Block = "{" BlockStatements "}"
        """
        return ast.BlockTree.mock()  # TODO 待开发真实执行逻辑

    def modifiers_opt(self, partial: Optional[ast.ModifiersTree] = None) -> ast.ModifiersTree:
        """修饰词

        [JDK Document] https://docs.oracle.com/javase/specs/jls/se22/html/jls-19.html
        ClassModifier:
          (one of)
          Annotation public protected private
          abstract static final sealed non-sealed strictfp

        FieldModifier:
          (one of)
          Annotation public protected private
          static final transient volatile

        MethodModifier:
          (one of)
          Annotation public protected private
          abstract static final synchronized native strictfp

        VariableModifier:
          Annotation
          final

        ConstructorModifier:
          (one of)
          Annotation public protected private

        InterfaceModifier:
          (one of)
          Annotation public protected private
          abstract static sealed non-sealed strictfp

        ConstantModifier:
          (one of)
          Annotation public
          static final

        InterfaceMethodModifier:
          (one of)
          Annotation public private
          abstract default static strictfp

        AnnotationInterfaceElementModifier:
          (one of)
          Annotation public
          abstract

        [JDK Code] JavacParser.modifiersOpt
        ModifiersOpt = { Modifier }
        Modifier = PUBLIC | PROTECTED | PRIVATE | STATIC | ABSTRACT | FINAL
                 | NATIVE | SYNCHRONIZED | TRANSIENT | VOLATILE | "@"
                 | "@" Annotation

        Examples
        --------
        >>> JavaParser(LexicalFSM("non-sealed class")).modifiers_opt(None).flags
        [<Modifier.NON_SEALED: 'non-sealed'>]
        >>> JavaParser(LexicalFSM("public class")).modifiers_opt(None).flags
        [<Modifier.PUBLIC: 'public'>]
        >>> JavaParser(LexicalFSM("public static class")).modifiers_opt(None).flags
        [<Modifier.PUBLIC: 'public'>, <Modifier.STATIC: 'static'>]
        >>> JavaParser(LexicalFSM("public static final NUMBER")).modifiers_opt(None).flags
        [<Modifier.PUBLIC: 'public'>, <Modifier.STATIC: 'static'>, <Modifier.FINAL: 'final'>]
        """
        if partial is not None:
            flags = partial.flags
            annotations = partial.annotations
            pos = partial.start_pos
        else:
            flags = []
            annotations = []
            pos = self.token.pos

        if self.token.deprecated_flag():
            flags.append(Modifier.DEPRECATED)

        while True:
            tk = self.token.kind
            if flag := hash.TOKEN_TO_MODIFIER.get(tk):
                flags.append(flag)
                self.next_token()
            elif tk == TokenKind.MONKEYS_AT:
                last_pos = self.token.pos
                self.next_token()
                if self.token.kind != TokenKind.INTERFACE:
                    annotation = self.annotation(last_pos, None)  # TODO 待修改参数
                    # if first modifier is an annotation, set pos to annotation's
                    if len(flags) == 0 and len(annotations) == 0:
                        pos = annotation.start_pos
                    annotations.append(annotation)
                    flags = []
            elif tk == TokenKind.IDENTIFIER:
                if self.is_non_sealed_class_start(False):
                    flags.append(Modifier.NON_SEALED)
                    self.next_token()
                    self.next_token()
                    self.next_token()
                if self.is_sealed_class_start(False):
                    flags.append(Modifier.SEALED)
                    self.next_token()
                break
            else:
                break

        if len(flags) > len(set(flags)):
            self.syntax_error(pos, "RepeatedModifier(存在重复的修饰符)")

        tk = self.token.kind
        if tk == TokenKind.ENUM:
            flags.append(Modifier.ENUM)
        elif tk == TokenKind.INTERFACE:
            flags.append(Modifier.INTERFACE)

        if len([flag for flag in flags if not flag.is_virtual()]) == 0 and len(annotations) == 0:
            pos = None

        return ast.ModifiersTree.create(
            flags=flags,
            annotations=annotations,
            **self._info_exclude(pos)
        )

    def variable_declarator_id(self,
                               modifiers: ast.ModifiersTree,
                               variable_type: Optional[ast.ExpressionTree],
                               catch_parameter: bool,
                               lambda_parameter: bool):
        """解析变量声明语句中的标识符

        [JDK Document] https://docs.oracle.com/javase/specs/jls/se22/html/jls-19.html
        VariableDeclaratorId:
          Identifier [Dims]
          _

        [JDK Code] JavacParser.variableDeclaratorId
        VariableDeclaratorId = Ident BracketsOpt

        Examples
        --------
        >>> JavaParser(LexicalFSM("abc")).variable_declarator_id(ast.ModifiersTree.mock(), None, False, False).kind
        <TreeKind.VARIABLE: 54>
        >>> JavaParser(LexicalFSM("abc")).variable_declarator_id(ast.ModifiersTree.mock(), None, False, False).source
        'abc'
        >>> JavaParser(LexicalFSM("abc[]")).variable_declarator_id(ast.ModifiersTree.mock(), None, False, False).kind
        <TreeKind.VARIABLE: 54>
        >>> JavaParser(LexicalFSM("abc[]")).variable_declarator_id(ast.ModifiersTree.mock(),
        ...                                                        None, False, False).variable_type.kind
        <TreeKind.ARRAY_TYPE: 5>
        """
        if modifiers.start_pos is not None:
            pos = modifiers.start_pos
        elif variable_type is not None:
            pos = variable_type.start_pos
        else:
            pos = self.token.pos
        if (self.allow_this_ident is False
                and lambda_parameter is True
                and self.token.kind not in LAX_IDENTIFIER
                and modifiers.flags == Modifier.PARAMETER
                and len(modifiers.annotations) == 0):
            self.syntax_error(pos, "这是一个 lambda 表达式的参数，且 Token 类型不是标识符，且没有任何修饰符或注解，则意味着编译"
                                   "器本应假设该 lambda 表达式为显式形式，但它可能包含隐式参数或显式参数的混合")

        if self.token.kind == TokenKind.UNDERSCORE and (catch_parameter or lambda_parameter):
            expression = ast.IdentifierTree.create(
                name=self.ident_or_underscore(),
                **self._info_exclude(pos)
            )
        else:
            expression = self.qualident(False)

        if expression.kind == TreeKind.IDENTIFIER and expression.name != "this":
            variable_type = self.brackets_opt(variable_type)
            return ast.VariableTree.create_by_name(
                modifiers=modifiers,
                name=expression.name,
                variable_type=variable_type,
                **self._info_exclude(pos)
            )
        if lambda_parameter and variable_type is None:
            self.syntax_error(pos, "we have a lambda parameter that is not an identifier this is a syntax error")
        else:
            return ast.VariableTree.create_by_name_expression(
                modifiers=modifiers,
                name_expression=expression,
                variable_type=variable_type,
                **self._info_include(pos)
            )

    def annotation(self, pos: int, kind: Any) -> ast.AnnotationTree:
        """TODO"""

    def formal_parameters(self,
                          lambda_parameter: bool = False,
                          record_component: bool = False) -> List[ast.VariableTree]:
        """形参的列表

        [JDK Document] https://docs.oracle.com/javase/specs/jls/se22/html/jls-19.html
        匹配: ( [ReceiverParameter ,] [FormalParameterList] )

        FormalParameterList:
          FormalParameter {, FormalParameter}

        LambdaParameters: 【部分包含】
          ( [LambdaParameterList] )
          ConciseLambdaParameter

        LambdaParameterList:
          NormalLambdaParameter {, NormalLambdaParameter}
          ConciseLambdaParameter {, ConciseLambdaParameter} 【不包含】

        [JDK Code] JavacParser.formalParameters
        FormalParameters = "(" [ FormalParameterList ] ")"
        FormalParameterList = [ FormalParameterListNovarargs , ] LastFormalParameter
        FormalParameterListNovarargs = [ FormalParameterListNovarargs , ] FormalParameter

        Examples
        --------
        >>> result = JavaParser(LexicalFSM("(int name1, String name2)")).formal_parameters()
        >>> len(result)
        2
        >>> result[0].name
        'name1'
        >>> result[1].name
        'name2'
        """
        self.accept(TokenKind.LPAREN)
        params: List[ast.VariableTree] = []
        if self.token.kind != TokenKind.RPAREN:
            self.allow_this_ident = not lambda_parameter and not record_component
            last_param = self.formal_parameter(lambda_parameter, record_component)
            if last_param.name_expression is not None:
                self.receiver_param = last_param
            else:
                params.append(last_param)
            self.allow_this_ident = False
            while self.token.kind == TokenKind.COMMA:
                self.next_token()
                params.append(self.formal_parameter(lambda_parameter, record_component))
        if self.token.kind != TokenKind.RPAREN:
            self.syntax_error(self.token.pos, f"expect COMMA, RPAREN or LBRACKET, but get {self.token.kind}")
        self.next_token()
        return params

    def implicit_parameters(self, has_parens: bool):
        """隐式形参的列表

        [JDK Document] https://docs.oracle.com/javase/specs/jls/se22/html/jls-19.html
        LambdaParameters: 【部分包含】
          ( [LambdaParameterList] )
          ConciseLambdaParameter

        LambdaParameterList:
          NormalLambdaParameter {, NormalLambdaParameter} 【不包含】
          ConciseLambdaParameter {, ConciseLambdaParameter}

        [JDK Code] JavacParser.implicitParameters

        Examples
        --------
        >>> result = JavaParser(LexicalFSM("name1, name2")).implicit_parameters(False)
        >>> len(result)
        2
        >>> result[0].name
        'name1'
        >>> result[1].name
        'name2'
        >>> result = JavaParser(LexicalFSM("(name1, name2)")).implicit_parameters(True)
        >>> len(result)
        2
        >>> result[0].name
        'name1'
        >>> result[1].name
        'name2'
        """
        if has_parens is True:
            self.accept(TokenKind.LPAREN)
        params = []
        if self.token.kind not in {TokenKind.RPAREN, TokenKind.ARROW}:
            params.append(self.implicit_parameter())
            while self.token.kind == TokenKind.COMMA:
                self.next_token()
                params.append(self.implicit_parameter())
        if has_parens is True:
            self.accept(TokenKind.RPAREN)
        return params

    def formal_parameter(self,
                         lambda_parameter: bool = False,
                         record_component: bool = False) -> ast.VariableTree:
        """形参

        [JDK Document] https://docs.oracle.com/javase/specs/jls/se22/html/jls-19.html
        ReceiverParameter:
          {Annotation} UnannType [Identifier .] this

        FormalParameter:
          {VariableModifier} UnannType VariableDeclaratorId
          VariableArityParameter

        VariableArityParameter:
          {VariableModifier} UnannType {Annotation} ... Identifier

        NormalLambdaParameter:
          {VariableModifier} LambdaParameterType VariableDeclaratorId
          VariableArityParameter

        LambdaParameterType:
          UnannType
          var

        [JDK Code] JavacParser.formalParameter
        FormalParameter = { FINAL | '@' Annotation } Type VariableDeclaratorId
        LastFormalParameter = { FINAL | '@' Annotation } Type '...' Ident | FormalParameter

        Examples
        --------
        >>> JavaParser(LexicalFSM("int name1")).formal_parameter().kind.name
        'VARIABLE'
        >>> JavaParser(LexicalFSM("int name1")).formal_parameter().name
        'name1'
        """
        if record_component is True:
            modifiers = self.modifiers_opt()
        else:
            modifiers = self.opt_final(flags=[Modifier.PARAMETER])

        if record_component is True:
            modifiers.flags |= {Modifier.RECORD, Modifier.FINAL, Modifier.PRIVATE, Modifier.GENERATED_MEMBER}

        self.permit_type_annotations_push_back = True
        param_type = self.parse_type(allow_var=False)
        self.permit_type_annotations_push_back = False

        if self.token.kind == TokenKind.ELLIPSIS:
            varargs_annotations: List[ast.AnnotationTree] = self.type_annotations_pushed_back
            modifiers.flags.append(Modifier.VARARGS)
            # TODO 考虑是否需要增加 insertAnnotationsToMostInner 的逻辑
            param_type = ast.AnnotatedTypeTree.create(
                annotations=varargs_annotations,
                underlying_type=param_type,
                **self._info_include(None)
            )
            self.next_token()
        self.type_annotations_pushed_back = []
        return self.variable_declarator_id(modifiers, param_type, False, lambda_parameter)

    def implicit_parameter(self) -> ast.VariableTree:
        """隐式形参

        [JDK Document] https://docs.oracle.com/javase/specs/jls/se22/html/jls-19.html
        ConciseLambdaParameter:
          Identifier
          _

        [JDK Code] JavacParser.implicitParameter

        >>> result = JavaParser(LexicalFSM("name1")).implicit_parameter()
        >>> result.name
        'name1'
        """
        modifiers = ast.ModifiersTree.create(
            flags=[Modifier.PARAMETER],
            **self._info_include(self.token.pos)  # TODO 下标待修正
        )
        return self.variable_declarator_id(modifiers, None, False, True)

    def is_non_sealed_class_start(self, local: bool):
        """如果从当前 Token 开始为 non-sealed 关键字则返回 True，否则返回 False

        [JDK Code] JavacParser.isNonSealedClassStart

        Examples
        --------
        >>> JavaParser(LexicalFSM("non-sealed class")).is_non_sealed_class_start(False)
        True
        >>> JavaParser(LexicalFSM("non-sealed function")).is_non_sealed_class_start(False)
        False
        """
        return (self.is_non_sealed_identifier(self.token, 0)
                and self.allowed_after_sealed_or_non_sealed(self.lexer.token(3), local, True))

    def is_non_sealed_identifier(self, some_token: Token, lookahead: int):
        """判断当前位置的标识符是否为 non-sealed 关键字

        [JDK Code] JavacParser.isNonSealedIdentifier
        """
        if some_token.name == "non" and self.peek_token(lookahead, TokenKind.SUB, TokenKind.IDENTIFIER):
            token_sub: Token = self.lexer.token(lookahead + 1)
            token_sealed: Token = self.lexer.token(lookahead + 2)
            return (some_token.end_pos == token_sub.pos
                    and token_sub.end_pos == token_sealed.pos
                    and token_sealed.name == "sealed")
        return False

    def is_sealed_class_start(self, local: bool):
        """如果当前 Token 为 sealed 关键字则返回 True，否则返回 False

        [JDK Code] JavacParser.isSealedClassStart

        Examples
        --------
        >>> JavaParser(LexicalFSM("sealed class")).is_sealed_class_start(False)
        True
        >>> JavaParser(LexicalFSM("sealed function")).is_sealed_class_start(False)
        False
        """
        return (self.token.name == "sealed"
                and self.allowed_after_sealed_or_non_sealed(self.lexer.token(1), local, False))

    def allowed_after_sealed_or_non_sealed(self, next_token: Token, local: bool, current_is_non_sealed: bool):
        """检查 next_token 是否为 sealed 关键字或 non-sealed 关键字之后的 Token 是否合法

        [JDK Code] JavacParser.allowedAfterSealedOrNonSealed
        """
        tk = next_token.kind
        if tk == TokenKind.MONKEYS_AT:
            return self.lexer.token(2).kind != TokenKind.INTERFACE or current_is_non_sealed
        if local is True:
            return tk in {TokenKind.ABSTRACT, TokenKind.FINAL, TokenKind.STRICTFP, TokenKind.CLASS, TokenKind.INTERFACE,
                          TokenKind.ENUM}
        elif tk in {TokenKind.PUBLIC, TokenKind.PROTECTED, TokenKind.PRIVATE, TokenKind.ABSTRACT, TokenKind.STATIC,
                    TokenKind.FINAL, TokenKind.STRICTFP, TokenKind.CLASS, TokenKind.INTERFACE, TokenKind.ENUM}:
            return True
        elif tk == TokenKind.IDENTIFIER:
            return (self.is_non_sealed_identifier(next_token, 3 if current_is_non_sealed else 1)
                    or next_token.name == "sealed")
        return False

    def opt_final(self, flags: List[Modifier]):
        """可选的 final 关键字

        [JDK Code] JavacParser.optFinal
        """
        modifiers = self.modifiers_opt()
        if len({flag for flag in modifiers.flags if flag not in {Modifier.FINAL, Modifier.DEPRECATED}}) > 0:
            self.syntax_error(self.token.pos, f"存在不是 FINAL 的修饰符: {flags}")
        modifiers.flags.extend(flags)
        return modifiers


if __name__ == "__main__":
    #         样例 1: List<String>
    #         样例 2: List<?>
    #         样例 3: List<? extends Number>
    #         样例 4: List<? super Integer>
    #         样例 5: List<@NonNull String>
    #         样例 6: List<? extends Number & Comparable<?>>

    print(JavaParser(LexicalFSM("++a")).term_3().kind.name)
    print(JavaParser(LexicalFSM("(int)")).term_3().kind.name)

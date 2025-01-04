"""
语法解析器
"""

from typing import Any, Dict, List, Optional

from metasequoia_java import ast
from metasequoia_java.ast import ReferenceMode
from metasequoia_java.ast import TreeKind
from metasequoia_java.ast.constants import INT_LITERAL_STYLE_HASH
from metasequoia_java.ast.constants import LONG_LITERAL_STYLE_HASH
from metasequoia_java.ast.element import Modifier
from metasequoia_java.grammar import grammar_enum
from metasequoia_java.grammar import grammar_hash
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

    TODO 待整理各个场景下使用的集合
    """

    # 中缀操作符的优先级级别的数量
    INFIX_PRECEDENCE_LEVELS = 10

    def __init__(self, lexer: LexicalFSM, mode: Mode = Mode.NULL):
        self.text = lexer.text
        self.lexer = lexer
        self.last_token: Optional[Token] = None  # 上一个 Token
        self.token: Optional[Token] = self.lexer.token(0)  # 当前 Token

        self.mode: Mode = mode  # 当前解析模式
        self.last_mode: Mode = Mode.NULL  # 上一个解析模式

        # 如果 permit_type_annotations_push_back 为假，那么当解析器遇到额外的注解时会直接抛出错误；否则会将额外的注解存入 type_annotations_push_back 变量中
        self.permit_type_annotations_push_back: bool = False
        self.type_annotations_pushed_back: List[ast.AnnotationTree] = []

        # 如果 allow_this_ident 为真，则允许将 "this" 视作标识符
        self.allow_this_ident: Optional[bool] = None

        # 方法接收的第一个 this 参数类型
        self.receiver_param: Optional[ast.VariableTree] = None

        # 当前源码层级中是否允许出现 yield 语句
        self.allow_yield_statement: bool = False

        # 为节省每次二元操作时分配新的操作数 / 操作符栈的开销，所以采用供应机制
        self.od_stack_supply: List[List[Optional[ast.ExpressionTree]]] = []
        self.op_stack_supply: List[List[Optional[Token]]] = []

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

    def raise_syntax_error(self, pos: int, message: str):
        """报告语法错误"""
        raise JavaSyntaxError(f"报告语法错误: pos={pos}, message={message}")

    def illegal(self, pos: Optional[int] = None):
        """报告表达式或类型的非法开始 Token"""
        if pos is None:
            pos = self.token.pos
        if self.is_mode(Mode.EXPR):
            self.raise_syntax_error(pos, "IllegalStartOfExpr")
        else:
            self.raise_syntax_error(pos, "IllegalStartOfType")

    # ------------------------------ 其他解析方法 ------------------------------

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

    # ------------------------------ 解析方法 ------------------------------

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
            self.raise_syntax_error(self.token.pos, f"AssertAsIdentifier")
        if self.token.kind == TokenKind.ENUM:
            self.raise_syntax_error(self.token.pos, f"EnumAsIdentifier")
        if self.token.kind == TokenKind.THIS:
            if self.allow_this_ident:
                name = self.token.name
                self.next_token()
                return name
            else:
                self.raise_syntax_error(self.token.pos, f"ThisAsIdentifier")
        if self.token.kind == TokenKind.UNDERSCORE:
            name = self.token.name
            self.next_token()
            return name
        self.accept(TokenKind.IDENTIFIER)
        raise JavaSyntaxError(f"{self.token.source} 不能作为 Identifier")

    def ident_or_underscore(self) -> str:
        """标识符或下划线

        [JDK Code] JavacParser.identOrUnderscore
        """
        return self.ident()

    def qualident(self, allow_annotations: bool):
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
            type_annotations = self.type_annotations_opt() if allow_annotations is True else None
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
        Literal =
            INTLITERAL
          | LONGLITERAL
          | FLOATLITERAL
          | DOUBLELITERAL
          | CHARLITERAL
          | STRINGLITERAL
          | TRUE
          | FALSE
          | NULL
        """
        pos = self.token.pos
        if self.token.kind in {TokenKind.INT_OCT_LITERAL, TokenKind.INT_DEC_LITERAL, TokenKind.INT_HEX_LITERAL}:
            literal = ast.IntLiteralTree.create(
                style=INT_LITERAL_STYLE_HASH[self.token.kind],
                value=self.token.int_value(),
                **self._info_include(pos)
            )
        elif self.token.kind in {TokenKind.LONG_OCT_LITERAL, TokenKind.LONG_DEC_LITERAL, TokenKind.LONG_HEX_LITERAL}:
            literal = ast.LongLiteralTree.create(
                style=LONG_LITERAL_STYLE_HASH[self.token.kind],
                value=self.token.int_value(),
                **self._info_include(pos)
            )
        elif self.token.kind == TokenKind.FLOAT_LITERAL:
            literal = ast.FloatLiteralTree.create(
                value=self.token.float_value(),
                **self._info_include(pos)
            )
        elif self.token.kind == TokenKind.DOUBLE_LITERAL:
            literal = ast.DoubleLiteralTree.create(
                value=self.token.float_value(),
                **self._info_include(pos)
            )
        elif self.token.kind == TokenKind.TRUE:
            literal = ast.TrueLiteralTree.create(
                **self._info_include(pos)
            )
        elif self.token.kind == TokenKind.FALSE:
            literal = ast.FalseLiteralTree.create(
                **self._info_include(pos)
            )
        elif self.token.kind == TokenKind.CHAR_LITERAL:
            literal = ast.CharacterLiteralTree.create(
                value=self.token.char_value(),
                **self._info_include(pos)
            )
        elif self.token.kind == TokenKind.STRING_LITERAL:
            literal = ast.StringLiteralTree.create_string(
                value=self.token.string_value(),
                **self._info_include(pos)
            )
        elif self.token.kind == TokenKind.TEXT_BLOCK:
            literal = ast.StringLiteralTree.create_text_block(
                value=self.token.string_value(),
                **self._info_include(pos)
            )
        elif self.token.kind == TokenKind.NULL:
            literal = ast.NullLiteralTree.create(
                **self._info_include(pos)
            )
        else:
            raise JavaSyntaxError(f"{self.token.source} 不是字面值")
        self.next_token()
        return literal

    def parse_expression(self) -> ast.ExpressionTree:
        """解析表达式（可以是表达式或类型）

        [JDK Code] JavacParser.parseExpression
        """
        return self.term(Mode.EXPR)

    def parse_pattern(self, pos: int, modifiers: Optional[ast.ModifiersTree],
                      parsed_type: Optional[ast.ExpressionTree],
                      allow_var: bool, check_guard: bool) -> ast.PatternTree:
        """解析模式

        [JDK Document] https://docs.oracle.com/javase/specs/jls/se22/html/jls-19.html
        Pattern:
          TypePattern
          RecordPattern

        TypePattern:
          LocalVariableDeclaration

        RecordPattern:
          ReferenceType ( [ComponentPatternList] )

        ComponentPatternList:
          ComponentPattern {, ComponentPattern }

        ComponentPattern:
          Pattern
          MatchAllPattern

        MatchAllPattern:
          _

        [JDK Code] JavacParser.parsePattern

        TODO 待补充单元测试（待 term 完成）

        Examples
        --------
        >>> JavaParser(LexicalFSM("_")).parse_pattern(0, ast.ModifiersTree.create_empty(), None, False, True).kind.name
        'ANY_PATTERN'
        """
        if modifiers is None:
            modifiers = self.opt_final([])

        if self.token.kind == TokenKind.UNDERSCORE and parsed_type is None:
            self.next_token()
            return ast.AnyPatternTree.create(**self._info_exclude(self.token.pos))

        if parsed_type is None:
            var = (self.token.kind == TokenKind.IDENTIFIER and self.token.name == "var")
            expression = self.unannotated_type(allow_var=allow_var, new_mode=Mode.TYPE | Mode.NO_LAMBDA)
            if var is True:
                expression = None
        else:
            expression = parsed_type

        # ReferenceType ( [ComponentPatternList] )
        if self.token.kind == TokenKind.LPAREN:
            nested: List[ast.PatternTree] = []
            if self.peek_token(0, TokenKind.RPAREN):
                self.next_token()
            else:
                while True:
                    self.next_token()
                    nested.append(self.parse_pattern(self.token.pos, None, None, True, False))
                    if self.token.kind != TokenKind.COMMA:
                        break
            self.accept(TokenKind.RPAREN)
            # TODO 待补充检查逻辑
            return ast.DeconstructionPatternTree.create(
                deconstructor=expression,
                nested_patterns=nested,
                **self._info_exclude(pos)
            )

        var_pos = self.token.pos
        name: str = self.ident_or_underscore()
        # TODO 待考虑补充特性逻辑
        variable = ast.VariableTree.create_by_name(
            modifiers=modifiers,
            name=name,
            variable_type=expression,
            **self._info_exclude(var_pos)
        )
        # TODO 补充检查日志逻辑
        return ast.BindingPatternTree.create(
            variable=variable,
            **self._info_exclude(pos)
        )

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
            是否允许 "var" 作为类型名称
        annotations : Optional[List[ast.AnnotationTree]], default = None
            已经解析的注解

        [JDK Code] JavacParser.parseType

        TODO 待补充单元测试（等待 term 完成）
        """
        if pos is None:
            pos = self.token.pos
        if annotations is None:
            annotations = self.type_annotations_opt()

        result = self.unannotated_type(allow_var=allow_var)

        if annotations:
            # TODO 待确定是否需要实现类似 insertAnnotationsToMostInner 的逻辑
            return ast.AnnotatedTypeTree.create(
                annotations=annotations,
                underlying_type=result,
                **self._info_include(pos)
            )
        return result

    def parse_intersection_type(self, pos: int, first_type: ast.ExpressionTree):
        """解析 CAST 语句中的交叉类型

        [JDK Document] https://docs.oracle.com/javase/specs/jls/se22/html/jls-19.html
        AdditionalBound:
          & InterfaceType

        [JDK Code] JavacParser.parseIntersectionType

        Examples
        --------
        >>> JavaParser(LexicalFSM(" & type2")).parse_intersection_type(0, ast.ExpressionTree.mock()).kind.name
        'INTERSECTION_TYPE'
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

    def unannotated_type(self, allow_var: bool = False, new_mode: Mode = Mode.TYPE) -> ast.ExpressionTree:
        """解析不包含注解的类型

        [JDK Code] JavacParser.unannotatedType

        TODO 待补充单元测试（待 term 完成）
        """
        result = self.term(new_mode)
        restricted_type_name = self.restricted_type_name(result)
        if restricted_type_name is not None and (not allow_var or restricted_type_name != "var"):
            self.raise_syntax_error(result.start_pos, f"RestrictedTypeNotAllowedHere, but get {result.kind.name}")
        return result

    def term(self, new_mode: Optional[Mode] = None) -> ast.ExpressionTree:
        """解析第 0 层级语法元素

        [JDK Document] https://docs.oracle.com/javase/specs/jls/se22/html/jls-19.html
        AssignmentExpression:
          ConditionalExpression
          Assignment

        Assignment:
          LeftHandSide AssignmentOperator Expression

        LeftHandSide:
          ExpressionName
          FieldAccess
          ArrayAccess

        AssignmentOperator:
          (one of)
          =  *=  /=  %=  +=  -=  <<=  >>=  >>>=  &=  ^=  |=

        [JDK Code] JavacParser.term(int newmode)
        [JDK Code] JavacParser.term()
        Expression = Expression1 [ExpressionRest]
        ExpressionRest = [AssignmentOperator Expression1]
        AssignmentOperator = "=" | "+=" | "-=" | "*=" | "/=" |
                             "&=" | "|=" | "^=" |
                             "%=" | "<<=" | ">>=" | ">>>="
        Type = Type1
        TypeNoParams = TypeNoParams1
        StatementExpression = Expression
        ConstantExpression = Expression

        Examples
        --------
        >>> JavaParser(LexicalFSM("name2 = name1 > 3 ? 2 : 1"), mode=Mode.EXPR).term().kind.name
        'ASSIGNMENT'
        >>> JavaParser(LexicalFSM("name2 += name1 > 3 ? 2 : 1"), mode=Mode.EXPR).term().kind.name
        'PLUS_ASSIGNMENT'
        """
        prev_mode = None
        if new_mode is not None:
            prev_mode = self.mode
            self.set_mode(new_mode)

        expression = self.term1()
        if (self.is_mode(Mode.EXPR)
                and self.token.kind in {TokenKind.EQ, TokenKind.PLUS_EQ, TokenKind.SUB_EQ, TokenKind.STAR_EQ,
                                        TokenKind.SLASH_EQ, TokenKind.AMP_EQ, TokenKind.BAR_EQ, TokenKind.CARET_EQ,
                                        TokenKind.PERCENT_EQ, TokenKind.LT_LT_EQ, TokenKind.GT_GT_EQ,
                                        TokenKind.GT_GT_GT_EQ}):
            expression = self.term_rest(expression)

        if new_mode is not None:
            self.set_last_mode(self.mode)
            self.set_mode(prev_mode)

        return expression

    def term_rest(self, expression: ast.ExpressionTree) -> ast.ExpressionTree:
        """解析第 0 层级语法元素的剩余部分

        [JDK Code] JavacParser.termRest(JCExpression)
        """
        if self.token.kind == TokenKind.EQ:
            pos = self.token.pos
            self.next_token()
            self.select_expr_mode()
            expression_1 = self.term()
            return ast.AssignmentTree.create(
                variable=expression,
                expression=expression_1,
                **self._info_exclude(pos)
            )
        elif self.token.kind in {TokenKind.PLUS_EQ, TokenKind.SUB_EQ, TokenKind.STAR_EQ, TokenKind.SLASH_EQ,
                                 TokenKind.AMP_EQ, TokenKind.BAR_EQ, TokenKind.CARET_EQ, TokenKind.PERCENT_EQ,
                                 TokenKind.LT_LT_EQ, TokenKind.GT_GT_EQ, TokenKind.GT_GT_GT_EQ}:
            pos = self.token.pos
            tk = self.token.kind
            self.next_token()
            self.select_expr_mode()
            expression_1 = self.term()
            return ast.CompoundAssignmentTree.create(
                kind=grammar_hash.ASSIGN_OPERATOR_TO_TREE_KIND[tk],
                variable=expression,
                expression=expression_1,
                **self._info_exclude(pos)
            )
        else:
            return expression

    def term1(self) -> ast.ExpressionTree:
        """解析第 1 层级语法元素

        [JDK Document] https://docs.oracle.com/javase/specs/jls/se22/html/jls-19.html
        ConditionalExpression:
          ConditionalOrExpression
          ConditionalOrExpression ? Expression : ConditionalExpression
          ConditionalOrExpression ? Expression : LambdaExpression

        [JDK Code] JavacParser.term1
        Expression1   = Expression2 [Expression1Rest]
        Type1         = Type2
        TypeNoParams1 = TypeNoParams2

        Examples
        --------
        >>> JavaParser(LexicalFSM("name > 3 ? 2 : 1"), mode=Mode.EXPR).term1().kind.name
        'CONDITIONAL_EXPRESSION'
        """
        expression = self.term2()
        if self.is_mode(Mode.EXPR) and self.token.kind == TokenKind.QUES:
            self.select_expr_mode()
            return self.term1_rest(expression)
        else:
            return expression

    def term1_rest(self, expression: ast.ExpressionTree) -> ast.ExpressionTree:
        """解析第 1 层级语法元素的剩余部分

        [JDK Code] JavacParser.term1Rest
        Expression1Rest = ["?" Expression ":" Expression1]
        """
        if self.token.kind == TokenKind.QUES:
            pos = self.token.pos
            self.next_token()
            expression_1 = self.term()
            self.accept(TokenKind.COLON)
            expression_2 = self.term1()
            return ast.ConditionalExpressionTree.create(
                condition=expression,
                true_expression=expression_1,
                false_expression=expression_2,
                **self._info_exclude(pos)
            )
        else:
            return expression

    def term2(self):
        """解析第 2 层级语法元素

        处理如下层级的表达式：
        OR_PREC = 4  # "||"
        AND_PREC = 5  # "&&"
        BIT_OR_PREC = 6  # "|"
        BIT_XOR_PREC = 7  # "^"
        BIT_AND_PREC = 8  # "&"
        EQ_PREC = 9  # "==" | "!="
        ORD_PREC = 10  # "<" | ">" | "<=" | ">="
        SHIFT_PREC = 11  # "<<" | ">>" | ">>>"
        ADD_PREC = 12  # "+" | "-"
        MUL_PREC = 13  # "*" | "/" | "%"

        [JDK Document] https://docs.oracle.com/javase/specs/jls/se22/html/jls-19.html
        ConditionalOrExpression:
          ConditionalAndExpression
          ConditionalOrExpression || ConditionalAndExpression

        ConditionalAndExpression:
          InclusiveOrExpression
          ConditionalAndExpression && InclusiveOrExpression

        InclusiveOrExpression:
          ExclusiveOrExpression
          InclusiveOrExpression | ExclusiveOrExpression

        ExclusiveOrExpression:
          AndExpression
          ExclusiveOrExpression ^ AndExpression

        AndExpression:
          EqualityExpression
          AndExpression & EqualityExpression

        EqualityExpression:
          RelationalExpression
          EqualityExpression == RelationalExpression
          EqualityExpression != RelationalExpression

        RelationalExpression:
          ShiftExpression
          RelationalExpression < ShiftExpression
          RelationalExpression > ShiftExpression
          RelationalExpression <= ShiftExpression
          RelationalExpression >= ShiftExpression
          InstanceofExpression

        InstanceofExpression:
          RelationalExpression instanceof ReferenceType
          RelationalExpression instanceof Pattern

        ShiftExpression:
          AdditiveExpression
          ShiftExpression << AdditiveExpression
          ShiftExpression >> AdditiveExpression
          ShiftExpression >>> AdditiveExpression

        AdditiveExpression:
          MultiplicativeExpression
          AdditiveExpression + MultiplicativeExpression
          AdditiveExpression - MultiplicativeExpression

        MultiplicativeExpression:
          UnaryExpression
          MultiplicativeExpression * UnaryExpression
          MultiplicativeExpression / UnaryExpression
          MultiplicativeExpression % UnaryExpression

        [JDK Code] JavacParser.term2()
        Expression2   = Expression3 [Expression2Rest]
        Type2         = Type3
        TypeNoParams2 = TypeNoParams3

        Examples
        --------
        >>> JavaParser(LexicalFSM("1 + 2"), mode=Mode.EXPR).term2().kind.name
        'PLUS'
        >>> JavaParser(LexicalFSM("1 * 2"), mode=Mode.EXPR).term2().kind.name
        'MULTIPLY'
        >>> JavaParser(LexicalFSM("1 + 2 * 3"), mode=Mode.EXPR).term2().kind.name
        'PLUS'
        >>> JavaParser(LexicalFSM("(1 + 2) * 3"), mode=Mode.EXPR).term2().kind.name
        'MULTIPLY'
        """
        expression = self.term3()
        if self.is_mode(Mode.EXPR) and self.prec(self.token.kind) >= grammar_enum.OperatorPrecedence.OR_PREC:
            self.select_expr_mode()
            return self.term2_rest(expression, grammar_enum.OperatorPrecedence.OR_PREC)
        return expression

    def term2_rest(self, expression: ast.ExpressionTree,
                   min_prec: grammar_enum.OperatorPrecedence) -> ast.ExpressionTree:
        """解析第 2 层级语法元素的剩余部分

        [JDK Code] JavacParser.term2Rest(JCExpression, int)
        Expression2Rest = {infixop Expression3}
                        | Expression3 instanceof Type
                        | Expression3 instanceof Pattern
        infixop         = "||"
                        | "&&"
                        | "|"
                        | "^"
                        | "&"
                        | "==" | "!="
                        | "<" | ">" | "<=" | ">="
                        | "<<" | ">>" | ">>>"
                        | "+" | "-"
                        | "*" | "/" | "%"
        """
        od_stack: List[ast.ExpressionTree] = self.new_od_stack()
        op_stack: List[Token] = self.new_op_stack()

        top = 0
        od_stack[0] = expression
        top_op = Token.dummy()
        while self.prec(self.token.kind) >= min_prec:
            op_stack[top] = top_op

            # instanceof
            if self.token.kind == TokenKind.INSTANCEOF:
                pos = self.token.pos
                self.next_token()

                if self.token.kind == TokenKind.LPAREN:
                    pattern = self.parse_pattern(self.token.pos, None, None, False, False)
                else:
                    pattern_pos = self.token.pos
                    modifiers = self.opt_final([])
                    instance_type = self.unannotated_type(allow_var=False)
                    if self.token.kind == TokenKind.IDENTIFIER:
                        # TODO 待增加验证逻辑
                        pattern = self.parse_pattern(pattern_pos, modifiers, instance_type, False, False)
                    elif self.token.kind == TokenKind.LPAREN:
                        pattern = self.parse_pattern(pattern_pos, modifiers, instance_type, False, False)
                        # TODO 待增加验证逻辑
                    elif self.token.kind == TokenKind.UNDERSCORE:
                        pattern = self.parse_pattern(pattern_pos, modifiers, instance_type, False, False)
                    else:
                        if modifiers.annotations:
                            type_annotations: List[ast.AnnotationTree] = []
                            for decl in modifiers.annotations:
                                type_annotations.append(ast.AnnotationTree.create(
                                    annotation_type=decl.annotation_type,
                                    arguments=decl.arguments,
                                    start_pos=decl.start_pos,
                                    end_pos=decl.end_pos,
                                    source=decl.source,
                                ))
                            # TODO 考虑是否需要增加 insertAnnotationsToMostInner 的逻辑
                            instance_type = ast.AnnotatedTypeTree.create(
                                annotations=type_annotations,
                                underlying_type=instance_type,
                                **self._info_include(None)
                            )
                        pattern = instance_type

                od_stack[top] = ast.InstanceOfTree.create(
                    expression=od_stack[top],
                    pattern=pattern,
                    **self._info_exclude(pos)
                )

            else:
                top_op = self.token
                self.next_token()  # 跳过运算符
                top += 1
                od_stack[top] = self.term3()

            while top > 0 and self.prec(top_op.kind) >= self.prec(self.token.kind):  # 上一个运算符的优先级大于等于下一个运算符的优先级
                od_stack[top - 1] = ast.BinaryTree.create(
                    kind=grammar_hash.BINARY_OPERATOR_TO_TREE_KIND[top_op.kind],
                    left_operand=od_stack[top - 1],
                    right_operand=od_stack[top],
                    **self._info_exclude(od_stack[top - 1].start_pos)
                )
                top -= 1
                top_op = op_stack[top]

        assert top == 0
        expression = od_stack[0]

        # TODO 待补充合并字符串的逻辑

        self.od_stack_supply.append(od_stack)
        self.op_stack_supply.append(op_stack)

        return expression

    def new_od_stack(self) -> List[Optional[ast.ExpressionTree]]:
        """构造操作数的数组

        TODO 待设计适用于 Python 的优化方法
        """
        if not self.od_stack_supply:
            return [None] * (self.INFIX_PRECEDENCE_LEVELS + 1)
        return self.od_stack_supply.pop()

    def new_op_stack(self) -> List[Optional[Token]]:
        """构造操作符的数组

        TODO 待设计适用于 Python 的优化方法
        """
        if not self.op_stack_supply:
            return [None] * (self.INFIX_PRECEDENCE_LEVELS + 1)
        return self.op_stack_supply.pop()

    def term3(self) -> ast.ExpressionTree:
        """解析第 3 层级语法元素

        [JDK Document] https://docs.oracle.com/javase/specs/jls/se22/html/jls-19.html（不包含在代码中已单独注释了 [JDK Document] 的语义组）
        Primary:
          PrimaryNoNewArray
          ArrayCreationExpression

        PrimaryNoNewArray:
          Literal
          ClassLiteral
          this
          TypeName . this
          ( Expression )
          ClassInstanceCreationExpression
          FieldAccess
          ArrayAccess
          MethodInvocation
          MethodReference

        ClassLiteral:
          TypeName {[ ]} . class
          NumericType {[ ]} . class
          boolean {[ ]} . class
          void . class

        ArrayAccess:
          ExpressionName [ Expression ]
          PrimaryNoNewArray [ Expression ]
          ArrayCreationExpressionWithInitializer [ Expression ]

        FieldAccess:
          Primary . Identifier
          super . Identifier
          TypeName . super . Identifier

        MethodInvocation:
          MethodName ( [ArgumentList] )
          TypeName . [TypeArguments] Identifier ( [ArgumentList] )
          ExpressionName . [TypeArguments] Identifier ( [ArgumentList] )
          Primary . [TypeArguments] Identifier ( [ArgumentList] )
          super . [TypeArguments] Identifier ( [ArgumentList] )
          TypeName . super . [TypeArguments] Identifier ( [ArgumentList] )

        MethodReference:
          ExpressionName :: [TypeArguments] Identifier
          Primary :: [TypeArguments] Identifier
          ReferenceType :: [TypeArguments] Identifier
          super :: [TypeArguments] Identifier
          TypeName . super :: [TypeArguments] Identifier
          ClassType :: [TypeArguments] new
          ArrayType :: new

        UnaryExpressionNotPlusMinus:
          PostfixExpression
          ~ UnaryExpression
          ! UnaryExpression
          CastExpression
          SwitchExpression

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
        TODO 待补充单元测试：括号表达式
        TODO 待补充单元测试：this
        TODO 待补充单元测试：MONKEY_AT
        TODO 待补充单元测试：switch 语句

        Examples
        --------
        >>> JavaParser(LexicalFSM("++a")).term3().kind.name
        'PREFIX_INCREMENT'
        >>> JavaParser(LexicalFSM("(int) a")).term3().kind.name
        'TYPE_CAST'
        >>> JavaParser(LexicalFSM("(x, y)->{ return x + y; }")).term3().kind.name
        'LAMBDA_EXPRESSION'
        >>> parser = JavaParser(LexicalFSM("super::name"))
        >>> parser.select_expr_mode()
        >>> parser.term3().kind.name
        'MEMBER_REFERENCE'
        >>> parser = JavaParser(LexicalFSM("super::name1.name2"))
        >>> parser.select_expr_mode()
        >>> parser.term3().kind.name
        'MEMBER_REFERENCE'
        >>> parser = JavaParser(LexicalFSM("super::name1.(arg1)name2"))
        >>> parser.select_expr_mode()
        >>> parser.term3().kind.name
        'MEMBER_REFERENCE'
        >>> parser = JavaParser(LexicalFSM("super::name1.(arg1)name2(arg2)"))
        >>> parser.select_expr_mode()
        >>> parser.term3().kind.name
        'MEMBER_REFERENCE'
        >>> parser = JavaParser(LexicalFSM("new int[]{1, 2, 3}"))
        >>> parser.select_expr_mode()
        >>> parser.term3().kind.name
        'NEW_ARRAY'
        >>> JavaParser(LexicalFSM("new ClassName (name1, name2) {}"), mode=Mode.EXPR).term3().kind.name
        'NEW_CLASS'
        >>> JavaParser(LexicalFSM("ExprName.new ClassName (name1, name2) {}"), mode=Mode.EXPR).term3().kind.name
        'NEW_CLASS'
        >>> res = JavaParser(LexicalFSM("boolean[].class"), mode=Mode.EXPR).term3()
        >>> res.kind.name
        'MEMBER_SELECT'
        >>> res.expression.kind.name if isinstance(res, ast.MemberSelectTree) else None
        'ARRAY_TYPE'
        >>> res = JavaParser(LexicalFSM("boolean.class"), mode=Mode.EXPR).term3()
        >>> res.kind.name
        'MEMBER_SELECT'
        >>> res.expression.kind.name if isinstance(res, ast.MemberSelectTree) else None
        'PRIMITIVE_TYPE'
        >>> res = JavaParser(LexicalFSM("void.class"), mode=Mode.EXPR).term3()
        >>> res.kind.name
        'MEMBER_SELECT'
        >>> res.expression.kind.name if isinstance(res, ast.MemberSelectTree) else None
        'PRIMITIVE_TYPE'
        """
        pos = self.token.pos
        type_args = self.type_argument_list_opt()

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
                self.raise_syntax_error(pos, "Illegal")  # TODO 待增加说明信息
            tk = self.token.kind
            self.next_token()
            self.select_expr_mode()
            if tk == TokenKind.SUB and self.token.kind in {TokenKind.INT_DEC_LITERAL, TokenKind.LONG_DEC_LITERAL}:
                self.select_expr_mode()
                return self.term3_rest(self.literal(), type_args)

            expression = self.term3()
            return ast.UnaryTree.create(
                kind=grammar_hash.UNARY_OPERATOR_TO_TREE_KIND[tk],
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
                expression = self.term3()
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
                expression = self.term_rest(self.term1_rest(self.term2_rest(self.term3(),
                                                                            grammar_enum.OperatorPrecedence.OR_PREC)))
                self.accept(TokenKind.RPAREN)
                expression = ast.ParenthesizedTree.create(
                    expression=expression,
                    **self._info_exclude(pos)
                )
            return self.term3_rest(expression, type_args)

        # PrimaryNoNewArray:
        #   this
        if self.token.kind == TokenKind.THIS:
            if not self.is_mode(Mode.EXPR):
                self.raise_syntax_error(self.token.pos, "illegal")
            self.select_expr_mode()
            expression = ast.IdentifierTree.create(
                name="this",
                **self._info_include(pos)
            )
            self.next_token()
            if type_args is None:
                expression = self.arguments_opt(None, expression)
            else:
                expression = self.arguments(type_args, expression)
            return self.term3_rest(expression, None)

        # MethodReference:
        #   super :: [TypeArguments] Identifier
        if self.token.kind == TokenKind.SUPER:
            if not self.is_mode(Mode.EXPR):
                self.raise_syntax_error(self.token.pos, "illegal")
            self.select_expr_mode()
            expression = ast.IdentifierTree.create(
                name="super",
                **self._info_include(pos)
            )
            expression = self.super_suffix(type_args, expression)
            return self.term3_rest(expression, None)

        # PrimaryNoNewArray:
        #   Literal
        if self.token.kind in {TokenKind.INT_OCT_LITERAL, TokenKind.INT_DEC_LITERAL, TokenKind.INT_HEX_LITERAL,
                               TokenKind.LONG_OCT_LITERAL, TokenKind.LONG_DEC_LITERAL, TokenKind.LONG_HEX_LITERAL,
                               TokenKind.FLOAT_LITERAL, TokenKind.DOUBLE_LITERAL, TokenKind.CHAR_LITERAL,
                               TokenKind.STRING_LITERAL, TokenKind.TRUE, TokenKind.FALSE, TokenKind.NULL}:
            if type_args is not None or not self.is_mode(Mode.EXPR):
                self.illegal(self.token.pos)
            expression = self.literal()
            return self.term3_rest(expression, None)

        if self.token.kind == TokenKind.NEW:
            # [JDK Document] https://docs.oracle.com/javase/specs/jls/se22/html/jls-19.html
            # UnqualifiedClassInstanceCreationExpression:
            #   new [TypeArguments] ClassOrInterfaceTypeToInstantiate ( [ArgumentList] ) [ClassBody]
            #
            # ArrayCreationExpression:
            #   ArrayCreationExpressionWithoutInitializer
            #   ArrayCreationExpressionWithInitializer
            #
            # ArrayCreationExpressionWithoutInitializer:
            #   new PrimitiveType DimExprs [Dims]
            #   new ClassOrInterfaceType DimExprs [Dims]
            #
            # ArrayCreationExpressionWithInitializer:
            #   new PrimitiveType Dims ArrayInitializer
            #   new ClassOrInterfaceType Dims ArrayInitializer
            if type_args is not None or not self.is_mode(Mode.EXPR):
                self.illegal(self.token.pos)
            self.select_expr_mode()
            self.next_token()
            if self.token.kind == TokenKind.LT:
                type_args = self.type_argument_list(False)
            expression = self.creator(pos, type_args)
            return self.term3_rest(expression, None)

        # 可能是有注解的强制类型转换（annotated cast types），或方法引用（method references）
        if self.token.kind == TokenKind.MONKEYS_AT:
            type_annotations = self.type_annotations_opt()
            if not type_annotations:
                self.raise_syntax_error(self.token.pos, "expected type annotations, but found none!")

            expression = self.term3()
            if not self.is_mode(Mode.TYPE):
                if expression.kind == TreeKind.MEMBER_REFERENCE:
                    assert isinstance(expression, ast.MemberReferenceTree)
                    expression.expression = ast.AnnotatedTypeTree.create(
                        annotations=type_annotations,
                        underlying_type=expression.expression,
                        **self._info_exclude(self.token.pos)
                    )
                    return self.term3_rest(expression, type_args)
                elif expression.kind == TreeKind.MEMBER_SELECT:
                    # TODO 待增加日志中的失败信息：NoAnnotationsOnDotClass
                    return expression
                else:
                    self.illegal(type_annotations[0].start_pos)
            else:
                # TODO 考虑是否需要增加 insertAnnotationsToMostInner 的逻辑
                expression = ast.AnnotatedTypeTree.create(
                    annotations=type_annotations,
                    underlying_type=expression,
                    **self._info_include(None)
                )
                return self.term3_rest(expression, type_args)

        if self.token.kind in {TokenKind.UNDERSCORE, TokenKind.IDENTIFIER, TokenKind.ASSERT, TokenKind.ENUM}:
            if type_args is not None:
                self.illegal()

            # 没有括号的、且只有 1 个参数的 lambda 表达式
            if self.is_mode(Mode.EXPR) and not self.is_mode(Mode.NO_LAMBDA) and self.peek_token(0, TokenKind.ARROW):
                expression = self.lambda_expression_or_statement(has_parens=False, explicit_params=False, pos=pos)
                expression = self.type_arguments_opt(expression)
                return self.term3_rest(expression, None)

            # 将当前元素当作标识符处理
            expression = ast.IdentifierTree.create(
                name=self.ident(),
                **self._info_exclude(pos)
            )
            while True:
                pos = self.token.pos
                annotations = self.type_annotations_opt()
                if annotations and self.token.kind not in {TokenKind.LBRACKET, TokenKind.ELLIPSIS}:
                    self.illegal(annotations[0].start_pos)

                if self.token.kind == TokenKind.LBRACKET:
                    self.next_token()
                    if self.token.kind == TokenKind.RBRACKET:
                        # TypeName [ ] . class
                        self.next_token()
                        expression = self.brackets_opt(expression)
                        expression = ast.ArrayTypeTree.create(
                            expression=expression,
                            **self._info_exclude(pos)
                        )
                        if annotations:
                            expression = ast.AnnotatedTypeTree.create(
                                annotations=annotations,
                                underlying_type=expression,
                                **self._info_exclude(pos)
                            )
                        expression = self.brackets_suffix(expression)
                    else:
                        # ExpressionName [ Expression ]
                        if self.is_mode(Mode.EXPR):
                            self.select_expr_mode()
                            index = self.term()
                            if annotations:
                                self.illegal()
                            expression = ast.ArrayAccessTree.create(
                                expression=expression,
                                index=index,
                                **self._info_exclude(pos)
                            )
                        self.accept(TokenKind.RBRACKET)
                    break

                # MethodName ( [ArgumentList] )
                if self.token.kind == TokenKind.LPAREN:
                    if self.is_mode(Mode.EXPR):
                        self.select_expr_mode()
                        expression = self.arguments(type_args, expression)
                        if annotations:
                            self.illegal(annotations[0].start_pos)
                        type_args = None
                    break

                if self.token.kind == TokenKind.DOT:
                    self.next_token()
                    if self.token.kind == TokenKind.IDENTIFIER and type_args:
                        self.illegal()

                    prev_mode = self.mode
                    self.set_mode(self.mode & ~Mode.NO_PARAMS)
                    type_args = self.type_argument_list_opt(Mode.EXPR)
                    self.set_mode(prev_mode)

                    if self.is_mode(Mode.EXPR):
                        # TypeName . class
                        # NumericType . class
                        # boolean . class
                        # void . class
                        if self.token.kind == TokenKind.CLASS:
                            if type_args:
                                self.illegal()
                            self.select_expr_mode()
                            expression = ast.MemberSelectTree.create(
                                expression=expression,
                                identifier=ast.IdentifierTree.create(name="class",
                                                                     **self._info_exclude(self.token.pos)),
                                **self._info_include(pos)
                            )
                            self.next_token()
                            break

                        # TypeName . this
                        if self.token.kind == TokenKind.THIS:
                            if type_args:
                                self.illegal()
                            self.select_expr_mode()
                            expression = ast.MemberSelectTree.create(
                                expression=expression,
                                identifier=ast.IdentifierTree.create(name="this",
                                                                     **self._info_exclude(self.token.pos)),
                                **self._info_include(pos)
                            )
                            self.next_token()
                            break

                        # TypeName . super :: [TypeArguments] Identifier
                        if self.token.kind == TokenKind.SUPER:
                            self.select_expr_mode()
                            expression = ast.MemberSelectTree.create(
                                expression=expression,
                                identifier=ast.IdentifierTree.create(name="super",
                                                                     **self._info_exclude(self.token.pos)),
                                **self._info_include(pos)
                            )
                            expression = self.super_suffix(type_args, expression)
                            break

                        # [JDK Document] https://docs.oracle.com/javase/specs/jls/se22/html/jls-19.html
                        # ClassInstanceCreationExpression:
                        #   UnqualifiedClassInstanceCreationExpression
                        #   ExpressionName . UnqualifiedClassInstanceCreationExpression
                        #   Primary . UnqualifiedClassInstanceCreationExpression
                        if self.token.kind == TokenKind.NEW:
                            self.select_expr_mode()
                            pos1 = self.token.pos
                            self.next_token()
                            if self.token.kind == TokenKind.LT:
                                type_args = self.type_argument_list(False)
                            expression = self.inner_creator(pos1, type_args, expression)
                            break

                    # 继续第二轮循环
                    type_annotations: Optional[List[ast.AnnotationTree]] = None
                    if self.is_mode(Mode.TYPE) and self.token.kind == TokenKind.MONKEYS_AT:
                        type_annotations = self.type_annotations_opt()

                    expression = ast.MemberSelectTree.create(
                        expression=expression,
                        identifier=ast.IdentifierTree.create(name=self.ident(), **self._info_exclude(self.token.pos)),
                        **self._info_include(pos)
                    )
                    # TODO 待增加失败恢复的机制
                    if type_annotations:
                        expression = ast.AnnotatedTypeTree.create(
                            annotations=type_annotations,
                            underlying_type=expression,
                            **self._info_exclude(type_annotations[0].start_pos)
                        )
                    continue

                if self.token.kind == TokenKind.ELLIPSIS:
                    if self.permit_type_annotations_push_back is False:
                        self.illegal()
                    self.type_annotations_pushed_back = annotations
                    break

                # Primary :: [TypeArguments] Identifier【前缀部分】
                if self.token.kind == TokenKind.LT:
                    if not self.is_mode(Mode.EXPR) and self.is_unbound_member_ref():
                        pos_1 = self.token.pos
                        self.accept(TokenKind.LT)
                        type_arguments = [self.type_argument()]
                        while self.token.kind == TokenKind.COMMA:
                            self.next_token()
                            type_arguments.append(self.type_argument())
                        self.accept(TokenKind.GT)

                        expression = ast.ParameterizedTypeTree.create(
                            type_name=expression,
                            type_arguments=type_arguments,
                            **self._info_exclude(pos_1)
                        )

                        while self.token.kind == TokenKind.DOT:
                            self.next_token()
                            self.select_type_mode()
                            expression = ast.MemberSelectTree.create(
                                expression=expression,
                                identifier=ast.IdentifierTree.create(name=self.ident(),
                                                                     **self._info_include(self.token.pos)),
                                **self._info_include(self.token.pos)
                            )
                            expression = self.type_arguments_opt(expression)

                        expression = self.brackets_opt(expression)

                        if self.token.kind != TokenKind.COL_COL:
                            self.illegal()

                        self.select_expr_mode()
                    break

                break
            if type_args is not None:
                self.illegal()
            expression = self.type_arguments_opt(expression)
            return self.term3_rest(expression, None)

        # NumericType {[ ]} . class
        # boolean {[ ]} . class
        if self.token.kind in {TokenKind.BYTE, TokenKind.SHORT, TokenKind.CHAR, TokenKind.INT, TokenKind.LONG,
                               TokenKind.FLOAT, TokenKind.DOUBLE, TokenKind.BOOLEAN}:
            if type_args is not None:
                self.illegal()
            expression = self.brackets_suffix(self.brackets_opt(self.basic_type()))
            return self.term3_rest(expression, None)

        # void . class
        if self.token.kind == TokenKind.VOID:
            if type_args is not None:
                self.illegal()
            if self.is_mode(Mode.EXPR):
                self.next_token()
                if self.token.kind != TokenKind.DOT:
                    self.illegal(pos)
                expression = ast.PrimitiveTypeTree.create_void(**self._info_include(pos))
                expression = self.brackets_suffix(expression)
                return self.term3_rest(expression, None)
            else:
                # 通过向下一个阶段传递一个 void 类型来支持 myMethodHandle.<void>invoke() 的特殊情况
                expression = ast.PrimitiveTypeTree.create_void(**self._info_include(pos))
                self.next_token()
                return expression

        # [JDK Document] https://docs.oracle.com/javase/specs/jls/se22/html/jls-19.html
        # SwitchExpression:
        #   switch ( Expression ) SwitchBlock
        if self.token.kind == TokenKind.SWITCH:
            self.allow_yield_statement = True
            switch_pos = self.token.pos
            self.next_token()
            expression = self.par_expression()
            self.accept(TokenKind.LBRACE)
            cases: List[ast.CaseTree] = []
            while True:
                pos = self.token.pos
                if self.token.kind in {TokenKind.CASE, TokenKind.DEFAULT}:
                    cases.extend(self.switch_expression_statement_group())
                elif self.token.kind in {TokenKind.RBRACE, TokenKind.EOF}:
                    switch_expression = ast.SwitchExpressionTree.create(
                        expression=expression,
                        cases=cases,
                        **self._info_exclude(switch_pos)
                    )
                    switch_expression.end_pos = self.token.pos  # TODO 待考虑 source 的逻辑
                    self.accept(TokenKind.RBRACE)
                    return switch_expression
                else:
                    self.raise_syntax_error(self.token.pos, f"expect CASE, DEFAULT or RBRACE, "
                                                            f"but get {self.token.kind.name}")

        self.illegal()

    def switch_expression_statement_group(self) -> List[ast.CaseTree]:
        """解析 Switch 表达式中的一组 Case 语句

        [JDK Document] https://docs.oracle.com/javase/specs/jls/se22/html/jls-19.html
        SwitchBlock:
          { SwitchRule {SwitchRule} }
          { {SwitchBlockStatementGroup} {SwitchLabel :} }

        SwitchRule:
          SwitchLabel -> Expression ;
          SwitchLabel -> Block
          SwitchLabel -> ThrowStatement

        SwitchBlockStatementGroup:
          SwitchLabel : {SwitchLabel :} BlockStatements

        [JDK Code] JavacParser.switchExpressionStatementGroup()

        TODO 补充单元测试（等待 parse_expression、parse_statement 和 block_statements）
        """
        case_pos = self.token.pos
        case_expression_list: List[ast.CaseTree] = []
        labels: List[ast.CaseLabelTree] = []

        if self.token.kind == TokenKind.DEFAULT:
            self.next_token()
            labels.append(ast.DefaultCaseLabelTree.create(**self._info_exclude(case_pos)))
        else:
            self.accept(TokenKind.CASE)
            allow_default = False
            while True:
                label: ast.CaseLabelTree = self.parse_case_label(allow_default=allow_default)
                labels.append(label)
                if self.token.kind != TokenKind.COMMA:
                    break
                self.next_token()  # 跳过 COMMA
                # TODO 待确定 isNone 的逻辑是否正确
                allow_default = (label.kind == TreeKind.CONSTANT_CASE_LABEL
                                 and isinstance(label, ast.ConstantCaseLabelTree)
                                 and label.expression.kind == TreeKind.NULL_LITERAL)
            guard = self.parse_guard(labels[-1])
            if self.token.kind == TokenKind.ARROW:
                self.next_token()
                if self.token.kind == TokenKind.THROW or self.token.kind == TokenKind.LBRACE:
                    statements = [self.parse_statement()]
                    case_expression_list.append(ast.CaseTree.create_rule(
                        labels=labels,
                        guard=guard,
                        statements=statements,
                        body=statements[0],
                        **self._info_exclude(case_pos)
                    ))
                else:
                    value = self.parse_expression()
                    statements = [ast.YieldTree.create(value=value, **self._info_exclude(value.start_pos))]
                    case_expression_list.append(ast.CaseTree.create_statement(
                        labels=labels,
                        guard=guard,
                        statements=statements,
                        body=value,
                        **self._info_exclude(case_pos)
                    ))
                    self.accept(TokenKind.SEMI)
            else:
                self.accept(TokenKind.COLON)
                statements = self.block_statements()
                case_expression_list.append(ast.CaseTree.create_statement(
                    labels=labels,
                    guard=guard,
                    statements=statements,
                    body=None,
                    **self._info_exclude(case_pos)
                ))
            return case_expression_list

    def term3_rest(self, expression: ast.ExpressionTree,
                   type_args: Optional[List[ast.ExpressionTree]]) -> ast.ExpressionTree:
        """解析第 3 层级语法元素的剩余部分

        [JDK Document] https://docs.oracle.com/javase/specs/jls/se22/html/jls-19.html
        PostfixExpression:
          Primary
          ExpressionName
          PostIncrementExpression
          PostDecrementExpression

        PostIncrementExpression:
          PostfixExpression ++

        PostDecrementExpression:
          PostfixExpression --

        [JDK Code] JavacParser.term3Rest(JCExpression, List<JCExpression>)

        Examples
        --------
        >>> JavaParser(LexicalFSM("[]"), mode=Mode.TYPE).term3_rest(ast.ExpressionTree.mock(), None).kind.name
        'ARRAY_TYPE'
        >>> JavaParser(LexicalFSM("[1]"), mode=Mode.EXPR).term3_rest(ast.ExpressionTree.mock(), None).kind.name
        'ARRAY_ACCESS'
        >>> JavaParser(LexicalFSM("++"), mode=Mode.EXPR).term3_rest(ast.ExpressionTree.mock(), None).kind.name
        'PREFIX_INCREMENT'
        >>> JavaParser(LexicalFSM("--"), mode=Mode.EXPR).term3_rest(ast.ExpressionTree.mock(), None).kind.name
        'PREFIX_DECREMENT'
        """
        if type_args is not None:
            self.illegal()
        while True:
            pos_1 = self.token.pos
            annotations: List[ast.AnnotationTree] = self.type_annotations_opt()
            if self.token.kind == TokenKind.LBRACKET:
                self.next_token()  # 跳过 LBRACKET
                if self.is_mode(Mode.TYPE):
                    prev_mode = self.mode
                    self.select_type_mode()
                    if self.token.kind == TokenKind.RBRACKET:
                        # term3 [ ]
                        self.next_token()  # 跳过 RBRACKET
                        expression = self.brackets_opt(expression)
                        expression = ast.ArrayTypeTree.create(
                            expression=expression,
                            **self._info_exclude(pos_1)
                        )

                        # term3 [ ] ::
                        if self.token.kind == TokenKind.COL_COL:
                            self.select_expr_mode()
                            continue
                        if annotations:
                            expression = ast.AnnotatedTypeTree.create(
                                annotations=annotations,
                                underlying_type=expression,
                                **self._info_exclude(pos_1)
                            )
                        return expression
                    self.set_mode(prev_mode)

                # term3 [ index ]
                if self.is_mode(Mode.EXPR):
                    self.select_expr_mode()
                    index = self.term()
                    expression = ast.ArrayAccessTree.create(
                        expression=expression,
                        index=index,
                        **self._info_exclude(pos_1)
                    )
                self.accept(TokenKind.RBRACKET)
            elif self.token.kind == TokenKind.DOT:
                self.next_token()  # 跳过 DOT
                type_args = self.type_argument_list_opt(Mode.EXPR)

                # term3 . super ( expression , ... )
                if self.token.kind == TokenKind.SUPER and self.is_mode(Mode.EXPR):
                    self.select_expr_mode()
                    expression = ast.MemberSelectTree.create(
                        expression=expression,
                        identifier=ast.IdentifierTree.create(name="super", **self._info_include(self.token.pos)),
                        **self._info_include(self.token.pos)
                    )
                    self.next_token()  # 跳过 SUPER
                    expression = self.arguments(type_args, expression)
                    type_args = None

                # term3 . new < type_argument, ... >
                elif self.token.kind == TokenKind.NEW and self.is_mode(Mode.EXPR):
                    if type_args is not None:
                        self.illegal()
                    self.select_expr_mode()
                    pos_2 = self.token.pos
                    self.next_token()  # 跳过 NEW
                    if self.token.kind == TokenKind.LT:
                        type_args = self.type_argument_list(diamond_allowed=False)
                    expression = self.inner_creator(pos_2, type_args, expression)
                    type_args = None

                # term . identifier {type_annotations} {(argument, ...)}
                else:
                    type_annotations: Optional[List[ast.AnnotationTree]] = None
                    if self.is_mode(Mode.TYPE) and self.token.kind == TokenKind.MONKEYS_AT:
                        type_annotations = self.type_annotations_opt()
                    expression = ast.MemberSelectTree.create(
                        expression=expression,
                        identifier=ast.IdentifierTree.create(name=self.ident(), **self._info_exclude(self.token.pos)),
                        **self._info_include(self.token.pos)
                    )
                    # TODO 待补充错误恢复逻辑
                    if type_annotations:
                        expression = ast.AnnotatedTypeTree.create(
                            annotations=type_annotations,
                            underlying_type=expression,
                            **self._info_exclude(type_annotations[0].start_pos)
                        )
                    expression = self.arguments_opt(type_args, self.type_arguments_opt(expression))
                    type_args = None

            # [JDK Document] https://docs.oracle.com/javase/specs/jls/se22/html/jls-19.html
            # MethodReference:
            #   ExpressionName :: [TypeArguments] Identifier
            #   Primary :: [TypeArguments] Identifier
            #   ReferenceType :: [TypeArguments] Identifier
            #   super :: [TypeArguments] Identifier
            #   TypeName . super :: [TypeArguments] Identifier
            #   ClassType :: [TypeArguments] new
            #   ArrayType :: new
            elif self.token.kind == TokenKind.COL_COL and self.is_mode(Mode.EXPR):
                self.select_expr_mode()
                if type_args is not None:
                    self.illegal()
                self.accept(TokenKind.COL_COL)
                expression = self.member_reference_suffix(expression, pos=pos_1)

            else:
                if annotations:
                    if self.permit_type_annotations_push_back:
                        self.type_annotations_pushed_back = annotations
                    else:
                        self.illegal()
                break

        while self.token.kind in {TokenKind.PLUS_PLUS, TokenKind.SUB_SUB} and self.is_mode(Mode.EXPR):
            self.select_expr_mode()
            expression = ast.UnaryTree.create(
                kind=grammar_hash.UNARY_OPERATOR_TO_TREE_KIND[self.token.kind],
                expression=expression,
                **self._info_include(self.token.pos)
            )
            self.next_token()  # 跳过 ++ 或 --

        return expression

    def is_unbound_member_ref(self) -> bool:
        """如果在标识符后跟着一个 <，则可能是一个未绑定的方法引用或一个二元表达式。为消除歧义，需要匹配的 > 并查看随后的终结符中是否为 . 或 ::

        Examples
        --------
        >>> JavaParser(LexicalFSM("<name>::"), mode=Mode.EXPR).is_unbound_member_ref()
        True
        >>> JavaParser(LexicalFSM("<name(xx,xx,xx)>::"), mode=Mode.EXPR).is_unbound_member_ref()
        True
        >>> JavaParser(LexicalFSM("<name> value"), mode=Mode.EXPR).is_unbound_member_ref()
        False
        """
        pos = 0
        depth = 0
        while self.lexer.token(pos).kind != TokenKind.EOF:
            token = self.lexer.token(pos)
            if token.kind in {TokenKind.IDENTIFIER, TokenKind.UNDERSCORE, TokenKind.QUES, TokenKind.EXTENDS,
                              TokenKind.SUPER, TokenKind.DOT, TokenKind.RBRACKET, TokenKind.LBRACKET, TokenKind.COMMA,
                              TokenKind.BYTE, TokenKind.SHORT, TokenKind.INT, TokenKind.LONG, TokenKind.FLOAT,
                              TokenKind.DOUBLE, TokenKind.BOOLEAN, TokenKind.CHAR, TokenKind.MONKEYS_AT}:
                pos += 1

            elif token.kind == TokenKind.LPAREN:
                nesting = 0
                while True:
                    tk2 = self.lexer.token(pos).kind
                    if tk2 == TokenKind.EOF:
                        return False
                    if tk2 == TokenKind.LPAREN:
                        nesting += 1
                    elif tk2 == TokenKind.RPAREN:
                        nesting -= 1
                        if nesting == 0:
                            pos += 1
                            break
                    pos += 1

            elif token.kind == TokenKind.LT:
                depth += 1
                pos += 1

            elif token.kind in {TokenKind.GT_GT_GT, TokenKind.GT_GT, TokenKind.GT}:
                if token.kind == TokenKind.GT_GT_GT:
                    depth -= 3
                elif token.kind == TokenKind.GT_GT:
                    depth -= 2
                else:
                    depth -= 1

                if depth == 0:
                    return self.lexer.token(pos + 1).kind in {TokenKind.DOT, TokenKind.LBRACKET, TokenKind.COL_COL}

                pos += 1

            else:
                return False

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

    def super_suffix(self, type_args: Optional[List[ast.ExpressionTree]],
                     expression: ast.ExpressionTree) -> ast.ExpressionTree:
        """super 关键字之后的元素

        [JDK Document] https://docs.oracle.com/javase/specs/jls/se22/html/jls-19.html
        MethodReference:
          ExpressionName :: [TypeArguments] Identifier【不包含】
          Primary :: [TypeArguments] Identifier【不包含】
          ReferenceType :: [TypeArguments] Identifier【不包含】
          super :: [TypeArguments] Identifier
          TypeName . super :: [TypeArguments] Identifier【不包含】
          ClassType :: [TypeArguments] new【不包含】
          ArrayType :: new【不包含】

        [JDK Code] JavacParser.superSuffix(List<JCExpression>, JCExpression)
        SuperSuffix = Arguments | "." [TypeArguments] Ident [Arguments]

        Examples
        --------
        >>> JavaParser(LexicalFSM("super::name")).super_suffix(None, ast.ExpressionTree.mock()).kind.name
        'MEMBER_REFERENCE'
        >>> JavaParser(LexicalFSM("super::name1.name2")).super_suffix(None, ast.ExpressionTree.mock()).kind.name
        'MEMBER_REFERENCE'
        >>> JavaParser(LexicalFSM("super::name1.(arg1)name2")).super_suffix(None, ast.ExpressionTree.mock()).kind.name
        'MEMBER_REFERENCE'
        >>> JavaParser(LexicalFSM("super::name1.(arg1)name2(arg2)")).super_suffix(None, ast.ExpressionTree.mock()).kind.name
        'MEMBER_REFERENCE'
        """
        self.next_token()
        if self.token.kind == TokenKind.LPAREN and type_args is not None:
            return self.arguments(type_args, expression)
        elif self.token.kind == TokenKind.COL_COL:
            if type_args is not None:
                self.raise_syntax_error(self.token.pos, "illegal")
            return self.member_reference_suffix(expression)
        else:
            pos = self.token.pos
            self.accept(TokenKind.DOT)
            type_args: Optional[List[ast.ExpressionTree]] = None
            if self.token.kind == TokenKind.LT:
                type_args = self.type_argument_list(False)
            name = self.ident()
            ident = ast.IdentifierTree.create(
                name=name,
                **self._info_exclude(pos)
            )
            return self.arguments_opt(type_args, ident)

    def basic_type(self) -> ast.PrimitiveTypeTree:
        """原生类型

        [JDK Document] https://docs.oracle.com/javase/specs/jls/se22/html/jls-19.html
        UnannPrimitiveType:
          NumericType
          boolean

        NumericType:
          IntegralType
          FloatingPointType

        IntegralType:
          (one of)
          byte short int long char

        FloatingPointType:
          (one of)
          float double

        [JDK Code] JavacParser.basicType
        BasicType = BYTE | SHORT | CHAR | INT | LONG | FLOAT | DOUBLE | BOOLEAN

        Examples
        --------
        >>> result = JavaParser(LexicalFSM("byte")).basic_type()
        >>> result.kind.name
        'PRIMITIVE_TYPE'
        >>> result.source
        'byte'
        >>> result.type_kind.name
        'BYTE'
        """
        type_kind = grammar_hash.TOKEN_TO_TYPE_KIND[self.token.kind]
        primitive_type = ast.PrimitiveTypeTree.create(
            type_kind=type_kind,
            **self._info_include(self.token.pos)
        )
        self.next_token()
        return primitive_type

    def arguments_opt(self,
                      type_args: Optional[List[ast.ExpressionTree]],
                      expression: ast.ExpressionTree) -> ast.ExpressionTree:
        """可选择的包含括号的实参列表

        [JDK Code] JavacParser.argumentsOpt
        ArgumentsOpt = [ Arguments ]

        Examples
        --------
        >>> parser = JavaParser(LexicalFSM("(name1)"))
        >>> parser.select_expr_mode()
        >>> res1 = parser.arguments_opt(None, ast.ExpressionTree.mock())
        >>> res1.kind.name
        'METHOD_INVOCATION'
        >>> if isinstance(res1, ast.MethodInvocationTree):
        ...     len(res1.arguments)
        1
        >>> parser = JavaParser(LexicalFSM("(name1, name2)"))
        >>> parser.select_expr_mode()
        >>> res1 = parser.arguments_opt(None, ast.ExpressionTree.mock())
        >>> res1.kind.name
        'METHOD_INVOCATION'
        >>> if isinstance(res1, ast.MethodInvocationTree):
        ...     len(res1.arguments)
        2
        """
        if (self.is_mode(Mode.EXPR) and self.token.kind == TokenKind.LPAREN) or type_args is not None:
            self.select_expr_mode()
            return self.arguments(type_args, expression)
        else:
            return expression

    def argument_list(self) -> List[ast.ExpressionTree]:
        """包含括号的实参节点的列表

        [JDK Document] https://docs.oracle.com/javase/specs/jls/se22/html/jls-19.html
        ArgumentList:
          Expression {, Expression}

        [JDK Code] JavacParser.arguments()
        Arguments = "(" [Expression { COMMA Expression }] ")"
        """
        args = []
        if self.token.kind != TokenKind.LPAREN:
            self.raise_syntax_error(self.token.pos, f"expect LPAREN, gut get {self.token.kind.name}")
        self.next_token()
        if self.token.kind != TokenKind.RPAREN:
            args.append(self.parse_expression())
            while self.token.kind == TokenKind.COMMA:
                self.next_token()
                args.append(self.parse_expression())
        self.accept(TokenKind.RPAREN)
        return args

    def arguments(self, type_arguments: List[ast.ExpressionTree], expression: ast.ExpressionTree) -> ast.ExpressionTree:
        """包含括号的实参节点

        [JDK Code] JavacParser.arguments(List<JCExpression>, JCExpression)
        """
        pos = self.token.pos
        arguments = self.argument_list()
        return ast.MethodInvocationTree.create(
            type_arguments=type_arguments,
            method_select=expression,
            arguments=arguments,
            **self._info_exclude(pos)
        )

    def type_arguments_opt(self, expression: ast.ExpressionTree) -> ast.ExpressionTree:
        """可选的类型实参

        [JDK Code] JavacParser.typeArgumentsOpt(JCExpression t)
        TypeArgumentsOpt = [ TypeArguments ]

        Examples
        --------
        >>> parser = JavaParser(LexicalFSM("<name1>"))
        >>> parser.select_expr_mode()
        >>> parser.type_arguments_opt(ast.ExpressionTree.mock()).kind.name
        'PARAMETERIZED_TYPE'
        """
        if self.token.kind == TokenKind.LT and self.is_mode(Mode.EXPR) and not self.is_mode(Mode.NO_PARAMS):
            self.select_type_mode()
            return self.type_arguments(expression, False)
        return expression

    def type_argument_list_opt(self, use_mode: Mode = Mode.TYPE) -> Optional[List[ast.ExpressionTree]]:
        """可选的多个类型实参的列表

        [JDK Code 1] JavacParser.typeArgumentsOpt()
        [JDK Code 2] JavacParser.typeArgumentsOpt(int useMode)
        TypeArgumentsOpt = [ TypeArguments ]

        Examples
        --------
        >>> parser = JavaParser(LexicalFSM("<name1>"))
        >>> parser.select_type_mode()
        >>> len(parser.type_argument_list_opt())
        1
        >>> JavaParser(LexicalFSM("")).type_argument_list_opt() is None
        True
        """
        if self.token.kind != TokenKind.LT:
            return None
        if not self.is_mode(use_mode) or self.is_mode(Mode.NO_PARAMS):
            self.illegal()
        self.set_mode(use_mode)
        return self.type_argument_list(False)

    def type_argument_list(self, diamond_allowed: bool) -> List[ast.ExpressionTree]:
        """多个类型实参的列表

        [JDK Document] https://docs.oracle.com/javase/specs/jls/se22/html/jls-19.html
        TypeArguments:
          < TypeArgumentList >

        TypeArgumentList:
          TypeArgument {, TypeArgument}

        [JDK Code] JavacParser.typeArguments
        TypeArguments  = "<" TypeArgument {"," TypeArgument} ">"

        Parameters
        ----------
        diamond_allowed : bool
            是否允许没有实参的类型实参，即 "<>"

        Examples
        --------
        >>> len(JavaParser(LexicalFSM("<>")).type_argument_list(True))
        0
        >>> len(JavaParser(LexicalFSM("<String>")).type_argument_list(True))
        1
        >>> len(JavaParser(LexicalFSM("<String, int>")).type_argument_list(True))
        2
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
            raise JavaSyntaxError(f"expect GT or COMMA in type_arguments, "
                                  f"but find {self.token.kind.name}({self.token.kind.value})")

        return args

    def type_argument(self) -> ast.ExpressionTree:
        """单个类型实参

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

        Examples
        --------
        >>> # JavaParser(LexicalFSM("String>")).type_argument()
        >>> JavaParser(LexicalFSM("?>")).type_argument().kind.name
        'UNBOUNDED_WILDCARD'
        >>> JavaParser(LexicalFSM("? extends Number>")).type_argument().kind.name
        'EXTENDS_WILDCARD'
        >>> JavaParser(LexicalFSM("? super Number>")).type_argument().kind.name
        'SUPER_WILDCARD'
        >>> # JavaParser(LexicalFSM("@NonNull String>")).type_argument()
        >>> JavaParser(LexicalFSM("? super Number & Comparable<?>>")).type_argument().kind.name
        'SUPER_WILDCARD'
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

    def type_arguments(self, expression: ast.ExpressionTree, diamond_allowed: bool) -> ast.ParameterizedTypeTree:
        """包含尖括号的类型实参

        [JDK Document] https://docs.oracle.com/javase/specs/jls/se22/html/jls-19.html
        TypeArgumentsOrDiamond:
          TypeArguments
          <>

        [JDK Code] JavacParser.typeArguments

        Examples
        --------
        >>> JavaParser(LexicalFSM("<>")).type_arguments(ast.ExpressionTree.mock(), True).kind.name
        'PARAMETERIZED_TYPE'
        >>> JavaParser(LexicalFSM("<String>")).type_arguments(ast.ExpressionTree.mock(), False).kind.name
        'PARAMETERIZED_TYPE'
        """
        pos = self.token.pos
        type_arguments = self.type_argument_list(diamond_allowed=diamond_allowed)
        return ast.ParameterizedTypeTree.create(
            type_name=expression,
            type_arguments=type_arguments,
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

    def brackets_suffix(self, expression: ast.ExpressionTree) -> ast.ExpressionTree:
        """可选的 .class

        [JDK Document] https://docs.oracle.com/javase/specs/jls/se22/html/jls-19.html
        ClassLiteral: 【后缀部分】
          TypeName {[ ]} . class
          NumericType {[ ]} . class
          boolean {[ ]} . class
          void . class

        [JDK Code] JavacParser.bracketsSuffix(JCExpression)
        BracketsSuffixExpr = "." CLASS
        BracketsSuffixType =

        Examples
        --------
        >>> JavaParser(LexicalFSM(".class"), mode=Mode.EXPR).brackets_suffix(ast.ExpressionTree.mock()).kind.name
        'MEMBER_SELECT'
        """
        if self.is_mode(Mode.EXPR) and self.token.kind == TokenKind.DOT:
            self.select_expr_mode()
            pos1 = self.token.pos
            self.next_token()  # 跳过 DOT
            pos2 = self.token.pos
            self.accept(TokenKind.CLASS)
            # TODO 待增加语法检查和错误语法处理逻辑
            return ast.MemberSelectTree.create(
                expression=expression,
                identifier=ast.IdentifierTree.create(name="class", **self._info_exclude(pos2)),
                **self._info_include(pos1)
            )
        elif self.is_mode(Mode.TYPE):
            if self.token.kind != TokenKind.COL_COL:
                self.select_type_mode()
        elif self.token.kind != TokenKind.COL_COL:
            self.raise_syntax_error(self.token.pos, "DotClassExpected")
        return expression

    def member_reference_suffix(self, expression: ast.ExpressionTree, pos: Optional[int] = None) -> ast.ExpressionTree:
        """方法引用表达式的后缀

        [JDK Document] https://docs.oracle.com/javase/specs/jls/se22/html/jls-19.html
        MethodReference: 【后缀部分】
          ExpressionName :: [TypeArguments] Identifier
          Primary :: [TypeArguments] Identifier
          ReferenceType :: [TypeArguments] Identifier
          super :: [TypeArguments] Identifier
          TypeName . super :: [TypeArguments] Identifier
          ClassType :: [TypeArguments] new
          ArrayType :: new

        [JDK Code] JavacParser.memberReferenceSuffix
        MemberReferenceSuffix = "::" [TypeArguments] Ident
                              | "::" [TypeArguments] "new"

        Examples
        --------
        >>> JavaParser(LexicalFSM("::name")).member_reference_suffix(ast.ExpressionTree.mock()).kind.name
        'MEMBER_REFERENCE'
        """
        if pos is None:
            pos = self.token.pos
            self.accept(TokenKind.COL_COL)

        self.select_expr_mode()
        type_arguments: Optional[List[ast.ExpressionTree]] = None
        if self.token.kind == TokenKind.LT:
            type_arguments = self.type_argument_list(False)
        if self.token.kind == TokenKind.NEW:
            ref_mode = ReferenceMode.NEW
            ref_name = "init"
            self.next_token()
        else:
            ref_mode = ReferenceMode.INVOKE
            ref_name = self.ident()
        return ast.MemberReferenceTree.create(
            mode=ref_mode,
            name=ref_name,
            qualifier_expression=expression,
            type_arguments=type_arguments,
            **self._info_exclude(pos)
        )

    def creator(self, new_pos: int, type_args: Optional[List[ast.ExpressionTree]]) -> ast.ExpressionTree:
        """调用的构造方法

        [JDK Document] https://docs.oracle.com/javase/specs/jls/se22/html/jls-19.html
        ClassOrInterfaceTypeToInstantiate:
          {Annotation} Identifier {. {Annotation} Identifier} [TypeArgumentsOrDiamond]

        [JDK Code] JavacParser.creator
        Creator = [Annotations] Qualident [TypeArguments] ( ArrayCreatorRest | ClassCreatorRest )

        Examples
        --------
        >>> JavaParser(LexicalFSM("int[]{}")).creator(0, None).kind.name
        'NEW_ARRAY'
        >>> JavaParser(LexicalFSM("wrap1.wrap2.TypeName[]{}")).creator(0, None).kind.name
        'NEW_ARRAY'
        >>> res = JavaParser(LexicalFSM("ClassName (name1, name2) {}")).creator(0, [])
        >>> res.kind.name
        'NEW_CLASS'
        >>> len(res.arguments) if isinstance(res, ast.NewClassTree) else None
        2
        >>> res = JavaParser(LexicalFSM("wrap1.wrap2.ClassName (name1, name2) {}")).creator(0, [])
        >>> res.kind.name
        'NEW_CLASS'
        >>> len(res.arguments) if isinstance(res, ast.NewClassTree) else None
        2
        """
        new_annotations = self.type_annotations_opt()

        # 解析原生类型数组的场景
        if (self.token.kind in {TokenKind.BYTE, TokenKind.SHORT, TokenKind.CHAR, TokenKind.INT, TokenKind.LONG,
                                TokenKind.FLOAT, TokenKind.DOUBLE, TokenKind.BOOLEAN}
                and type_args is None):
            if len(new_annotations) == 0:
                return self.array_creator_rest(new_pos, self.basic_type())
            else:
                annotated_type = ast.AnnotatedTypeTree.create(
                    annotations=new_annotations,
                    underlying_type=self.basic_type(),
                    **self._info_exclude(new_annotations[0].start_pos)
                )
                return self.array_creator_rest(new_pos, annotated_type)

        # 解析名称部分
        expression = self.qualident(allow_annotations=True)

        prev_mode = self.mode
        self.select_type_mode()
        diamond_found = False
        last_type_args_pos = -1

        if self.token.kind == TokenKind.LT:
            last_type_args_pos = self.token.pos
            expression = self.type_arguments(expression, True)
            diamond_found = self.is_mode(Mode.DIAMOND)

        while self.token.kind == TokenKind.DOT:
            if diamond_found is True:
                self.illegal(self.token.pos)
            pos = self.token.pos
            self.next_token()
            type_annotations = self.type_annotations_opt()
            expression = ast.IdentifierTree.create(
                name=self.ident(),
                **self._info_exclude(pos)
            )
            if type_annotations is not None and len(type_annotations) > 0:
                expression = ast.AnnotatedTypeTree.create(
                    annotations=type_annotations,
                    underlying_type=expression,
                    **self._info_exclude(pos)
                )
                if self.token.kind == TokenKind.LT:
                    last_type_args_pos = self.token.pos
                    expression = self.type_arguments(expression, True)
                    diamond_found = self.is_mode(Mode.DIAMOND)
        self.set_mode(prev_mode)
        if self.token.kind in {TokenKind.LBRACKET, TokenKind.MONKEYS_AT}:
            if new_annotations:
                # TODO 考虑是否需要增加 insertAnnotationsToMostInner 的逻辑
                expression = ast.AnnotatedTypeTree.create(
                    annotations=new_annotations,
                    underlying_type=expression,
                    **self._info_include(None)
                )

            expression_2 = self.array_creator_rest(new_pos, expression)
            if diamond_found:
                self.raise_syntax_error(last_type_args_pos, "CannotCreateArrayWithDiamond")
            if type_args:
                self.raise_syntax_error(new_pos, "CannotCreateArrayWithTypeArguments")
            return expression_2
        elif self.token.kind == TokenKind.LPAREN:
            if new_annotations:
                # TODO 考虑是否需要增加 insertAnnotationsToMostInner 的逻辑
                expression = ast.AnnotatedTypeTree.create(
                    annotations=new_annotations,
                    underlying_type=expression,
                    **self._info_include(None)
                )
            return self.class_creator_rest(new_pos, None, type_args, expression)
        else:
            self.raise_syntax_error(new_pos, f"expect LPAREN or LBRACKET, but get {self.token.kind.name}")

    def inner_creator(self, new_pos: int,
                      type_args: List[ast.ExpressionTree],
                      encl: ast.ExpressionTree) -> ast.ExpressionTree:
        """TODO 名称待整理

        [JDK Code] JavacParser.innerCreator(int, List<JCExpression>, JCExpression)
        InnerCreator = [Annotations] Ident [TypeArguments] ClassCreatorRest
        """
        new_annotations = self.type_annotations_opt()
        expression = ast.IdentifierTree.create(
            name=self.ident(),
            **self._info_exclude(self.token.pos)
        )

        if new_annotations:
            expression = ast.AnnotatedTypeTree.create(
                annotations=new_annotations,
                underlying_type=expression,
                **self._info_exclude(new_annotations[0].start_pos)
            )

        if self.token.kind == TokenKind.LT:
            prev_mode = self.mode
            expression = self.type_arguments(expression, True)
            self.set_mode(prev_mode)

        return self.class_creator_rest(new_pos, encl, type_args, expression)

    def array_creator_rest(self, new_pos: int, elem_type: ast.ExpressionTree) -> ast.ExpressionTree:
        """数组的构造方法的剩余部分

        [JDK Document] https://docs.oracle.com/javase/specs/jls/se22/html/jls-19.html
        DimExprs:
          DimExpr {DimExpr}

        DimExpr:
          {Annotation} [ Expression ]

        [JDK Code] JavacParser.arrayCreatorRest
        ArrayCreatorRest = [Annotations] "[" ( "]" BracketsOpt ArrayInitializer
                               | Expression "]" {[Annotations]  "[" Expression "]"} BracketsOpt )

        Examples
        --------
        >>> res = JavaParser(LexicalFSM("[]{}")).array_creator_rest(0, ast.ExpressionTree.mock())
        >>> res.kind.name
        'NEW_ARRAY'
        >>> len(getattr(res, "initializers"))
        0
        >>> res = JavaParser(LexicalFSM("[]{1, 2, 3}")).array_creator_rest(0, ast.ExpressionTree.mock())
        >>> res.kind.name
        'NEW_ARRAY'
        >>> len(getattr(res, "initializers"))
        3
        """
        annotations = self.type_annotations_opt()
        self.accept(TokenKind.LBRACKET)
        if self.token.kind == TokenKind.RBRACKET:
            self.accept(TokenKind.RBRACKET)
            elem_type = self.brackets_opt(elem_type, annotations)
            if self.token.kind != TokenKind.LBRACE:
                self.raise_syntax_error(self.token.pos, "ArrayDimensionMissing")
            array = self.array_initializer(new_pos, elem_type)
            if len(annotations) > 0:
                # 如果将注解没有写在 [ ] 之中，则需要修正它
                assert isinstance(elem_type, ast.AnnotatedTypeTree)
                assert elem_type.annotations == annotations
                array.annotations = elem_type.annotations
                array.array_type = elem_type.underlying_type
            return array
        else:
            dims: List[ast.ExpressionTree] = []
            dim_annotations: List[List[ast.AnnotationTree]] = [annotations]
            dims.append(self.parse_expression())
            self.accept(TokenKind.RBRACKET)
            while self.token.kind in {TokenKind.LBRACKET, TokenKind.MONKEYS_AT}:
                maybe_dim_annotations = self.type_annotations_opt()
                pos = self.token.pos
                self.next_token()
                if self.token.kind == TokenKind.RBRACKET:
                    elem_type = self.brackets_opt_cont(elem_type, pos, maybe_dim_annotations)
                else:
                    dim_annotations.append(maybe_dim_annotations)
                    dims.append(self.parse_expression())
                    self.accept(TokenKind.RBRACKET)

            err_pos = self.token.pos
            initializers = self.array_initializer_elements()
            if initializers is not None:
                self.raise_syntax_error(err_pos, "IllegalArrayCreationBothDimensionAndInitialization")

            new_array = ast.NewArrayTree.create(
                array_type=elem_type,
                dimensions=dims,
                initializers=initializers,
                dim_annotations=dim_annotations,
                **self._info_exclude(new_pos)
            )
            return new_array

    def class_creator_rest(self,
                           new_pos: int,
                           enclosing: Optional[ast.ExpressionTree],
                           type_arguments: List[ast.ExpressionTree],
                           expression: ast.ExpressionTree) -> ast.NewClassTree:
        """类构造方法的剩余部分

        [JDK Code] JavacParser.classCreatorRest
        ClassCreatorRest = Arguments [ClassBody]

        Examples
        --------
        >>> res = JavaParser(LexicalFSM("(name1, name2) {}")).class_creator_rest(0, None, [], ast.ExpressionTree.mock())
        >>> res.kind.name
        'NEW_CLASS'
        >>> res.identifier.kind.name
        'MOCK'
        >>> len(res.arguments)
        2
        """
        arguments = self.argument_list()
        class_body: Optional[ast.NewClassTree] = None
        if self.token.kind == TokenKind.LBRACE:
            pos = self.token.pos
            members: List[ast.Tree] = self.class_interface_or_record_body(None, False, False)
            modifiers = ast.ModifiersTree.create_empty()
            class_body = ast.ClassTree.create_anonymous_class(
                modifiers=modifiers,
                members=members,
                **self._info_exclude(pos)
            )
        return ast.NewClassTree.create(
            enclosing=enclosing,
            type_arguments=type_arguments,
            identifier=expression,
            arguments=arguments,
            class_body=class_body,
            **self._info_exclude(new_pos)
        )

    def array_initializer(self, new_pos: int, expression: Optional[ast.ExpressionTree]) -> ast.NewArrayTree:
        """数组初始化

        [JDK Code] JavacParser.arrayInitializer
        ArrayInitializer = "{" [VariableInitializer {"," VariableInitializer}] [","] "}"

        Examples
        --------
        >>> res = JavaParser(LexicalFSM("{}")).array_initializer(0, None)
        >>> res.kind.name
        'NEW_ARRAY'
        >>> len(getattr(res, "initializers"))
        0
        >>> res = JavaParser(LexicalFSM("{1}")).array_initializer(0, None)
        >>> res.kind.name
        'NEW_ARRAY'
        >>> len(getattr(res, "initializers"))
        1
        >>> res = JavaParser(LexicalFSM("{1, 2}")).array_initializer(0, None)
        >>> res.kind.name
        'NEW_ARRAY'
        >>> len(getattr(res, "initializers"))
        2
        >>> res = JavaParser(LexicalFSM("{1, {2, 3}}")).array_initializer(0, None)
        >>> res.kind.name
        'NEW_ARRAY'
        >>> len(getattr(res, "initializers"))
        2
        >>> getattr(res, "initializers")[1].kind.name
        'NEW_ARRAY'
        """
        initializers = self.array_initializer_elements()
        return ast.NewArrayTree.create(
            array_type=expression,
            dimensions=[],
            initializers=initializers,
            **self._info_exclude(new_pos)
        )

    def array_initializer_elements(self) -> List[ast.ExpressionTree]:
        """数组初始化时，包含大括号的值列表

        [JDK Document] https://docs.oracle.com/javase/specs/jls/se22/html/jls-19.html
        ArrayInitializer:
          { [VariableInitializerList] [,] }

        VariableInitializerList:
          VariableInitializer {, VariableInitializer}

        [JDK Code] JavacParser.arrayInitializerElements
        """
        self.accept(TokenKind.LBRACE)
        initializers = []
        if self.token.kind == TokenKind.COMMA:
            self.next_token()
        elif self.token.kind != TokenKind.RBRACE:
            initializers.append(self.variable_initializer())
            while self.token.kind == TokenKind.COMMA:
                self.next_token()
                if self.token.kind == TokenKind.RBRACE:
                    break
                initializers.append(self.variable_initializer())
        self.accept(TokenKind.RBRACE)
        return initializers

    def variable_initializer(self) -> ast.ExpressionTree:
        """初始化变量值

        [JDK Document] https://docs.oracle.com/javase/specs/jls/se22/html/jls-19.html
        VariableInitializer:
          Expression
          ArrayInitializer

        [JDK Code] javacParser.variableInitializer
        VariableInitializer = ArrayInitializer | Expression
        """
        if self.token.kind == TokenKind.LBRACE:
            return self.array_initializer(self.token.pos, None)
        return self.parse_expression()

    def par_expression(self) -> ast.ParenthesizedTree:
        """括号框柱的表达式

        [JDK Code] JavacParser.parExpression()
        ParExpression = "(" Expression ")"

        Examples
        --------
        >>> JavaParser(LexicalFSM("(expr)")).par_expression().kind.name
        'PARENTHESIZED'
        """
        pos = self.token.pos
        self.accept(TokenKind.LPAREN)
        expression = self.parse_expression()
        self.accept(TokenKind.RPAREN)
        return ast.ParenthesizedTree.create(
            expression=expression,
            **self._info_exclude(pos)
        )

    def block(self, pos: int, flags: int) -> ast.BlockTree:
        """解析代码块

        [JDK Code] JavacParser.block
        Block = "{" BlockStatements "}"
        """
        return ast.BlockTree.mock()  # TODO 待开发真实执行逻辑

    def block_statements(self) -> List[ast.StatementTree]:
        """TODO 名称待整理

        [JDK Code] JavacParser.blockStatements
        BlockStatements = { BlockStatement }
        BlockStatement  = LocalVariableDeclarationStatement
                        | ClassOrInterfaceOrEnumDeclaration
                        | [Ident ":"] Statement
        LocalVariableDeclarationStatement
                        = { FINAL | '@' Annotation } Type VariableDeclarators ";"
        """
        return []  # TODO 待开发真实执行逻辑

    def parse_statement(self) -> ast.StatementTree:
        """解析语句

        [JDK Code] JavacParser.parseStatement()
        """
        return ast.StatementTree.mock()  # TODO 待开发真实执行逻辑

    def parse_case_label(self, allow_default: bool) -> ast.CaseLabelTree:
        """switch 语句中的 case 子句

        [JDK Document] https://docs.oracle.com/javase/specs/jls/se22/html/jls-19.html
        SwitchLabel:
          case CaseConstant {, CaseConstant}
          case null [, default]
          case CasePattern {, CasePattern} [Guard] 【不包含 Guard】
          default

        CaseConstant:
          ConditionalExpression

        CasePattern:
          Pattern

        [JDK Code] JavacParser.parseCaseLabel(boolean allowDefault)

        Examples
        --------
        >>> JavaParser(LexicalFSM("default")).parse_case_label(True).kind.name
        'DEFAULT_CASE_LABEL'
        >>> JavaParser(LexicalFSM("1")).parse_case_label(True).kind.name
        'CONSTANT_CASE_LABEL'
        >>> JavaParser(LexicalFSM("_ xxx")).parse_case_label(True).kind.name
        'PATTERN_CASE_LABEL'
        """
        pattern_pos = self.token.pos

        # default
        if self.token.kind == TokenKind.DEFAULT:
            if not allow_default:
                self.raise_syntax_error(pattern_pos, "DefaultLabelNotAllowed")
            self.next_token()
            return ast.DefaultCaseLabelTree.create(**self._info_exclude(pattern_pos))

        modifiers = self.opt_final([])

        # case CasePattern {, CasePattern}
        if (modifiers.flags or modifiers.annotations
                or self.analyze_pattern(lookahead=0) == grammar_enum.PatternResult.PATTERN):
            pattern = self.parse_pattern(pattern_pos, modifiers, None, False, True)
            return ast.PatternCaseLabelTree.create(
                pattern=pattern,
                **self._info_exclude(pattern_pos)
            )

        # case CaseConstant {, CaseConstant}
        else:
            expression = self.term(new_mode=Mode.EXPR | Mode.NO_LAMBDA)
            return ast.ConstantCaseLabelTree.create(
                expression=expression,
                **self._info_exclude(pattern_pos)
            )

    def parse_guard(self, label: ast.CaseLabelTree) -> Optional[ast.ExpressionTree]:
        """解析 when Expression 的逻辑

        [JDK Document] https://docs.oracle.com/javase/specs/jls/se22/html/jls-19.html
        Guard:
          when Expression

        [JDK Code] JavacParser.parseGuard(JCCaseLabel)

        Examples
        --------
        >>> JavaParser(LexicalFSM("when expr")).parse_guard(ast.PatternCaseLabelTree.mock()) is not None
        True
        """
        if not (self.token.kind == TokenKind.IDENTIFIER and self.token.name == "when"):
            return None
        pos = self.token.pos
        self.next_token()
        if label.kind != TreeKind.PATTERN_CASE_LABEL:
            self.raise_syntax_error(pos, "GuardNotAllowed")
        return self.term(new_mode=Mode.EXPR | Mode.NO_LAMBDA)

    def analyze_pattern(self, lookahead: int) -> grammar_enum.PatternResult:
        """分析 pattern 的类型

        Examples
        --------
        >>> JavaParser(LexicalFSM("int name")).analyze_pattern(0).name
        'PATTERN'
        >>> JavaParser(LexicalFSM("String name")).analyze_pattern(0).name
        'PATTERN'
        >>> JavaParser(LexicalFSM("int, xxx")).analyze_pattern(0).name
        'EXPRESSION'
        >>> JavaParser(LexicalFSM("int -> xxx")).analyze_pattern(0).name
        'EXPRESSION'
        >>> JavaParser(LexicalFSM("_, ")).analyze_pattern(0).name
        'PATTERN'
        >>> JavaParser(LexicalFSM("_)")).analyze_pattern(0).name
        'PATTERN'
        >>> JavaParser(LexicalFSM("_ xxx")).analyze_pattern(0).name
        'PATTERN'
        >>> JavaParser(LexicalFSM("<>(")).analyze_pattern(0).name
        'PATTERN'
        >>> JavaParser(LexicalFSM("<>")).analyze_pattern(0).name
        'EXPRESSION'
        >>> JavaParser(LexicalFSM("() -> xxx")).analyze_pattern(0).name
        'PATTERN'
        """
        type_depth = 0
        paren_depth = 0
        pending_result = grammar_enum.PatternResult.EXPRESSION
        while True:
            token = self.lexer.token(lookahead)
            if token.kind in {TokenKind.BYTE, TokenKind.SHORT, TokenKind.INT, TokenKind.LONG, TokenKind.FLOAT,
                              TokenKind.DOUBLE, TokenKind.BOOLEAN, TokenKind.CHAR, TokenKind.VOID, TokenKind.ASSERT,
                              TokenKind.ENUM, TokenKind.IDENTIFIER}:
                if paren_depth == 0 and self.peek_token(lookahead, LAX_IDENTIFIER):
                    if paren_depth == 0:
                        return grammar_enum.PatternResult.PATTERN
                    else:
                        pending_result = grammar_enum.PatternResult.EXPRESSION
                elif (type_depth == 0 and paren_depth == 0
                      and self.peek_token(lookahead, TokenKind.ARROW | TokenKind.COMMA)):
                    return grammar_enum.PatternResult.EXPRESSION
            elif token.kind == TokenKind.UNDERSCORE:
                if type_depth == 0 and self.peek_token(lookahead, TokenKind.RPAREN | TokenKind.COMMA):
                    return grammar_enum.PatternResult.PATTERN
                elif type_depth == 0 and self.peek_token(lookahead, LAX_IDENTIFIER):
                    if paren_depth == 0:
                        return grammar_enum.PatternResult.PATTERN
                    else:
                        pending_result = grammar_enum.PatternResult.PATTERN
            elif token.kind in {TokenKind.DOT, TokenKind.QUES, TokenKind.EXTENDS, TokenKind.SUPER, TokenKind.COMMA}:
                continue
            elif token.kind == TokenKind.LT:
                type_depth += 1
            elif token.kind in {TokenKind.GT_GT_GT, TokenKind.GT_GT, TokenKind.GT}:
                if token.kind == TokenKind.GT_GT_GT:
                    type_depth -= 3
                elif token.kind == TokenKind.GT_GT:
                    type_depth -= 2
                else:
                    type_depth -= 1
                if type_depth == 0 and not self.peek_token(lookahead, TokenKind.DOT):
                    if self.peek_token(lookahead, LAX_IDENTIFIER | TokenKind.LPAREN):
                        return grammar_enum.PatternResult.PATTERN
                    else:
                        return grammar_enum.PatternResult.EXPRESSION
                elif type_depth < 0:
                    return grammar_enum.PatternResult.EXPRESSION
            elif token.kind == TokenKind.MONKEYS_AT:
                lookahead = self.skip_annotation(lookahead)
            elif token.kind == TokenKind.LBRACKET:
                if self.peek_token(lookahead, TokenKind.RBRACKET, LAX_IDENTIFIER):
                    return grammar_enum.PatternResult.PATTERN
                elif self.peek_token(lookahead, TokenKind.RBRACKET):
                    lookahead += 1
                else:
                    return pending_result
            elif token.kind == TokenKind.LPAREN:
                if self.lexer.token(lookahead + 1).kind == TokenKind.RPAREN:
                    if paren_depth != 0 and self.lexer.token(lookahead + 2).kind == TokenKind.ARROW:
                        return grammar_enum.PatternResult.EXPRESSION
                    else:
                        return grammar_enum.PatternResult.PATTERN
                paren_depth += 1
            elif token.kind == TokenKind.RPAREN:
                paren_depth -= 1
                if (paren_depth == 0 and type_depth == 0
                        and self.peek_token(lookahead, TokenKind.IDENTIFIER)
                        and self.lexer.token(lookahead + 1).name == "when"):
                    return grammar_enum.PatternResult.PATTERN
            elif token.kind == TokenKind.ARROW:
                if paren_depth > 0:
                    return grammar_enum.PatternResult.EXPRESSION
                else:
                    return pending_result
            elif token.kind == TokenKind.FINAL:
                if paren_depth > 0:
                    return grammar_enum.PatternResult.PATTERN
            else:
                return pending_result
            lookahead += 1

    def type_annotations_opt(self) -> List[ast.AnnotationTree]:
        """TODO"""
        return []

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
            if flag := grammar_hash.TOKEN_TO_MODIFIER.get(tk):
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
            self.raise_syntax_error(pos, "RepeatedModifier(存在重复的修饰符)")

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

    def annotation(self, pos: int, kind: Any) -> ast.AnnotationTree:
        """TODO"""

    def restricted_type_name(self, expression: ast.ExpressionTree) -> Optional[str]:
        """限定类型名称

        [JDK Code] JavacParser.restrictedTypeName(JCExpression, boolean)
        """
        if expression.kind == TreeKind.IDENTIFIER:
            assert isinstance(expression, ast.IdentifierTree)
            if expression.name is not None:
                return self.restricted_type_name_starting_at_source(expression.name)
            else:
                return None
        if expression.kind == TreeKind.ARRAY_TYPE:
            assert isinstance(expression, ast.ArrayTypeTree)
            return self.restricted_type_name(expression.expression)
        return None

    def restricted_type_name_starting_at_source(self, name: str) -> Optional[str]:
        """TODO 名称待整理

        [JDK Code] JavacParser.restrictedTypeNameStartingAtSource
        """
        # TODO 待开发按 JDK 版本警告的逻辑
        if name in {"var", "yield", "record", "sealed", "permits"}:
            return name
        return None

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
            self.raise_syntax_error(pos, "这是一个 lambda 表达式的参数，且 Token 类型不是标识符，且没有任何修饰符或注解，则意味着编译"
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
            self.raise_syntax_error(pos, "we have a lambda parameter that is not an identifier this is a syntax error")
        else:
            return ast.VariableTree.create_by_name_expression(
                modifiers=modifiers,
                name_expression=expression,
                variable_type=variable_type,
                **self._info_include(pos)
            )

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

    def class_interface_or_record_body(self,
                                       class_name: Optional[str],
                                       is_interface: bool,
                                       is_record: bool) -> List[ast.Tree]:
        """解析类 class、interface 或 record 的代码块

        [JDK Code] JavacParser.classInterfaceOrRecordBody
        """
        self.accept(TokenKind.LBRACE)
        self.accept(TokenKind.RBRACE)
        return []  # TODO 待开发实际执行逻辑

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
            self.raise_syntax_error(self.token.pos, f"expect COMMA, RPAREN or LBRACKET, but get {self.token.kind}")
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

    def opt_final(self, flags: List[Modifier]):
        """可选的 final 关键字

        [JDK Code] JavacParser.optFinal
        """
        modifiers = self.modifiers_opt()
        if len({flag for flag in modifiers.flags if flag not in {Modifier.FINAL, Modifier.DEPRECATED}}) > 0:
            self.raise_syntax_error(self.token.pos, f"存在不是 FINAL 的修饰符: {flags}")
        modifiers.flags.extend(flags)
        return modifiers

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

    @staticmethod
    def prec(token_kind: TokenKind) -> grammar_enum.OperatorPrecedence:
        """计算 token_kind 的运算优先级

        [JDK Code] JavacParser.prec(TokenKind)
        """
        return grammar_hash.TOKEN_TO_OPERATOR_PRECEDENCE.get(token_kind, grammar_enum.OperatorPrecedence.NO_PREC)


if __name__ == "__main__":
    print(JavaParser(LexicalFSM("name2 = name1 > 3 ? 2 : 1"), mode=Mode.EXPR).term())
    print(JavaParser(LexicalFSM("name2 += name1 > 3 ? 2 : 1"), mode=Mode.EXPR).term())

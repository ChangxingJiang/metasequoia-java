"""
词法解析器的有限状态自动机

https://docs.oracle.com/javase/specs/jls/se22/html/jls-19.html
https://github.com/openjdk/jdk/blob/249f141211c94afcce70d9d536d84e108e07b4e5/src/jdk.compiler/share/classes/com/sun/tools/javac/code/Flags.java#L556
https://github.com/openjdk/jdk/blob/249f141211c94afcce70d9d536d84e108e07b4e5/src/jdk.compiler/share/classes/com/sun/tools/javac/parser/Tokens.java#L363
https://github.com/openjdk/jdk/blob/249f141211c94afcce70d9d536d84e108e07b4e5/src/jdk.compiler/share/classes/com/sun/tools/javac/parser/JavacParser.java#L3595
"""

import abc
import enum
from typing import Dict, List, Optional, Tuple

from metasequoia_java.lexical.charset import DEFAULT, END_CHAR, END_WORD, HEX_NUMBER, NUMBER, OCT_NUMBER
from metasequoia_java.lexical.keyword import KEYWORD_HASH
from metasequoia_java.lexical.state import LexicalState
from metasequoia_java.lexical.token_kind import TokenKind


class AffiliationStyle(enum.IntEnum):
    """附属元素的类型"""

    SPACE = enum.auto()  # 空格
    LINEBREAK = enum.auto()  # 换行符
    COMMENT_LINE = enum.auto()  # 以 // 开头的注释
    COMMENT_BLOCK = enum.auto()  # 以 /* 开头的注释
    JAVADOC_LINE = enum.auto()  # 以 //* 开头的注释
    JAVADOC_BLOCK = enum.auto()  # 以 /** 开头的注释


class Affiliation:
    """附属元素：包括空格、换行符和注释

    之所以设计附属元素的概念，是为了给构造的抽象语法树提供重新转换为 Java 代码的功能，且在恢复时能够还原原始代码的空格、换行符和注释。从而使构造的抽象
    语法树能够被应用到格式化代码、添加注释的场景。
    """

    __slots__ = ("_style", "_pos", "_end_pos", "_text")

    def __init__(self, style: AffiliationStyle, pos: int, end_pos: int, text: str):
        self._style = style
        self._pos = pos
        self._end_pos = end_pos
        self._text = text

    @property
    def style(self) -> AffiliationStyle:
        return self._style

    @property
    def pos(self) -> int:
        return self._pos

    @property
    def end_pos(self) -> int:
        return self._end_pos

    @property
    def text(self) -> str:
        return self._text


class Token:
    """语法元素"""

    __slots__ = ("_kind", "_pos", "_end_pos", "_affiliations", "_source")

    def __init__(self, kind: TokenKind, pos: int, end_pos: int, affiliations: List[Affiliation], source: Optional[str]):
        """

        Parameters
        ----------
        kind : TokenKind
            语法元素类型
        pos : int
            语法元素开始位置（包含）
        end_pos : int
            语法元素结束位置（不包含）
        affiliations : List[Affiliation]
            语法元素之后的附属元素
        source : Optional[str]
            语法元素的源代码；当前仅当当前语法元素为结束符时源代码为 None
        """
        self._kind = kind
        self._pos = pos
        self._end_pos = end_pos
        self._affiliations = affiliations
        self._source = source

    @property
    def kind(self) -> TokenKind:
        return self._kind

    @property
    def pos(self) -> int:
        return self._pos

    @property
    def end_pos(self) -> int:
        return self._end_pos

    @property
    def affiliations(self) -> List[Affiliation]:
        return self._affiliations

    @property
    def source(self) -> str:
        return self._source

    def int_value(self) -> int:
        raise TypeError(f"{self.__class__.__name__}.int_value is undefined!")

    def float_value(self) -> int:
        raise TypeError(f"{self.__class__.__name__}.float_value is undefined!")

    def string_value(self) -> int:
        raise TypeError(f"{self.__class__.__name__}.string_value is undefined!")

    def __repr__(self) -> str:
        return f"{self.kind.name}({self.source}){self.affiliations}"


class IntToken(Token):
    """整数类型的 Token"""

    __slots__ = ("_kind", "_pos", "_end_pos", "_affiliations", "_source", "_value")

    def __init__(self, kind: TokenKind, pos: int, end_pos: int, affiliations: List[Affiliation], source: Optional[str],
                 value: int):
        super().__init__(kind, pos, end_pos, affiliations, source)
        self._value = value

    def int_value(self) -> int:
        return self._value


class FloatToken(Token):
    """浮点数类型的 Token"""

    __slots__ = ("_kind", "_pos", "_end_pos", "_affiliations", "_source", "_value")

    def __init__(self, kind: TokenKind, pos: int, end_pos: int, affiliations: List[Affiliation], source: Optional[str],
                 value: float):
        super().__init__(kind, pos, end_pos, affiliations, source)
        self._value = value

    def float_value(self) -> float:
        return self._value


class StringToken(Token):
    """浮点数类型的 Token"""

    __slots__ = ("_kind", "_pos", "_end_pos", "_affiliations", "_source", "_value")

    def __init__(self, kind: TokenKind, pos: int, end_pos: int, affiliations: List[Affiliation], source: Optional[str],
                 value: str):
        super().__init__(kind, pos, end_pos, affiliations, source)
        self._value = value

    def string_value(self) -> str:
        return self._value


class LexicalFSM:
    """词法解析器自动机的抽象基类"""

    __slots__ = ("_text", "_length", "pos_start", "pos", "state", "affiliations")

    def __init__(self, text: str):
        self._text: str = text  # Unicode 字符串
        self._length: int = len(self._text)  # Unicode 字符串长度

        self.pos_start: int = 0  # 当前词语开始的指针位置
        self.pos: int = 0  # 当前指针位置
        self.state: LexicalState = LexicalState.INIT  # 自动机状态
        self.affiliations: List[Affiliation] = []  # 还没有写入 Token 的附属元素的列表

    @property
    def length(self) -> int:
        return self._length

    # ------------------------------ Unicode 字符串迭代器 ------------------------------

    def _char(self):
        """返回当前字符"""
        if self.pos == self._length:
            return END_CHAR
        return self._text[self.pos]

    # ------------------------------ 工具函数 ------------------------------

    def get_word(self) -> str:
        """根据当前词语开始的指针位置和当前指针位置，截取当前词语"""
        return self._text[self.pos_start: self.pos]

    def pop_affiliation(self) -> List[Affiliation]:
        """获取当前词语之前的附属元素"""
        res = self.affiliations
        self.affiliations = []
        return res

    # ------------------------------ 词法解析主逻辑 ------------------------------

    def lex(self) -> Token:
        """解析并生成一个终结符"""

        while True:
            char = self._char()

            # print(f"state: {self.state.state.name}({self.state.state.value}), char: {char}")

            operate: Optional["Operator"] = FSM_OPERATION_MAP.get((self.state, char))

            if operate is None:
                # 如果没有则使用当前状态的默认处理规则
                operate: "Operator" = FSM_OPERATION_MAP_DEFAULT[self.state]

            res: Optional[Token] = operate(self)
            if res is not None:
                return res


class Operator(abc.ABC):
    """执行逻辑的抽象基类"""

    @abc.abstractmethod
    def __call__(self, fsm: LexicalFSM) -> Optional[Token]:
        """执行逻辑"""


class Nothing(Operator):
    """【不移动指针】无操作"""

    def __call__(self, fsm: LexicalFSM) -> None:
        pass


class NothingSetState(Operator):
    """【不移动指针】无操作 + 设置状态"""

    def __init__(self, state: LexicalState):
        self._state = state

    def __call__(self, fsm: LexicalFSM):
        fsm.state = self._state


class Shift(Operator):
    """【移动指针】移进操作"""

    def __call__(self, fsm: LexicalFSM):
        fsm.pos += 1


class ShiftSetState(Operator):
    """【移动指针】移进操作 + 设置状态"""

    def __init__(self, state: LexicalState):
        self._state = state

    def __call__(self, fsm: LexicalFSM):
        fsm.state = self._state
        fsm.pos += 1


class ReduceSetState(Operator):
    """【不移动指针】结束规约操作，尝试将当前词语解析为关键词"""

    def __init__(self, kind: TokenKind, state: LexicalState):
        self._kind = kind
        self._state = state

    def __call__(self, fsm: LexicalFSM):
        fsm.state = self._state
        source = fsm.get_word()
        fsm.pos_start = fsm.pos
        return Token(
            kind=self._kind,
            pos=fsm.pos_start,
            end_pos=fsm.pos,
            affiliations=fsm.pop_affiliation(),
            source=source
        )


class ReduceIntSetState(Operator):
    """【不移动指针】将当前单词作为整型，执行规约操作，尝试将当前词语解析为关键词"""

    def __init__(self, state: LexicalState):
        self._state = state

    def __call__(self, fsm: LexicalFSM):
        fsm.state = self._state
        source = fsm.get_word()
        fsm.pos_start = fsm.pos
        return IntToken(
            kind=TokenKind.INT_LITERAL,
            pos=fsm.pos_start,
            end_pos=fsm.pos,
            affiliations=fsm.pop_affiliation(),
            source=source,
            value=int(source)
        )


class ReduceLongSetState(Operator):
    """【不移动指针】将当前单词作为长整型，执行规约操作，尝试将当前词语解析为关键词"""

    def __init__(self, state: LexicalState):
        self._state = state

    def __call__(self, fsm: LexicalFSM):
        fsm.state = self._state
        source = fsm.get_word()
        fsm.pos_start = fsm.pos
        return IntToken(
            kind=TokenKind.LONG_LITERAL,
            pos=fsm.pos_start,
            end_pos=fsm.pos,
            affiliations=fsm.pop_affiliation(),
            source=source,
            value=int(source[:-1])
        )


class ReduceOctSetState(Operator):
    """【不移动指针】将当前单词作为八进制整数，执行规约操作，尝试将当前词语解析为关键词"""

    def __init__(self, state: LexicalState):
        self._state = state

    def __call__(self, fsm: LexicalFSM):
        fsm.state = self._state
        source = fsm.get_word()
        fsm.pos_start = fsm.pos
        return IntToken(
            kind=TokenKind.LONG_LITERAL,
            pos=fsm.pos_start,
            end_pos=fsm.pos,
            affiliations=fsm.pop_affiliation(),
            source=source,
            value=int(source[1:], base=8)
        )


class ReduceHexSetState(Operator):
    """【不移动指针】将当前单词作为十六进制整数，执行规约操作，尝试将当前词语解析为关键词"""

    def __init__(self, state: LexicalState):
        self._state = state

    def __call__(self, fsm: LexicalFSM):
        fsm.state = self._state
        source = fsm.get_word()
        fsm.pos_start = fsm.pos
        return IntToken(
            kind=TokenKind.LONG_LITERAL,
            pos=fsm.pos_start,
            end_pos=fsm.pos,
            affiliations=fsm.pop_affiliation(),
            source=source,
            value=int(source[2:], base=16)
        )


class ReduceFloatSetState(Operator):
    """【不移动指针】将当前单词作为单精度浮点数，执行规约操作，尝试将当前词语解析为关键词"""

    def __init__(self, state: LexicalState):
        self._state = state

    def __call__(self, fsm: LexicalFSM):
        fsm.state = self._state
        source = fsm.get_word()
        fsm.pos_start = fsm.pos
        return FloatToken(
            kind=TokenKind.FLOAT_LITERAL,
            pos=fsm.pos_start,
            end_pos=fsm.pos,
            affiliations=fsm.pop_affiliation(),
            source=source, value=float(source[:-1])
        )


class ReduceDoubleSetState(Operator):
    """【不移动指针】将当前单词作为双精度浮点数，执行规约操作，尝试将当前词语解析为关键词"""

    def __init__(self, state: LexicalState):
        self._state = state

    def __call__(self, fsm: LexicalFSM):
        fsm.state = self._state
        source = fsm.get_word()
        fsm.pos_start = fsm.pos
        value = float(source[:-1]) if source.endswith("d") or source.endswith("D") else float(source)
        return FloatToken(
            kind=TokenKind.FLOAT_LITERAL,
            pos=fsm.pos_start,
            end_pos=fsm.pos,
            affiliations=fsm.pop_affiliation(),
            source=source,
            value=value
        )


class ReduceSetStateMaybeKeyword(Operator):
    """【不移动指针】结束规约操作，尝试将当前词语解析为关键词"""

    def __init__(self, state: LexicalState):
        self._state = state

    def __call__(self, fsm: LexicalFSM):
        fsm.state = self._state
        source = fsm.get_word()
        fsm.pos_start = fsm.pos
        kind = KEYWORD_HASH.get(source, TokenKind.IDENTIFIER)
        return Token(kind=kind, pos=fsm.pos_start, end_pos=fsm.pos, affiliations=fsm.pop_affiliation(), source=source)


class MoveReduceSetState(Operator):
    """【移动指针】结束规约操作"""

    def __init__(self, kind: TokenKind, state: LexicalState):
        self._kind = kind
        self._state = state

    def __call__(self, fsm: LexicalFSM):
        fsm.state = self._state
        fsm.pos += 1
        source = fsm.get_word()
        fsm.pos_start = fsm.pos
        return Token(kind=self._kind, pos=fsm.pos_start, end_pos=fsm.pos, affiliations=fsm.pop_affiliation(),
                     source=source)


class Comment(Operator):
    """【移动指针】将当前元素作为附属元素，进行规约操作"""

    def __init__(self, style: AffiliationStyle):
        self._style = style

    def __call__(self, fsm: LexicalFSM):
        source = fsm.get_word()
        fsm.pos_start = fsm.pos
        fsm.affiliations.append(Affiliation(
            style=self._style,
            pos=fsm.pos_start,
            end_pos=fsm.pos,
            text=source
        ))


class CommentSetState(Operator):
    """【移动指针】将当前元素作为附属元素，进行规约操作"""

    def __init__(self, style: AffiliationStyle, state: LexicalState):
        self._style = style
        self._state = state

    def __call__(self, fsm: LexicalFSM):
        fsm.state = self._state
        source = fsm.get_word()
        fsm.pos_start = fsm.pos
        fsm.affiliations.append(Affiliation(
            style=self._style,
            pos=fsm.pos_start,
            end_pos=fsm.pos,
            text=source
        ))


class MoveComment(Operator):
    """【移动指针】将当前元素作为附属元素，进行规约操作"""

    def __init__(self, style: AffiliationStyle):
        self._style = style

    def __call__(self, fsm: LexicalFSM):
        fsm.pos += 1
        source = fsm.get_word()
        fsm.pos_start = fsm.pos
        fsm.affiliations.append(Affiliation(
            style=self._style,
            pos=fsm.pos_start,
            end_pos=fsm.pos,
            text=source
        ))


class MoveCommentSetState(Operator):
    """【移动指针】将当前元素作为附属元素，进行规约操作"""

    def __init__(self, style: AffiliationStyle, state: LexicalState):
        self._style = style
        self._state = state

    def __call__(self, fsm: LexicalFSM):
        fsm.state = self._state
        fsm.pos += 1
        source = fsm.get_word()
        fsm.pos_start = fsm.pos
        fsm.affiliations.append(Affiliation(
            style=self._style,
            pos=fsm.pos_start,
            end_pos=fsm.pos,
            text=source
        ))


class FixedSetState(Operator):
    """【不移动指针】结束固定操作"""

    def __init__(self, kind: TokenKind, source: str, state: LexicalState):
        self._kind = kind
        self._source = source
        self._state = state

    def __call__(self, fsm: LexicalFSM):
        fsm.state = self._state
        fsm.pos_start = fsm.pos
        return Token(kind=self._kind, pos=fsm.pos_start, end_pos=fsm.pos, affiliations=fsm.pop_affiliation(),
                     source=self._source)


class FixedIntSetState(Operator):
    """【不移动指针】将当前单词作为整型，执行固定值规约操作"""

    def __init__(self, source: str, state: LexicalState):
        self._source = source
        self._state = state

    def __call__(self, fsm: LexicalFSM):
        fsm.state = self._state
        fsm.pos_start = fsm.pos
        return IntToken(kind=TokenKind.INT_LITERAL, pos=fsm.pos_start, end_pos=fsm.pos,
                        affiliations=fsm.pop_affiliation(),
                        source=self._source, value=int(self._source))


class MoveFixed(Operator):
    """【移动指针】结束固定操作"""

    def __init__(self, kind: TokenKind, source: str):
        self._kind = kind
        self._source = source

    def __call__(self, fsm: LexicalFSM):
        fsm.pos += 1
        fsm.pos_start = fsm.pos
        return Token(kind=self._kind, pos=fsm.pos_start, end_pos=fsm.pos, affiliations=fsm.pop_affiliation(),
                     source=self._source)


class MoveFixedSetState(Operator):
    """【移动指针】结束固定操作"""

    def __init__(self, kind: TokenKind, source: str, state: LexicalState):
        self._kind = kind
        self._source = source
        self._state = state

    def __call__(self, fsm: LexicalFSM):
        fsm.state = self._state
        fsm.pos += 1
        fsm.pos_start = fsm.pos
        return Token(kind=self._kind, pos=fsm.pos_start, end_pos=fsm.pos, affiliations=fsm.pop_affiliation(),
                     source=self._source)


class Error(Operator):
    """【异常】"""

    def __call__(self, fsm: LexicalFSM):
        raise Exception(f"未知的词法结构，当前状态={fsm}")


class Finish(Operator):
    """【结束】"""

    def __call__(self, fsm: LexicalFSM):
        return Token(kind=TokenKind.EOF, pos=fsm.length, end_pos=fsm.length, affiliations=fsm.pop_affiliation(),
                     source=None)


# 运算符的开始符号
OPERATOR = frozenset({"+", "-", "*", "/", "%", "=", "!", "<", ">", "&", "|", "^", "~", "?"})

# 行为映射表设置表（用于设置配置信息，输入参数允许是一个不可变集合）
FSM_OPERATION_MAP_SOURCE: Dict[LexicalState, Dict[str, Operator]] = {
    # 当前没有正在解析的词语
    LexicalState.INIT: {
        " ": MoveComment(style=AffiliationStyle.SPACE),
        "\n": MoveComment(style=AffiliationStyle.LINEBREAK),
        "{": MoveFixed(kind=TokenKind.LBRACE, source="{"),
        "}": MoveFixed(kind=TokenKind.RBRACE, source="}"),
        "[": MoveFixed(kind=TokenKind.LBRACKET, source="["),
        "]": MoveFixed(kind=TokenKind.RBRACKET, source="]"),
        "(": MoveFixed(kind=TokenKind.LPAREN, source="("),
        ")": MoveFixed(kind=TokenKind.RPAREN, source=")"),
        ".": ShiftSetState(state=LexicalState.DOT),
        ";": MoveFixed(kind=TokenKind.SEMI, source=";"),
        ":": MoveFixed(kind=TokenKind.COLON, source=":"),
        ",": MoveFixed(kind=TokenKind.COMMA, source=","),
        "@": MoveFixed(kind=TokenKind.MONKEYS_AT, source="@"),
        "0": ShiftSetState(state=LexicalState.ZERO),
        frozenset({"1", "2", "3", "4", "5", "6", "7", "8", "9"}): ShiftSetState(state=LexicalState.NUMBER),
        "'": ShiftSetState(state=LexicalState.IN_SINGLE_QUOTE),
        "\"": ShiftSetState(state=LexicalState.IN_DOUBLE_QUOTE),
        "+": ShiftSetState(state=LexicalState.CHAR_ADD),
        "-": ShiftSetState(state=LexicalState.CHAR_SUB),
        "*": ShiftSetState(state=LexicalState.CHAR_MULT),
        "/": ShiftSetState(state=LexicalState.CHAR_DIV),
        "%": ShiftSetState(state=LexicalState.CHAR_MOD),
        "=": ShiftSetState(state=LexicalState.CHAR_EQUAL),
        "!": ShiftSetState(state=LexicalState.CHAR_EXCLAMATION),
        "<": ShiftSetState(state=LexicalState.CHAR_LESS),
        ">": ShiftSetState(state=LexicalState.CHAR_MORE),
        "&": ShiftSetState(state=LexicalState.CHAR_AND),
        "|": ShiftSetState(state=LexicalState.CHAR_OR),
        "^": MoveFixed(kind=TokenKind.CARET, source="^"),
        "~": MoveFixed(kind=TokenKind.TILDE, source="~"),
        "?": MoveFixed(kind=TokenKind.QUES, source="?"),
        END_CHAR: Finish(),
        DEFAULT: ShiftSetState(state=LexicalState.IDENT),
    },
    # 当前词语为不是特殊词语
    LexicalState.IDENT: {
        END_WORD: ReduceSetStateMaybeKeyword(state=LexicalState.INIT),
        OPERATOR: ReduceSetStateMaybeKeyword(state=LexicalState.INIT),
        END_CHAR: ReduceSetStateMaybeKeyword(state=LexicalState.INIT),
        DEFAULT: Shift(),
    },

    # -------------------- 数值字面值 --------------------
    # 0（可能为八进制的前缀）
    LexicalState.ZERO: {
        frozenset({"x", "X"}): ShiftSetState(state=LexicalState.ZERO_X),
        frozenset({"l", "L"}): ShiftSetState(state=LexicalState.NUMBER_LONG),
        frozenset({"f", "f"}): ShiftSetState(state=LexicalState.NUMBER_FLOAT),
        frozenset({"d", "D"}): ShiftSetState(state=LexicalState.NUMBER_DOUBLE),
        NUMBER: ShiftSetState(state=LexicalState.OCT_NUMBER),
        OPERATOR: FixedIntSetState(source="0", state=LexicalState.INIT),
        END_WORD: FixedIntSetState(source="0", state=LexicalState.INIT),
        END_CHAR: FixedIntSetState(source="0", state=LexicalState.INIT),
    },

    # 0[xX]（十六进制的前缀）
    LexicalState.ZERO_X: {
        HEX_NUMBER: ShiftSetState(state=LexicalState.HEX_NUMBER),
    },

    # [1-9][0-9]+（十进制数）
    LexicalState.NUMBER: {
        NUMBER: Shift(),
        frozenset({"l", "L"}): ShiftSetState(state=LexicalState.NUMBER_LONG),
        frozenset({"f", "f"}): ShiftSetState(state=LexicalState.NUMBER_FLOAT),
        frozenset({"d", "D"}): ShiftSetState(state=LexicalState.NUMBER_DOUBLE),
        ".": ShiftSetState(state=LexicalState.NUMBER_DECIMAL),
        frozenset({"e", "E"}): ShiftSetState(state=LexicalState.NUMBER_DECIMAL_E),
        OPERATOR: ReduceIntSetState(state=LexicalState.INIT),
        frozenset(END_WORD - {"."}): ReduceIntSetState(state=LexicalState.INIT),
        END_CHAR: ReduceIntSetState(state=LexicalState.INIT),
    },

    # 0[0-7]+（八进制数）
    LexicalState.OCT_NUMBER: {
        OCT_NUMBER: Shift(),
        OPERATOR: ReduceOctSetState(state=LexicalState.INIT),
        END_WORD: ReduceOctSetState(state=LexicalState.INIT),
        END_CHAR: ReduceOctSetState(state=LexicalState.INIT),
    },

    # 0[xX][0-9a-fA-F]+（十六进制数）
    LexicalState.HEX_NUMBER: {
        HEX_NUMBER: Shift(),
        OPERATOR: ReduceHexSetState(state=LexicalState.INIT),
        END_WORD: ReduceHexSetState(state=LexicalState.INIT),
        END_CHAR: ReduceHexSetState(state=LexicalState.INIT)
    },

    # [1-9][0-9]*L（长整型字面值）
    LexicalState.NUMBER_LONG: {
        OPERATOR: ReduceLongSetState(state=LexicalState.INIT),
        END_WORD: ReduceLongSetState(state=LexicalState.INIT),
        END_CHAR: ReduceLongSetState(state=LexicalState.INIT),
    },

    # [0-9]+\.[0-9]+（小数）
    LexicalState.NUMBER_DECIMAL: {
        NUMBER: Shift(),
        frozenset({"f", "f"}): ShiftSetState(state=LexicalState.NUMBER_FLOAT),
        frozenset({"d", "D"}): ShiftSetState(state=LexicalState.NUMBER_DOUBLE),
        frozenset({"e", "E"}): ShiftSetState(state=LexicalState.NUMBER_DECIMAL_E),
        OPERATOR: ReduceDoubleSetState(state=LexicalState.INIT),
        END_WORD: ReduceDoubleSetState(state=LexicalState.INIT),
        END_CHAR: ReduceDoubleSetState(state=LexicalState.INIT),
    },

    # [0-9]+(\.[0-9]+)?[eE]（科学记数法的前缀）
    LexicalState.NUMBER_DECIMAL_E: {
        NUMBER: ShiftSetState(state=LexicalState.NUMBER_SCIENTIFIC),
        "-": ShiftSetState(state=LexicalState.NUMBER_SCIENTIFIC),
    },

    # [0-9]+(\.[0-9]+)?[eE]-?[0-9]*（科学记数法）
    LexicalState.NUMBER_SCIENTIFIC: {
        NUMBER: Shift(),
        frozenset({"f", "f"}): ShiftSetState(state=LexicalState.NUMBER_FLOAT),
        frozenset({"d", "D"}): ShiftSetState(state=LexicalState.NUMBER_DOUBLE),
        OPERATOR: ReduceDoubleSetState(state=LexicalState.INIT),
        END_WORD: ReduceDoubleSetState(state=LexicalState.INIT),
        END_CHAR: ReduceDoubleSetState(state=LexicalState.INIT),
    },

    # [0-9]+(\.[0-9]+)?([eE]-?[0-9]*)?[fF]（单精度浮点数字面值）
    LexicalState.NUMBER_FLOAT: {
        OPERATOR: ReduceFloatSetState(state=LexicalState.INIT),
        END_WORD: ReduceFloatSetState(state=LexicalState.INIT),
        END_CHAR: ReduceFloatSetState(state=LexicalState.INIT),
    },

    # [0-9]+(\.[0-9]+)?([eE]-?[0-9]*)?[dD]（双精度浮点数字面值）
    LexicalState.NUMBER_DOUBLE: {
        OPERATOR: ReduceDoubleSetState(state=LexicalState.INIT),
        END_WORD: ReduceDoubleSetState(state=LexicalState.INIT),
        END_CHAR: ReduceDoubleSetState(state=LexicalState.INIT),
    },

    # -------------------- 字符字面值 --------------------
    # 在单引号字符串中
    LexicalState.IN_SINGLE_QUOTE: {
        "\\": ShiftSetState(state=LexicalState.IN_SINGLE_QUOTE_ESCAPE),
        "'": MoveReduceSetState(kind=TokenKind.CHAR_LITERAL, state=LexicalState.INIT),
        END_CHAR: Error(),
        DEFAULT: Shift(),
    },

    # 在单引号字符串中的转义符之后
    LexicalState.IN_SINGLE_QUOTE_ESCAPE: {
        END_CHAR: Error(),
        DEFAULT: ShiftSetState(state=LexicalState.IN_SINGLE_QUOTE),
    },

    # -------------------- 字符串字面值 --------------------
    # 在双引号字符串中
    LexicalState.IN_DOUBLE_QUOTE: {
        "\\": ShiftSetState(state=LexicalState.IN_DOUBLE_QUOTE_ESCAPE),
        "\"": MoveReduceSetState(kind=TokenKind.STRING_LITERAL, state=LexicalState.INIT),
        END_CHAR: Error(),
        DEFAULT: Shift(),
    },

    # 在双引号字符串中的转义符之后
    LexicalState.IN_DOUBLE_QUOTE_ESCAPE: {
        END_CHAR: Error(),
        DEFAULT: ShiftSetState(state=LexicalState.IN_DOUBLE_QUOTE),
    },

    # -------------------- 多字符运算符 --------------------
    # +
    LexicalState.CHAR_ADD: {
        "=": MoveFixedSetState(kind=TokenKind.PLUS_EQ, source="+=", state=LexicalState.INIT),
        "+": MoveFixedSetState(kind=TokenKind.PLUS_PLUS, source="++", state=LexicalState.INIT),
        DEFAULT: FixedSetState(kind=TokenKind.PLUS, source="+", state=LexicalState.INIT),
    },

    # -
    LexicalState.CHAR_SUB: {
        "=": MoveFixedSetState(kind=TokenKind.SUB_EQ, source="-=", state=LexicalState.INIT),
        "-": MoveFixedSetState(kind=TokenKind.SUB_SUB, source="--", state=LexicalState.INIT),
        DEFAULT: FixedSetState(kind=TokenKind.SUB, source="-", state=LexicalState.INIT),
    },

    # *
    LexicalState.CHAR_MULT: {
        "=": MoveFixedSetState(kind=TokenKind.STAR_EQ, source="*=", state=LexicalState.INIT),
        DEFAULT: FixedSetState(kind=TokenKind.STAR, source="*", state=LexicalState.INIT),
    },

    # /
    LexicalState.CHAR_DIV: {
        "=": MoveFixedSetState(kind=TokenKind.SLASH_EQ, source="/=", state=LexicalState.INIT),
        "/": ShiftSetState(state=LexicalState.IN_LINE_COMMENT),
        "*": ShiftSetState(state=LexicalState.IN_MULTI_COMMENT),
        DEFAULT: FixedSetState(kind=TokenKind.SLASH, source="/", state=LexicalState.INIT),
    },

    # %
    LexicalState.CHAR_MOD: {
        "=": MoveFixedSetState(kind=TokenKind.PERCENT_EQ, source="%=", state=LexicalState.INIT),
        DEFAULT: FixedSetState(kind=TokenKind.PERCENT, source="%", state=LexicalState.INIT),
    },

    # =
    LexicalState.CHAR_EQUAL: {
        "=": MoveFixedSetState(kind=TokenKind.EQ_EQ, source="==", state=LexicalState.INIT),
        DEFAULT: FixedSetState(kind=TokenKind.EQ, source="=", state=LexicalState.INIT),
    },

    # !
    LexicalState.CHAR_EXCLAMATION: {
        "=": MoveFixedSetState(kind=TokenKind.BANG_EQ, source="!=", state=LexicalState.INIT),
        DEFAULT: FixedSetState(kind=TokenKind.BANG, source="!", state=LexicalState.INIT),
    },

    # <
    LexicalState.CHAR_LESS: {
        "<": MoveFixedSetState(kind=TokenKind.LT_LT, source="<<", state=LexicalState.INIT),
        "=": MoveFixedSetState(kind=TokenKind.LT_EQ, source="<=", state=LexicalState.INIT),
        DEFAULT: FixedSetState(kind=TokenKind.LT, source="<", state=LexicalState.INIT)
    },

    # >
    LexicalState.CHAR_MORE: {
        ">": ShiftSetState(state=LexicalState.CHAR_MORE_MORE),
        "=": MoveFixedSetState(kind=TokenKind.GT_EQ, source=">=", state=LexicalState.INIT),
        DEFAULT: FixedSetState(kind=TokenKind.GT, source=">", state=LexicalState.INIT)
    },

    # >>
    LexicalState.CHAR_MORE_MORE: {
        ">": MoveFixedSetState(kind=TokenKind.GT_GT_GT, source=">>>", state=LexicalState.INIT),
        DEFAULT: FixedSetState(kind=TokenKind.GT_GT, source=">>", state=LexicalState.INIT),
    },

    # &
    LexicalState.CHAR_AND: {
        "&": MoveFixedSetState(kind=TokenKind.AMP_AMP, source="&&", state=LexicalState.INIT),
        DEFAULT: FixedSetState(kind=TokenKind.AMP, source="&", state=LexicalState.INIT),
    },

    # |
    LexicalState.CHAR_OR: {
        "|": MoveFixedSetState(kind=TokenKind.BAR_BAR, source="||", state=LexicalState.INIT),
        DEFAULT: FixedSetState(kind=TokenKind.BAR, source="|", state=LexicalState.INIT),
    },

    # -------------------- 注释 --------------------
    # 在单行注释中
    LexicalState.IN_LINE_COMMENT: {
        "\n": CommentSetState(style=AffiliationStyle.COMMENT_LINE, state=LexicalState.INIT),
        END_CHAR: CommentSetState(style=AffiliationStyle.COMMENT_LINE, state=LexicalState.INIT),
        DEFAULT: Shift()
    },

    # 在多行注释中
    LexicalState.IN_MULTI_COMMENT: {
        "*": ShiftSetState(state=LexicalState.IN_MULTI_COMMENT_STAR),
        END_CHAR: Error(),
        DEFAULT: Shift()
    },

    # 在多行注释中的 * 之后
    LexicalState.IN_MULTI_COMMENT_STAR: {
        "*": Shift(),
        "/": CommentSetState(style=AffiliationStyle.COMMENT_BLOCK, state=LexicalState.INIT),
        END_CHAR: Error(),
        DEFAULT: ShiftSetState(state=LexicalState.IN_MULTI_COMMENT),
    },

    # -------------------- 特殊场景 --------------------
    # .
    LexicalState.POINT: {
        NUMBER: ShiftSetState(state=LexicalState.NUMBER_DECIMAL),  # 当下一个字符是数字时，为浮点数
        DEFAULT: FixedSetState(kind=TokenKind.DOT, source=".", state=LexicalState.INIT),  # 当下一个字符不是数字时，为类名或方法名
    }
}

# 状态行为映射表（用于用时行为映射信息，输入参数必须是一个字符）
FSM_OPERATION_MAP: Dict[Tuple[LexicalState, str], Operator] = {}
FSM_OPERATION_MAP_DEFAULT: Dict[LexicalState, Operator] = {}
for state_, operation_map in FSM_OPERATION_MAP_SOURCE.items():
    # 如果没有定义默认值，则默认其他字符为 Error
    if DEFAULT not in operation_map:
        FSM_OPERATION_MAP_DEFAULT[state_] = Error()

    # 遍历并添加定义的字符到行为映射表中
    for ch_or_set, fsm_operation in operation_map.items():
        if ch_or_set is DEFAULT:
            FSM_OPERATION_MAP_DEFAULT[state_] = fsm_operation
        elif isinstance(ch_or_set, str):
            FSM_OPERATION_MAP[(state_, ch_or_set)] = fsm_operation
        elif isinstance(ch_or_set, frozenset):
            for ch in ch_or_set:
                FSM_OPERATION_MAP[(state_, ch)] = fsm_operation
        else:
            raise KeyError("非法的行为映射表设置表")

    # 将 ASCII 编码 20 - 7E 之间的字符添加到行为映射表中（从而令第一次查询的命中率提高，避免第二次查询）
    for dec in range(32, 127):
        ch = chr(dec)
        if (state_, ch) not in FSM_OPERATION_MAP:
            FSM_OPERATION_MAP[(state_, ch)] = FSM_OPERATION_MAP_DEFAULT[state_]

if __name__ == "__main__":
    lexical_fsm = LexicalFSM("1 + 2//comment")
    token_list = []
    while token := lexical_fsm.lex():
        print("token:", token)
        if token.kind == TokenKind.EOF:
            break

"""
词法解析器的有限状态自动机

https://docs.oracle.com/javase/specs/jls/se22/html/jls-19.html
https://github.com/openjdk/jdk/blob/249f141211c94afcce70d9d536d84e108e07b4e5/src/jdk.compiler/share/classes/com/sun/tools/javac/code/Flags.java#L556
https://github.com/openjdk/jdk/blob/249f141211c94afcce70d9d536d84e108e07b4e5/src/jdk.compiler/share/classes/com/sun/tools/javac/parser/Tokens.java#L363
https://github.com/openjdk/jdk/blob/249f141211c94afcce70d9d536d84e108e07b4e5/src/jdk.compiler/share/classes/com/sun/tools/javac/parser/JavacParser.java#L3595

TODO 令 StringLiteral 和 TextBlock 转换为字符串字面值时 Token 支持 string_value 方法
TODO 增加 JavaDoc 的区分逻辑
"""

import abc
import collections
from typing import Dict, List, Optional, Tuple

from metasequoia_java.lexical.charset import DEFAULT, END_CHAR, END_WORD, HEX_NUMBER, NUMBER, OCT_NUMBER
from metasequoia_java.lexical.keyword_hash import KEYWORD_HASH
from metasequoia_java.lexical.split_hash import SPLIT_HASH
from metasequoia_java.lexical.state import LexicalState
from metasequoia_java.lexical.token import (Affiliation, AffiliationStyle, CharToken, FloatToken, IntToken, StringToken,
                                            Token)
from metasequoia_java.lexical.token_kind import TokenKind


class LexicalFSM:
    """词法解析器自动机的抽象基类

    Bison API：
    - lex()：每次调用时，解析下一个函数并返回

    JDK 词法解析器 API：
    - token(idx = 0)：每次调用时，获取当前终结符之后的第 idx 个终结符，其中 token(0) 为当前终结符
    - next_token()：每次调用时，将当前指向的终结符向后移动 1 个

    其中类似 JDK 词法解析器 API 是通过 Bison 实现的。
    """

    __slots__ = ("_text", "_length", "pos_start", "pos", "state", "affiliations", "_ahead")

    def __init__(self, text: str):
        self._text: str = text  # Unicode 字符串
        self._length: int = len(self._text)  # Unicode 字符串长度

        self.pos_start: int = 0  # 当前词语开始的指针位置
        self.pos: int = 0  # 当前指针位置
        self.state: LexicalState = LexicalState.INIT  # 自动机状态
        self.affiliations: List[Affiliation] = []  # 还没有写入 Token 的附属元素的列表

        self._ahead: collections.deque[Token] = collections.deque()  # 提前获取前置元素的缓存

    @property
    def text(self):
        return self._text

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

    # ------------------------------ Bison API ------------------------------

    def lex(self) -> Token:
        """解析并生成一个终结符"""
        while True:
            char = self._char()

            # print(f"state: {self.state.name}({self.state.value}), char: {char}")

            operate: Optional["Operator"] = FSM_OPERATION_MAP.get((self.state, char))

            if operate is None:
                # 如果没有则使用当前状态的默认处理规则
                operate: "Operator" = FSM_OPERATION_MAP_DEFAULT[self.state]

            res: Optional[Token] = operate(self)
            if res is not None:
                return res

    # ------------------------------ JDK 词法解析器 API ------------------------------

    def token(self, idx: int = 0):
        """提前获取当前终结符之后的第 idx 个终结符，其中 ahead(0) 对应当前终结符"""
        if len(self._ahead) <= idx:
            for _ in range(idx - len(self._ahead) + 1):
                self._ahead.append(self.lex())
        return self._ahead[idx]

    def next_token(self):
        if len(self._ahead) == 0:
            self._ahead.append(self.lex())
        self._ahead.popleft()

    def split(self):
        if len(self._ahead) == 0:
            self._ahead.append(self.lex())
        if self._ahead[0].kind not in SPLIT_HASH:
            raise KeyError("拆分失败")  # TODO 待修改异常类型
        kind1, kind2 = SPLIT_HASH[self._ahead[0].kind]
        token1 = Token(
            kind=kind1,
            pos=self._ahead[0].pos,
            end_pos=self._ahead[0].pos + 1,
            affiliations=self._ahead[0].affiliations,
            source=self._ahead[0].source[0]
        )
        token2 = Token(
            kind=kind2,
            pos=self._ahead[0].pos + 1,
            end_pos=self._ahead[0].end_pos,
            affiliations=[],
            source=self._ahead[0].source[1:]
        )
        self._ahead[0] = token2
        return token1


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
        pos = fsm.pos_start
        source = fsm.get_word()
        fsm.state = self._state
        fsm.pos_start = fsm.pos
        return Token(
            kind=self._kind,
            pos=pos,
            end_pos=fsm.pos,
            affiliations=fsm.pop_affiliation(),
            source=source
        )


class ReduceIntSetState(Operator):
    """【不移动指针】将当前单词作为整型，执行规约操作，尝试将当前词语解析为关键词"""

    def __init__(self, state: LexicalState):
        self._state = state

    def __call__(self, fsm: LexicalFSM):
        pos = fsm.pos_start
        source = fsm.get_word()
        fsm.state = self._state
        fsm.pos_start = fsm.pos
        return IntToken(
            kind=TokenKind.INT_DEC_LITERAL,
            pos=pos,
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
        pos = fsm.pos_start
        source = fsm.get_word()
        fsm.state = self._state
        fsm.pos_start = fsm.pos
        return IntToken(
            kind=TokenKind.LONG_DEC_LITERAL,
            pos=pos,
            end_pos=fsm.pos,
            affiliations=fsm.pop_affiliation(),
            source=source,
            value=int(source[:-1])
        )


class ReduceIntOctSetState(Operator):
    """【不移动指针】将当前单词作为八进制整数，执行规约操作，尝试将当前词语解析为关键词"""

    def __init__(self, state: LexicalState):
        self._state = state

    def __call__(self, fsm: LexicalFSM):
        pos = fsm.pos_start
        source = fsm.get_word()
        fsm.state = self._state
        fsm.pos_start = fsm.pos
        return IntToken(
            kind=TokenKind.INT_OCT_LITERAL,
            pos=pos,
            end_pos=fsm.pos,
            affiliations=fsm.pop_affiliation(),
            source=source,
            value=int(source[1:], base=8)
        )


class ReduceLongOctSetState(Operator):
    """【不移动指针】将当前单词作为八进制长整数，执行规约操作，尝试将当前词语解析为关键词"""

    def __init__(self, state: LexicalState):
        self._state = state

    def __call__(self, fsm: LexicalFSM):
        pos = fsm.pos_start
        source = fsm.get_word()
        fsm.state = self._state
        fsm.pos_start = fsm.pos
        return IntToken(
            kind=TokenKind.LONG_OCT_LITERAL,
            pos=pos,
            end_pos=fsm.pos,
            affiliations=fsm.pop_affiliation(),
            source=source,
            value=int(source[1:-1], base=8)
        )


class ReduceIntHexSetState(Operator):
    """【不移动指针】将当前单词作为十六进制整数，执行规约操作，尝试将当前词语解析为关键词"""

    def __init__(self, state: LexicalState):
        self._state = state

    def __call__(self, fsm: LexicalFSM):
        pos = fsm.pos_start
        source = fsm.get_word()
        fsm.state = self._state
        fsm.pos_start = fsm.pos
        return IntToken(
            kind=TokenKind.INT_HEX_LITERAL,
            pos=pos,
            end_pos=fsm.pos,
            affiliations=fsm.pop_affiliation(),
            source=source,
            value=int(source[2:], base=16)
        )


class ReduceLongHexSetState(Operator):
    """【不移动指针】将当前单词作为十六进制整数，执行规约操作，尝试将当前词语解析为关键词"""

    def __init__(self, state: LexicalState):
        self._state = state

    def __call__(self, fsm: LexicalFSM):
        pos = fsm.pos_start
        source = fsm.get_word()
        fsm.state = self._state
        fsm.pos_start = fsm.pos
        return IntToken(
            kind=TokenKind.LONG_HEX_LITERAL,
            pos=pos,
            end_pos=fsm.pos,
            affiliations=fsm.pop_affiliation(),
            source=source,
            value=int(source[2:-1], base=16)
        )


class ReduceFloatSetState(Operator):
    """【不移动指针】将当前单词作为单精度浮点数，执行规约操作，尝试将当前词语解析为关键词"""

    def __init__(self, state: LexicalState):
        self._state = state

    def __call__(self, fsm: LexicalFSM):
        pos = fsm.pos_start
        source = fsm.get_word()
        fsm.state = self._state
        fsm.pos_start = fsm.pos
        return FloatToken(
            kind=TokenKind.FLOAT_LITERAL,
            pos=pos,
            end_pos=fsm.pos,
            affiliations=fsm.pop_affiliation(),
            source=source, value=float(source[:-1])
        )


class ReduceDoubleSetState(Operator):
    """【不移动指针】将当前单词作为双精度浮点数，执行规约操作，尝试将当前词语解析为关键词"""

    def __init__(self, state: LexicalState):
        self._state = state

    def __call__(self, fsm: LexicalFSM):
        pos = fsm.pos_start
        source = fsm.get_word()
        fsm.state = self._state
        fsm.pos_start = fsm.pos
        value = float(source[:-1]) if source.endswith("d") or source.endswith("D") else float(source)
        return FloatToken(
            kind=TokenKind.DOUBLE_LITERAL,
            pos=pos,
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
        pos = fsm.pos_start
        source = fsm.get_word()
        fsm.state = self._state
        fsm.pos_start = fsm.pos
        kind = KEYWORD_HASH.get(source, TokenKind.IDENTIFIER)
        return Token(
            kind=kind,
            pos=pos,
            end_pos=fsm.pos,
            affiliations=fsm.pop_affiliation(),
            source=source
        )


class MoveReduceSetState(Operator):
    """【移动指针】结束规约操作"""

    def __init__(self, kind: TokenKind, state: LexicalState):
        self._kind = kind
        self._state = state

    def __call__(self, fsm: LexicalFSM):
        fsm.pos += 1
        pos = fsm.pos_start
        source = fsm.get_word()
        fsm.state = self._state
        fsm.pos_start = fsm.pos
        return Token(
            kind=self._kind,
            pos=pos,
            end_pos=fsm.pos,
            affiliations=fsm.pop_affiliation(),
            source=source
        )


class MoveReduceCharSetState(Operator):
    """【移动指针】将当前词语作为字符字面值，进行规约操作"""

    def __init__(self, state: LexicalState):
        self._state = state

    def __call__(self, fsm: LexicalFSM):
        fsm.pos += 1
        pos = fsm.pos_start
        source = fsm.get_word()
        fsm.state = self._state
        fsm.pos_start = fsm.pos
        return CharToken(
            kind=TokenKind.CHAR_LITERAL,
            pos=pos,
            end_pos=fsm.pos,
            affiliations=fsm.pop_affiliation(),
            source=source,
            value=source[1:-1]
        )


class MoveReduceStringSetState(Operator):
    """【移动指针】将当前词语作为字符串字面值，进行规约操作"""

    def __init__(self, state: LexicalState):
        self._state = state

    def __call__(self, fsm: LexicalFSM):
        fsm.pos += 1
        pos = fsm.pos_start
        source = fsm.get_word()
        fsm.state = self._state
        fsm.pos_start = fsm.pos
        return StringToken(
            kind=TokenKind.STRING_LITERAL,
            pos=pos,
            end_pos=fsm.pos,
            affiliations=fsm.pop_affiliation(),
            source=source,
            value=source[1:-1]
        )


class MoveReduceTextBlockSetState(Operator):
    """【移动指针】将当前词语作为 TextBlock，进行规约操作"""

    def __init__(self, state: LexicalState):
        self._state = state

    def __call__(self, fsm: LexicalFSM):
        fsm.pos += 1
        pos = fsm.pos_start
        source = fsm.get_word()
        fsm.state = self._state
        fsm.pos_start = fsm.pos
        return StringToken(
            kind=TokenKind.TEXT_BLOCK,
            pos=pos,
            end_pos=fsm.pos,
            affiliations=fsm.pop_affiliation(),
            source=source,
            value=source[3:-3]
        )


class CommentSetState(Operator):
    """【移动指针】将当前元素作为附属元素，进行规约操作"""

    def __init__(self, style: AffiliationStyle, state: LexicalState):
        self._style = style
        self._state = state

    def __call__(self, fsm: LexicalFSM):
        fsm.state = self._state
        pos = fsm.pos_start
        source = fsm.get_word()
        fsm.pos_start = fsm.pos
        fsm.affiliations.append(Affiliation(
            style=self._style,
            pos=pos,
            end_pos=fsm.pos,
            text=source
        ))


class MoveComment(Operator):
    """【移动指针】将当前元素作为附属元素，进行规约操作"""

    def __init__(self, style: AffiliationStyle):
        self._style = style

    def __call__(self, fsm: LexicalFSM):
        fsm.pos += 1
        pos = fsm.pos_start
        source = fsm.get_word()
        fsm.pos_start = fsm.pos
        fsm.affiliations.append(Affiliation(
            style=self._style,
            pos=pos,
            end_pos=fsm.pos,
            text=source
        ))


class MoveCommentSetState(Operator):
    """【移动指针】将当前元素作为附属元素，进行规约操作"""

    def __init__(self, style: AffiliationStyle, state: LexicalState):
        self._style = style
        self._state = state

    def __call__(self, fsm: LexicalFSM):
        fsm.pos += 1
        pos = fsm.pos_start
        source = fsm.get_word()
        fsm.state = self._state
        fsm.pos_start = fsm.pos
        fsm.affiliations.append(Affiliation(
            style=self._style,
            pos=pos,
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
        pos = fsm.pos_start
        fsm.pos_start = fsm.pos
        fsm.state = self._state
        return Token(
            kind=self._kind,
            pos=pos,
            end_pos=fsm.pos,
            affiliations=fsm.pop_affiliation(),
            source=self._source
        )


class FixedIntSetState(Operator):
    """【不移动指针】将当前单词作为整型，执行固定值规约操作"""

    def __init__(self, source: str, state: LexicalState):
        self._source = source
        self._state = state

    def __call__(self, fsm: LexicalFSM):
        pos = fsm.pos_start
        fsm.pos_start = fsm.pos
        fsm.state = self._state
        return IntToken(
            kind=TokenKind.INT_DEC_LITERAL,
            pos=pos,
            end_pos=fsm.pos,
            affiliations=fsm.pop_affiliation(),
            source=self._source,
            value=int(self._source)
        )


class MoveFixed(Operator):
    """【移动指针】结束固定操作"""

    def __init__(self, kind: TokenKind, source: str):
        self._kind = kind
        self._source = source

    def __call__(self, fsm: LexicalFSM):
        fsm.pos += 1
        pos = fsm.pos_start
        fsm.pos_start = fsm.pos
        return Token(
            kind=self._kind,
            pos=pos,
            end_pos=fsm.pos,
            affiliations=fsm.pop_affiliation(),
            source=self._source
        )


class MoveFixedSetState(Operator):
    """【移动指针】结束固定操作"""

    def __init__(self, kind: TokenKind, source: str, state: LexicalState):
        self._kind = kind
        self._source = source
        self._state = state

    def __call__(self, fsm: LexicalFSM):
        fsm.pos += 1
        pos = fsm.pos_start
        fsm.pos_start = fsm.pos
        fsm.state = self._state
        return Token(
            kind=self._kind,
            pos=pos,
            end_pos=fsm.pos,
            affiliations=fsm.pop_affiliation(),
            source=self._source
        )


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
        ":": ShiftSetState(state=LexicalState.COLON),
        ",": MoveFixed(kind=TokenKind.COMMA, source=","),
        "@": MoveFixed(kind=TokenKind.MONKEYS_AT, source="@"),
        "0": ShiftSetState(state=LexicalState.ZERO),
        frozenset({"1", "2", "3", "4", "5", "6", "7", "8", "9"}): ShiftSetState(state=LexicalState.DEC),
        "'": ShiftSetState(state=LexicalState.LIT_CHAR),
        "\"": ShiftSetState(state=LexicalState.DQ),
        "+": ShiftSetState(state=LexicalState.PLUS),
        "-": ShiftSetState(state=LexicalState.SUB),
        "*": ShiftSetState(state=LexicalState.STAR),
        "/": ShiftSetState(state=LexicalState.SLASH),
        "%": ShiftSetState(state=LexicalState.PERCENT),
        "=": ShiftSetState(state=LexicalState.EQ),
        "!": ShiftSetState(state=LexicalState.BANG),
        "<": ShiftSetState(state=LexicalState.LT),
        ">": ShiftSetState(state=LexicalState.GT),
        "&": ShiftSetState(state=LexicalState.AMP),
        "|": ShiftSetState(state=LexicalState.BAR),
        "^": ShiftSetState(state=LexicalState.CARET),
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
        frozenset({"l", "L"}): ShiftSetState(state=LexicalState.DEC_L),
        frozenset({"f", "F"}): ShiftSetState(state=LexicalState.DEC_DOT_NUM_E_NUM_F),
        frozenset({"d", "D"}): ShiftSetState(state=LexicalState.DEC_DOT_NUM_E_NUM_D),
        NUMBER: ShiftSetState(state=LexicalState.OCT),
        OPERATOR: FixedIntSetState(source="0", state=LexicalState.INIT),
        END_WORD: FixedIntSetState(source="0", state=LexicalState.INIT),
        END_CHAR: FixedIntSetState(source="0", state=LexicalState.INIT),
    },

    # 0[xX]（十六进制的前缀）
    LexicalState.ZERO_X: {
        HEX_NUMBER: ShiftSetState(state=LexicalState.HEX),
    },

    # [1-9][0-9]+（十进制数）
    LexicalState.DEC: {
        NUMBER: Shift(),
        frozenset({"l", "L"}): ShiftSetState(state=LexicalState.DEC_L),
        frozenset({"f", "f"}): ShiftSetState(state=LexicalState.DEC_DOT_NUM_E_NUM_F),
        frozenset({"d", "D"}): ShiftSetState(state=LexicalState.DEC_DOT_NUM_E_NUM_D),
        ".": ShiftSetState(state=LexicalState.DEC_DOT_NUM),
        frozenset({"e", "E"}): ShiftSetState(state=LexicalState.DEC_DOT_NUM_E),
        OPERATOR: ReduceIntSetState(state=LexicalState.INIT),
        frozenset(END_WORD - {"."}): ReduceIntSetState(state=LexicalState.INIT),
        END_CHAR: ReduceIntSetState(state=LexicalState.INIT),
    },

    # [1-9][0-9]*L（长整型字面值）
    LexicalState.DEC_L: {
        OPERATOR: ReduceLongSetState(state=LexicalState.INIT),
        END_WORD: ReduceLongSetState(state=LexicalState.INIT),
        END_CHAR: ReduceLongSetState(state=LexicalState.INIT),
    },

    # 0[0-7]+（八进制数）
    LexicalState.OCT: {
        frozenset({"l", "L"}): ShiftSetState(state=LexicalState.OCT_L),
        OCT_NUMBER: Shift(),
        OPERATOR: ReduceIntOctSetState(state=LexicalState.INIT),
        END_WORD: ReduceIntOctSetState(state=LexicalState.INIT),
        END_CHAR: ReduceIntOctSetState(state=LexicalState.INIT),
    },

    # [1-9][0-9]*L（八进制长整型）
    LexicalState.OCT_L: {
        OPERATOR: ReduceLongOctSetState(state=LexicalState.INIT),
        END_WORD: ReduceLongOctSetState(state=LexicalState.INIT),
        END_CHAR: ReduceLongOctSetState(state=LexicalState.INIT),
    },

    # 0[xX][0-9a-fA-F]+（十六进制数）
    LexicalState.HEX: {
        frozenset({"l", "L"}): ShiftSetState(state=LexicalState.HEX_L),
        HEX_NUMBER: Shift(),
        OPERATOR: ReduceIntHexSetState(state=LexicalState.INIT),
        END_WORD: ReduceIntHexSetState(state=LexicalState.INIT),
        END_CHAR: ReduceIntHexSetState(state=LexicalState.INIT)
    },

    # [1-9][0-9]*L（十六进制长整型）
    LexicalState.HEX_L: {
        OPERATOR: ReduceLongHexSetState(state=LexicalState.INIT),
        END_WORD: ReduceLongHexSetState(state=LexicalState.INIT),
        END_CHAR: ReduceLongHexSetState(state=LexicalState.INIT),
    },

    # [0-9]+\.[0-9]+（小数）
    LexicalState.DEC_DOT_NUM: {
        NUMBER: Shift(),
        frozenset({"f", "f"}): ShiftSetState(state=LexicalState.DEC_DOT_NUM_E_NUM_F),
        frozenset({"d", "D"}): ShiftSetState(state=LexicalState.DEC_DOT_NUM_E_NUM_D),
        frozenset({"e", "E"}): ShiftSetState(state=LexicalState.DEC_DOT_NUM_E),
        OPERATOR: ReduceDoubleSetState(state=LexicalState.INIT),
        END_WORD: ReduceDoubleSetState(state=LexicalState.INIT),
        END_CHAR: ReduceDoubleSetState(state=LexicalState.INIT),
    },

    # [0-9]+(\.[0-9]+)?[eE]（科学记数法的前缀）
    LexicalState.DEC_DOT_NUM_E: {
        NUMBER: ShiftSetState(state=LexicalState.DEC_DOT_NUM_E_NUM),
        "-": ShiftSetState(state=LexicalState.DEC_DOT_NUM_E_NUM),
    },

    # [0-9]+(\.[0-9]+)?[eE]-?[0-9]*（科学记数法）
    LexicalState.DEC_DOT_NUM_E_NUM: {
        NUMBER: Shift(),
        frozenset({"f", "f"}): ShiftSetState(state=LexicalState.DEC_DOT_NUM_E_NUM_F),
        frozenset({"d", "D"}): ShiftSetState(state=LexicalState.DEC_DOT_NUM_E_NUM_D),
        OPERATOR: ReduceDoubleSetState(state=LexicalState.INIT),
        END_WORD: ReduceDoubleSetState(state=LexicalState.INIT),
        END_CHAR: ReduceDoubleSetState(state=LexicalState.INIT),
    },

    # [0-9]+(\.[0-9]+)?([eE]-?[0-9]*)?[fF]（单精度浮点数字面值）
    LexicalState.DEC_DOT_NUM_E_NUM_F: {
        OPERATOR: ReduceFloatSetState(state=LexicalState.INIT),
        END_WORD: ReduceFloatSetState(state=LexicalState.INIT),
        END_CHAR: ReduceFloatSetState(state=LexicalState.INIT),
    },

    # [0-9]+(\.[0-9]+)?([eE]-?[0-9]*)?[dD]（双精度浮点数字面值）
    LexicalState.DEC_DOT_NUM_E_NUM_D: {
        OPERATOR: ReduceDoubleSetState(state=LexicalState.INIT),
        END_WORD: ReduceDoubleSetState(state=LexicalState.INIT),
        END_CHAR: ReduceDoubleSetState(state=LexicalState.INIT),
    },

    # -------------------- 字符字面值 --------------------
    # 在单引号字符串中
    LexicalState.LIT_CHAR: {
        "\\": ShiftSetState(state=LexicalState.LIT_CHAR_ESCAPE),
        "'": MoveReduceCharSetState(state=LexicalState.INIT),
        END_CHAR: Error(),
        DEFAULT: Shift(),
    },

    # 在单引号字符串中的转义符之后
    LexicalState.LIT_CHAR_ESCAPE: {
        END_CHAR: Error(),
        DEFAULT: ShiftSetState(state=LexicalState.LIT_CHAR),
    },

    # -------------------- 字符串字面值 --------------------
    # "
    LexicalState.DQ: {
        "\"": ShiftSetState(state=LexicalState.DQ_DQ),
        "\\": ShiftSetState(state=LexicalState.LIT_STRING_ESCAPE),
        END_CHAR: Error(),
        DEFAULT: ShiftSetState(state=LexicalState.LIT_STRING),
    },

    # ""
    LexicalState.DQ_DQ: {
        "\"": ShiftSetState(state=LexicalState.LIT_BLOCK),
        DEFAULT: MoveFixedSetState(kind=TokenKind.STRING_LITERAL, source="\"\"", state=LexicalState.INIT),
    },

    # 在双引号字符串中
    LexicalState.LIT_STRING: {
        "\\": ShiftSetState(state=LexicalState.LIT_STRING_ESCAPE),
        "\"": MoveReduceStringSetState(state=LexicalState.INIT),
        END_CHAR: Error(),
        DEFAULT: Shift(),
    },

    # 在双引号字符串中的转义符之后
    LexicalState.LIT_STRING_ESCAPE: {
        END_CHAR: Error(),
        DEFAULT: ShiftSetState(state=LexicalState.LIT_STRING),
    },

    # 在 TextBlock 中
    LexicalState.LIT_BLOCK: {
        "\"": ShiftSetState(state=LexicalState.LIT_BLOCK_DQ),
        "\\": ShiftSetState(state=LexicalState.LIT_BLOCK_ESCAPE),
        END_CHAR: Error(),
        DEFAULT: Shift(),
    },

    # 在 TextBlock 中的转义符之后
    LexicalState.LIT_BLOCK_ESCAPE: {
        END_CHAR: Error(),
        DEFAULT: ShiftSetState(state=LexicalState.LIT_BLOCK),
    },

    # 在 TextBlock 中的 " 之后
    LexicalState.LIT_BLOCK_DQ: {
        "\"": ShiftSetState(state=LexicalState.LIT_BLOCK_DQ_DQ),
        "\\": ShiftSetState(state=LexicalState.LIT_BLOCK_ESCAPE),
        END_CHAR: Error(),
        DEFAULT: ShiftSetState(state=LexicalState.LIT_BLOCK),
    },

    # 在 TextBlock 中的 "" 之后
    LexicalState.LIT_BLOCK_DQ_DQ: {
        "\"": MoveReduceTextBlockSetState(state=LexicalState.INIT),
        "\\": ShiftSetState(state=LexicalState.LIT_BLOCK_ESCAPE),
        END_CHAR: Error(),
        DEFAULT: ShiftSetState(state=LexicalState.LIT_BLOCK),
    },

    # -------------------- 多字符运算符 --------------------
    # +
    LexicalState.PLUS: {
        "=": MoveFixedSetState(kind=TokenKind.PLUS_EQ, source="+=", state=LexicalState.INIT),
        "+": MoveFixedSetState(kind=TokenKind.PLUS_PLUS, source="++", state=LexicalState.INIT),
        DEFAULT: FixedSetState(kind=TokenKind.PLUS, source="+", state=LexicalState.INIT),
    },

    # -
    LexicalState.SUB: {
        ">": MoveFixedSetState(kind=TokenKind.ARROW, source="->", state=LexicalState.INIT),
        "=": MoveFixedSetState(kind=TokenKind.SUB_EQ, source="-=", state=LexicalState.INIT),
        "-": MoveFixedSetState(kind=TokenKind.SUB_SUB, source="--", state=LexicalState.INIT),
        DEFAULT: FixedSetState(kind=TokenKind.SUB, source="-", state=LexicalState.INIT),
    },

    # *
    LexicalState.STAR: {
        "=": MoveFixedSetState(kind=TokenKind.STAR_EQ, source="*=", state=LexicalState.INIT),
        DEFAULT: FixedSetState(kind=TokenKind.STAR, source="*", state=LexicalState.INIT),
    },

    # /
    LexicalState.SLASH: {
        "=": MoveFixedSetState(kind=TokenKind.SLASH_EQ, source="/=", state=LexicalState.INIT),
        "/": ShiftSetState(state=LexicalState.IN_LINE_COMMENT),
        "*": ShiftSetState(state=LexicalState.IN_MULTI_COMMENT),
        DEFAULT: FixedSetState(kind=TokenKind.SLASH, source="/", state=LexicalState.INIT),
    },

    # %
    LexicalState.PERCENT: {
        "=": MoveFixedSetState(kind=TokenKind.PERCENT_EQ, source="%=", state=LexicalState.INIT),
        DEFAULT: FixedSetState(kind=TokenKind.PERCENT, source="%", state=LexicalState.INIT),
    },

    # =
    LexicalState.EQ: {
        "=": MoveFixedSetState(kind=TokenKind.EQ_EQ, source="==", state=LexicalState.INIT),
        DEFAULT: FixedSetState(kind=TokenKind.EQ, source="=", state=LexicalState.INIT),
    },

    # !
    LexicalState.BANG: {
        "=": MoveFixedSetState(kind=TokenKind.BANG_EQ, source="!=", state=LexicalState.INIT),
        DEFAULT: FixedSetState(kind=TokenKind.BANG, source="!", state=LexicalState.INIT),
    },

    # <
    LexicalState.LT: {
        "<": ShiftSetState(state=LexicalState.LT_LT),
        "=": MoveFixedSetState(kind=TokenKind.LT_EQ, source="<=", state=LexicalState.INIT),
        DEFAULT: FixedSetState(kind=TokenKind.LT, source="<", state=LexicalState.INIT)
    },

    # <<
    LexicalState.LT_LT: {
        "=": MoveFixedSetState(kind=TokenKind.LT_LT_EQ, source="<<=", state=LexicalState.INIT),
        DEFAULT: FixedSetState(kind=TokenKind.LT_LT, source="<<", state=LexicalState.INIT),
    },

    # >
    LexicalState.GT: {
        ">": ShiftSetState(state=LexicalState.GT_GT),
        "=": MoveFixedSetState(kind=TokenKind.GT_EQ, source=">=", state=LexicalState.INIT),
        DEFAULT: FixedSetState(kind=TokenKind.GT, source=">", state=LexicalState.INIT)
    },

    # >>
    LexicalState.GT_GT: {
        ">": ShiftSetState(state=LexicalState.GT_GT_GT),
        "=": MoveFixedSetState(kind=TokenKind.GT_GT_EQ, source=">>=", state=LexicalState.INIT),
        DEFAULT: FixedSetState(kind=TokenKind.GT_GT, source=">>", state=LexicalState.INIT),
    },

    # >>>
    LexicalState.GT_GT_GT: {
        "=": MoveFixedSetState(kind=TokenKind.GT_GT_GT_EQ, source=">>>=", state=LexicalState.INIT),
        DEFAULT: FixedSetState(kind=TokenKind.GT_GT_GT, source=">>>", state=LexicalState.INIT),
    },

    # &
    LexicalState.AMP: {
        "&": MoveFixedSetState(kind=TokenKind.AMP_AMP, source="&&", state=LexicalState.INIT),
        "=": MoveFixedSetState(kind=TokenKind.AMP_EQ, source="&=", state=LexicalState.INIT),
        DEFAULT: FixedSetState(kind=TokenKind.AMP, source="&", state=LexicalState.INIT),
    },

    # |
    LexicalState.BAR: {
        "|": MoveFixedSetState(kind=TokenKind.BAR_BAR, source="||", state=LexicalState.INIT),
        "=": MoveFixedSetState(kind=TokenKind.BAR_EQ, source="|=", state=LexicalState.INIT),
        DEFAULT: FixedSetState(kind=TokenKind.BAR, source="|", state=LexicalState.INIT),
    },

    # ^
    LexicalState.CARET: {
        "=": MoveFixedSetState(kind=TokenKind.CARET_EQ, source="^=", state=LexicalState.INIT),
        DEFAULT: FixedSetState(kind=TokenKind.CARET, source="^", state=LexicalState.INIT),
    },

    # :
    LexicalState.COLON: {
        "：": MoveFixedSetState(kind=TokenKind.COL_COL, source="::", state=LexicalState.INIT),
        DEFAULT: FixedSetState(kind=TokenKind.COLON, source=":", state=LexicalState.INIT),
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
        "/": MoveCommentSetState(style=AffiliationStyle.COMMENT_BLOCK, state=LexicalState.INIT),
        END_CHAR: Error(),
        DEFAULT: ShiftSetState(state=LexicalState.IN_MULTI_COMMENT),
    },

    # -------------------- 特殊场景 --------------------
    # .
    LexicalState.DOT: {
        ".": ShiftSetState(state=LexicalState.DOT_DOT),
        NUMBER: ShiftSetState(state=LexicalState.DEC_DOT_NUM),  # 当下一个字符是数字时，为浮点数
        DEFAULT: FixedSetState(kind=TokenKind.DOT, source=".", state=LexicalState.INIT),  # 当下一个字符不是数字时，为类名或方法名
    },

    # ..
    LexicalState.DOT_DOT: {
        ".": MoveFixedSetState(kind=TokenKind.ELLIPSIS, source="...", state=LexicalState.INIT),  # 当下一个字符是数字时，为浮点数
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
    lexical_fsm = LexicalFSM("int[] ident = List.of(3)")
    token_list = []
    while token := lexical_fsm.lex():
        print("token:", token, token.pos, token.end_pos)
        if token.kind == TokenKind.EOF:
            break

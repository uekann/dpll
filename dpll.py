from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Value(Enum):
    """True, False, Undefinedを表す列挙型"""

    UD = 0
    T = 1
    F = 2

    def __str__(self) -> str:
        # 文字列化
        if self == Value.UD:
            return "UNDEFINED"
        elif self == Value.T:
            return "TRUE"
        elif self == Value.F:
            return "FALSE"
        else:
            raise ValueError("Value must be UNDEFINED, TRUE or FALSE")

    def __invert__(self) -> Value:
        """否定(True -> False, False -> True, Undefined -> Undefined)"""
        if self == Value.UD:
            return Value.UD
        elif self == Value.T:
            return Value.F
        elif self == Value.F:
            return Value.T
        else:
            raise ValueError("Value must be UNDEFINED, TRUE or FALSE")


class CNF:
    """Conjunctive Normal Form(ANDの連言標準形)を表すクラス"""

    def __init__(self, s: Optional[Section] = None) -> None:
        self.l: list[Section] = []
        if s:
            self.l.append(s)

    def __mul__(self, other) -> CNF:
        """CNF同士の結合"""
        c = CNF()
        c.l = self.l + other.l
        return c

    def __str__(self) -> str:
        return " * ".join(map(str, self.l))

    def __repr__(self) -> str:
        return str(self)

    def evaluate(self) -> Value:
        """CNFの真偽値を返す"""
        flag = False
        for s in self.l:
            if s.evaluate() == Value.F:
                return Value.F
            elif s.evaluate() == Value.UD:
                flag = True
        return Value.UD if flag else Value.T

    def solve(self) -> int:
        """CNFが真になるような変数の割り当てを探索する"""
        if self.evaluate() != Value.UD:
            return 1 if self.evaluate() == Value.T else -1

        s = sorted(
            list(filter(lambda x: x.evaluate() == Value.UD, self.l)),
            key=lambda x: x._countUD(),
        )[0]
        vws = s._getUD()
        assert vws is not None
        vws.var.set_value(Value.F)
        if self.solve() == 1:
            return 1
        vws.var.set_value(Value.T)
        ret = self.solve()
        if ret == -1:
            vws.var.set_value(Value.UD)
        return ret

    def solve_nonrecursive(self) -> int:
        """再帰せずにCNFが真になるような変数の割り当てを探索する"""
        if self.evaluate() != Value.UD:
            return 1 if self.evaluate() == Value.T else -1

        # 決め打った変数を格納するスタック
        stack: list[tuple[Variable, Value]] = []

        while True:
            e = self.evaluate()
            if e == Value.F:

                while True:
                    if not stack:
                        # スタックが空(変更できる決めうちが存在しない)なら終了
                        return -1

                    # 最後に決め打った変数を取り出す
                    var, val = stack.pop()
                    if val == Value.F:
                        # 決め打った変数がFalseなら、その変数をTrueに変更し、再度探索
                        var.set_value(Value.T)
                        stack.append((var, Value.T))
                        break
                    else:
                        # 決め打った変数がTrueなら、その変数を未定に変更し、Falseと決め打った変数を探す
                        var.set_value(Value.UD)
                continue
            elif e == Value.UD:
                # 真偽値が未定な場合、未定の変数を一つ決め打つ

                # 真偽値が未定のSectionを取得
                s = sorted(
                    list(filter(lambda x: x.evaluate() == Value.UD, self.l)),
                    key=lambda x: x._countUD(),
                )[0]

                # 真偽値が未定なSecitonから未定の変数を一つ取得
                vws = s._getUD()
                assert vws is not None

                # 真偽値を決め打ち、スタックに積む
                vws.var.set_value(Value.F)
                stack.append((vws.var, Value.F))
                continue
            else:
                # e == Value.Tなら終了
                return 1


class Section(CNF):
    """節を表すクラス"""

    @dataclass
    class VariableWithSign:
        """符号付き変数を表すクラス.
        SectionはVariableWithSignの集合として表現される."""

        var: Variable
        sign: bool = True

        def __str__(self) -> str:
            return f"(~{str(self.var)})" if not self.sign else str(self.var)

        def __eq__(self, __value: object) -> bool:
            """同値性の判定.
            変数が同一オブジェクトかつ符号が一致している場合にTrueを返す."""

            if isinstance(__value, Section.VariableWithSign):
                return self.var is __value.var and self.sign == __value.sign
            return False

        def __hash__(self) -> int:
            return hash((self.var, self.sign))

        def evaluate(self) -> Value:
            """真偽値を返す"""
            return self.var.value if self.sign else ~self.var.value

    def __init__(self, v: Optional[Section.VariableWithSign] = None) -> None:
        super().__init__()
        self.l: list[Section] = [self]
        self.set: set[Section.VariableWithSign] = set()
        if v:
            self.set.add(v)

    def __add__(self, other) -> Section:
        """Section同士の結合"""
        s = Section()
        s.set = self.set.union(other.set)
        return s

    def __str__(self) -> str:
        return "(" + " + ".join(map(str, self.set)) + ")"

    def evaluate(self) -> Value:
        """真偽値を返す"""
        if len(self.set) == 0:
            return Value.T
        else:
            flag = False
            for vws in self.set:
                if vws.evaluate() == Value.T:
                    return Value.T

                if vws.evaluate() == Value.UD:
                    flag = True

            return Value.UD if flag else Value.F

    def _countUD(self) -> int:
        """Section内の未定義の変数の数を返す"""
        count = 0
        for vws in self.set:
            if vws.evaluate() == Value.UD:
                count += 1
        return count

    def _getUD(self) -> Optional[Section.VariableWithSign]:
        """未定義の変数を一つ返す"""
        for vws in self.set:
            if vws.evaluate() == Value.UD:
                return vws
        return None


class Variable(Section):
    """変数を表すクラス"""

    def __init__(self, name:str):
        super().__init__()
        self.l: list[Section] = [self]
        vws = Section.VariableWithSign(self)
        self.set: set[Section.VariableWithSign] = {vws}
        self.name: str = name
        self.value: Value = Value.UD

    def __str__(self) -> str:
        return self.name

    def __invert__(self) -> Section:
        s = Section()
        s.set.add(Section.VariableWithSign(self, False))
        return s

    def set_value(self, value: Value) -> None:
        """値の設定"""
        if not isinstance(value, Value):
            raise ValueError(
                "Value must be UNDEFINED, TRUE or FALSE, but got " + str(value)
            )
        self.value = value


if __name__ == "__main__":
    a = Variable("a")
    b = Variable("b")
    c = Variable("c")
    d = Variable("d")

    cnf = (a + b) * (~a + ~b) * (c + d) * (~c + d) * ~d
    print(cnf)
    print(cnf.solve())
    print(f"{a}: {a.value}\n{b}: {b.value}\n{c}: {c.value}\n{d}: {d.value}")
    # print(cnf.solve())
    # print(f"{a}: {a.value}\n{b}: {b.value}\n{c}: {c.value}\n{d}: {d.value}")

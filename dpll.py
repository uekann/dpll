from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


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

    def __init__(self, s: Section = None) -> None:
        self.l = []
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

        stack = []
        while True:
            e = self.evaluate()
            if e == Value.F:
                while True:
                    if not stack:
                        return -1
                    v, val = stack.pop()
                    if val == Value.F:
                        v.set_value(Value.T)
                        stack.append((v, Value.T))
                        break
                    else:
                        v.set_value(Value.UD)
                continue
            elif e == Value.UD:
                s = sorted(
                    list(filter(lambda x: x.evaluate() == Value.UD, self.l)),
                    key=lambda x: x._countUD(),
                )[0]
                vws = s._getUD()
                vws.var.set_value(Value.F)
                stack.append((vws.var, Value.F))
                continue
            else:
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

    def __init__(self, v: Variable = None) -> None:
        super().__init__()
        self.l = [self]
        self.set = set()
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

    def _getUD(self) -> Section.VariableWithSign:
        """未定義の変数を一つ返す"""
        for vws in self.set:
            if vws.evaluate() == Value.UD:
                return vws
        return None


class Variable(Section):
    """変数を表すクラス"""

    def __init__(self, name):
        super().__init__()
        self.l = [self]
        vws = Section.VariableWithSign(self)
        self.set = {vws}
        self.name = name
        self.value = Value.UD

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

    cnf = (a + b) * (~a + ~b) * (c + d) * (~c + d)
    print(cnf)
    print(cnf.solve_nonrecursive())
    print(f"{a}: {a.value}\n{b}: {b.value}\n{c}: {c.value}\n{d}: {d.value}")
    # print(cnf.solve())
    # print(f"{a}: {a.value}\n{b}: {b.value}\n{c}: {c.value}\n{d}: {d.value}")

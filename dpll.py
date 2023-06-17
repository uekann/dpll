from __future__ import annotations

from dataclasses import dataclass


class CNF:
    def __init__(self, s: Section = None) -> None:
        self.l = []
        if s:
            self.l.append(s)

    def __mul__(self, other) -> CNF:

        c = CNF()
        c.l = self.l + other.l
        return c

    def __str__(self) -> str:
        return " * ".join(map(str, self.l))

    def __repr__(self) -> str:
        return str(self)


class Section(CNF):
    @dataclass
    class VariableWithSign:
        var: Variable
        sign: bool = True

        def __str__(self) -> str:
            return f"(-{str(self.var)})" if not self.sign else str(self.var)

        def __eq__(self, __value: object) -> bool:
            if isinstance(__value, Section.VariableWithSign):
                return self.var is __value.var and self.sign == __value.sign
            return False

        def __hash__(self) -> int:
            return hash((self.var, self.sign))

    def __init__(self, v: Variable = None) -> None:
        super().__init__()
        self.l = [self]
        self.set = set()
        if v:
            self.set.add(v)

    def __add__(self, other) -> Section:
        s = Section()
        s.set = self.set.union(other.set)
        return s

    def __str__(self) -> str:
        return "(" + " + ".join(map(str, self.set)) + ")"


class Variable(Section):
    def __init__(self, name):
        super().__init__()
        self.l = [self]
        vws = Section.VariableWithSign(self)
        self.set = {vws}
        self.name = name

    def __str__(self) -> str:
        return self.name

    def __neg__(self) -> Section.VariableWithSign:
        s = Section()
        s.set.add(Section.VariableWithSign(self, False))
        return s

    # def _set(self, value):


if __name__ == "__main__":
    a = Variable("a")
    b = Variable("b")
    c = Variable("c")

    print((a + (-b)) * c * (b + c))

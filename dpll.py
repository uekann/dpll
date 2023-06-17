from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Value(Enum):
    UD = 0
    T = 1
    F = 2

    def __str__(self) -> str:
        if self == Value.UD:
            return "UNDEFINED"
        elif self == Value.T:
            return "TRUE"
        elif self == Value.F:
            return "FALSE"
        else:
            raise ValueError("Value must be UNDEFINED, TRUE or FALSE")

    def __invert__(self) -> Value:
        if self == Value.UD:
            return Value.UD
        elif self == Value.T:
            return Value.F
        elif self == Value.F:
            return Value.T
        else:
            raise ValueError("Value must be UNDEFINED, TRUE or FALSE")


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
            return f"(~{str(self.var)})" if not self.sign else str(self.var)

        def __eq__(self, __value: object) -> bool:
            if isinstance(__value, Section.VariableWithSign):
                return self.var is __value.var and self.sign == __value.sign
            return False

        def __hash__(self) -> int:
            return hash((self.var, self.sign))

        def evaluate(self) -> Value:
            return self.var.value if self.sign else ~self.var.value

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

    def evaluate(self) -> Value:
        if len(self.set) == 0:
            return Value.T
        else:
            for vws in self.set:
                flag = False
                if vws.evaluate() == Value.T:
                    return Value.T

                if vws.evaluate() == Value.UD:
                    flag = True

            return Value.UD if flag else Value.F


class Variable(Section):
    def __init__(self, name):
        super().__init__()
        self.l = [self]
        vws = Section.VariableWithSign(self)
        self.set = {vws}
        self.name = name
        self.value = Value.UD

    def __str__(self) -> str:
        return self.name

    def __invert__(self) -> Section.VariableWithSign:
        s = Section()
        s.set.add(Section.VariableWithSign(self, False))
        return s

    def _set_value(self, value: Value):
        if not isinstance(value, Value):
            raise ValueError(
                "Value must be UNDEFINED, TRUE or FALSE, but got " + str(value)
            )
        self.value = value


if __name__ == "__main__":
    a = Variable("a")
    b = Variable("b")
    c = Variable("c")

    print((a + (~b)) * c * (b + c))

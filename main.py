from dpll import CNF, Section, Variable

a = Variable("a")
b = Variable("b")
c = Variable("c")

print((a + a + (~a) + (~b)) * c * (b + c))  # (a + (~b)) * c * (b + c)

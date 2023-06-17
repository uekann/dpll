from dpll import CNF, Section, Value, Variable

sudoku = [[0, 0, 0, 4], [0, 0, 1, 2], [0, 0, 4, 3], [4, 3, 2, 1]]

v = [[[Variable(f"{i}_{j}_{k}") for k in range(4)] for j in range(4)] for i in range(4)]
cnf = CNF()
for i in range(4):
    for j in range(4):
        cnf *= v[i][j][0] + v[i][j][1] + v[i][j][2] + v[i][j][3]
        cnf *= ~v[i][j][0] + ~v[i][j][1]
        cnf *= ~v[i][j][0] + ~v[i][j][2]
        cnf *= ~v[i][j][0] + ~v[i][j][3]
        cnf *= ~v[i][j][1] + ~v[i][j][2]
        cnf *= ~v[i][j][1] + ~v[i][j][3]
        cnf *= ~v[i][j][2] + ~v[i][j][3]

for k in range(4):
    for i in range(4):
        cnf *= v[i][0][k] + v[i][1][k] + v[i][2][k] + v[i][3][k]
    for j in range(4):
        cnf *= v[0][j][k] + v[1][j][k] + v[2][j][k] + v[3][j][k]

    for i, j in [(0, 0), (0, 2), (2, 0), (2, 2)]:
        cnf *= (
            v[i + 0][j + 0][k]
            + v[i + 0][j + 1][k]
            + v[i + 1][j + 0][k]
            + v[i + 1][j + 1][k]
        )

for i in range(4):
    for j in range(4):
        if sudoku[i][j]:
            cnf *= v[i][j][sudoku[i][j] - 1]

print(cnf.solve())

for i in range(4):
    for j in range(4):
        for k in range(4):
            if v[i][j][k].value == Value.T:
                sudoku[i][j] = k + 1

print(*sudoku, sep="\n")

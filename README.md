# DPLLを用いたSATソルバー

授業で扱ったDPLLのアルゴリズムについて興味を持ったので実装しました。

## クイックスタート
```python
from dpll import Variable

a = Variable("a")
b = Variable("b")
c = Variable("c")
d = Variable("d")

cnf = (a + b) * (~a + ~b) * (c + d) * (~c + d)

print(cnf)  # (b + a) * ((~a) + (~b)) * (d + c) * (d + (~c))
print(cnf.solve())  # 1
print(f"a:{a.value}\nb:{b.value}\nc:{c.value}\nd:{d.value}")
# a:FALSE
# b:TRUE
# c:FALSE
# d:TRUE
```

## 使い方
### Value
真偽値を表す列挙型です。
以下の三つの値を持ちます。
```python
Value.T
Value.F
Value.UD
```
`~`をつけることで反転できます。
```python
~Value.T == Value.F
~Value.F == Value.T
~Value.UD == Value.UD
```
以下のように表示されます。
```python
print(Value.T) # TRUE
print(Value.F) # FALSE
print(Value.UD) # UNDEFIND
```
### Variable
変数を表すクラスです。
```python
a = Variable("a")
```
のように、内部で保持される変数名を渡すことでインスタンスを生成できます。
インスタンスは、名前と真偽値を保持しています。
```python
a.name # a
a.value # Value.UD
```
`set_value`メソッドを使うことで真偽値を設定できます。
```python
a.set_value(Value.T)
print(a.value) # TRUE
```
`~`をつけることで、反転を節として返します。

### Section
節を表すクラスです。
(誤訳らしい、正しくはclauseだった気がする。ちなみに真偽値が割り当てられていないことをUndefindとしてるのもおかしい気がする。)
```python
s = Section()
```
このようにインスタンスを生成できます。
節同士は足すことができ、また、変数も節として解釈できるので、以下のようにして生成することもできます。
```python
a = Variable("a")
b = Variable("c")
s = a + b
```
また、変数に`~`をつけても生成されます。
```python
s = ~a
```
足された結果、変数が同符号で重複している場合は省略されます。
```python
s = a + a + (~a) + b + (~b) + (~b)
print(s) # ((~a) + (~b) + b + a)
```
(順序を保持していないため、printした際、順番は前後する場合があります。)

### CNF
連語標準形(Conjunctive Normal Form)を表すクラスです。
セクション同様、
```python
cnf = CNF()
```
コンストラクタを用いてインスタを生成できます。
CNF同士はかける(論理積をとる)ことができ、節もCNFとして解釈できるので、以下のようにして生成することもできます。
```python
a = Variable("a")
b = Variable("b")
c = Variable("c")
d = Variable("d")
cnf = (a + b) * (c + ~d)
```
また、変数そのものや、変数の否定ともかけることができます。
```python
cnf = a * ~b * (c + d)
```
`solve`メソッドを使うことで、CNFを真にするような真偽値の割り当てを探索します。
```python
cnf = (a + b) * (~a + ~b) * (c + d) * (~c + d)
cnf.solve()
```
`solve`メソッドは探索が成功した時に`1`、失敗した時に`-1`を返します。
`solve`メソッドを使用したのちに、`変数.value`とすることで割り当てを確認できます。
失敗した場合解決前の状態(通常は`Value.UD`)です。
また、`solve`はそれ以前に`変数.set_value()`によって設定された変数を書き換えずに探索を行います。

非再帰版の`solve_nonrecursive`も提供しています。(こちらの使用を推奨)

`main.py`ではこれらを用いた数独の求解を行なっています。
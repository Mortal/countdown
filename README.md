# The Numbers round in Countdown

See e.g. [Wikipedia](https://en.wikipedia.org/wiki/Countdown_%28game_show%29#Numbers_round).

["It wasn't easy, but I found three ways."](https://youtu.be/dFhknK3PBO0?t=1360)

```
$ python3 numbers.py 25 50 10 7 7 6 931
931 == (25 - 6) * 7 * 7
931 == (50 - (25 + 6)) * 7 * 7
931 == (25 * 6 - (10 + 7)) * 7
931 == (7 * 7 - 10) * 25 + 6 - 50
931 == ((25 - 10) * 6 + 50 - 7) * 7
931 == ((50 + 6) * 25 / 10 - 7) * 7
931 == ((25 - 6) * 10 - (50 + 7)) * 7
931 == ((50 - 25) * 6 - (10 + 7)) * 7
```

## Some maths notes

General abstract grammar:

```
expr ::= leaf | expr "+" expr | expr "-" expr | expr "*" expr | expr "/" expr
```

Number of different expression trees:

```
counts = [0, 1]
for i in range(len(counts), 7):
	c = 0
	for left_size in range(1, i):
		right_size = i - left_size
		c += 4 * counts[left_size] * counts[right_size]
	counts.append(c)
from math import factorial as fac
print([c * fac(i) for i, c in enumerate(counts)])
```

`[0, 1, 8, 192, 7680, 430080, 30965760]`

We can eliminate minus-under-plus/minus using the following rewritings:

```
(a - b) - c = a - (b + c)
a - (b - c) = (a + c) - b
(a - b) + c = (a + c) - b
a + (b - c) = (a + b) - c
```

We can eliminate divide-under-times/divide using the following rewritings:

```
(a / b) / c = a / (b * c)
a / (b / c) = (a * c) / b
(a / b) * c = (a * c) / b
a * (b / c) = (a * b) / c
```

These rewritings lead to the following normal-form abstract grammar:

```
m ::= pdt "-" pdt
pdt ::= leaf | p | d | t
p ::= pdt "+" dt
dt ::= leaf | d | t
d ::= mpt "/" mpt
mpt ::= leaf | m | p | t
t ::= mpt "*" mp
mp ::= leaf | m | p
```

Because of the symmetry of plus and times, we can further require that the children in `p` and `t` are ordered, e.g. lexicographically in their leaf sets.

Number of different expressions:

```
from math import factorial as fac
m = [0, 0]; p = [0, 0]; d = [0, 0]; t = [0, 0]; leaf = [0, 1]
dt = lambda i: d[i] + t[i] + leaf[i]
pdt = lambda i: p[i] + dt(i)
mp = lambda i: m[i] + p[i] + leaf[i]
mpt = lambda i: mp(i) + t[i]
count = lambda i: m[i] + p[i] + d[i] + t[i] + leaf[i]
for i in range(len(m), 7):
	m.append(0); p.append(0); d.append(0); t.append(0); leaf.append(0)
	for left in range(1, i):
		right = i - left
		splits = fac(i) // (fac(left) * fac(right))
		ordered_splits = fac(i-1) // (fac(left-1) * fac(right))
		m[i] += pdt(left) * pdt(right) * splits
		p[i] += pdt(left) * dt(right) * ordered_splits
		d[i] += mpt(left) * mpt(right) * splits
		t[i] += mpt(left) * mp(right) * ordered_splits
print([count(i) for i in range(len(m))])
```

`[0, 1, 6, 70, 1346, 36178, 1249590]`

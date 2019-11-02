import argparse
import itertools
import random
import re
import time
from typing import Iterable, List, Set, Tuple


def splits(bitmask: int) -> Iterable[Tuple[int, int]]:
    if not bitmask:
        return
    lsb = bitmask & -bitmask
    rest = bitmask - lsb
    yield lsb, rest
    yield rest, lsb
    if rest != rest & -rest:
        for x, y in splits(rest):
            yield x + lsb, y
            yield x, y + lsb


def subsets(bitmask: int) -> Iterable[int]:
    lsb = bitmask & -bitmask
    if lsb == bitmask:
        yield 0
        yield bitmask
    else:
        for x in subsets(bitmask - lsb):
            yield x
            yield x + lsb


def non_singleton_splits(bitmask: int) -> Iterable[Tuple[int, ...]]:
    def visit(b: int, a: int) -> Iterable[Tuple[int, ...]]:
        lsb = b & -b
        if lsb == b:
            if a:
                yield (a + b,)
        else:
            yield from visit(b - lsb, a + lsb)
            if a:
                for xs in visit(b - lsb, 0):
                    yield (a + lsb, *xs)

    return visit(bitmask, 0)


def ordered_splits(bitmask: int) -> Iterable[Tuple[int, ...]]:
    if bitmask == bitmask & -bitmask:
        return
    for singletons in subsets(bitmask):
        a: Tuple[int, ...] = ()
        r = singletons
        while r:
            s = r & -r
            a += (s,)
            r -= s
        if bitmask == singletons:
            yield a
        for xs in non_singleton_splits(bitmask - singletons):
            y = xs + a
            if len(y) > 1:
                yield y


def prod(xs):
    r = 1
    for x in xs:
        r *= x
    return r


class Numbers:
    def __init__(self, xs: List[int], space: List[Set[int]]) -> None:
        self.xs = xs
        self.space = space

    def m(self, bitmask: int, value: int) -> Iterable[str]:
        for left, right in splits(bitmask):
            for x in self.space[left]:
                for y in self.space[right]:
                    if x - y != value:
                        continue
                    for x_s in self.pdt(left, x):
                        for y_s in self.dt(right, y):
                            yield f"{x_s} - {y_s}"
                        for y_s in self.p(right, y):
                            yield f"{x_s} - ({y_s})"

    def p(self, bitmask: int, value: int) -> Iterable[str]:
        for bitmasks in ordered_splits(bitmask):
            assert len(bitmasks) > 1
            spaces = (self.space[b] for b in bitmasks)
            for values in itertools.product(*spaces):
                if sum(values) != value:
                    continue
                ways = (self.dt(b, v) for b, v in zip(bitmasks, values))
                for way in itertools.product(*ways):
                    yield " + ".join(way)

    def d(self, bitmask: int, value: int) -> Iterable[str]:
        for left, right in splits(bitmask):
            for x in self.space[left]:
                for y in self.space[right]:
                    if x / y != value:
                        continue
                    for x_s in self.mpt(left, x):
                        for y_s in self.mp(right, y):
                            yield f"{x_s} / {y_s}"
                        for y_s in self.t(right, y):
                            yield f"{x_s} / ({y_s})"

    def t(self, bitmask: int, value: int) -> Iterable[str]:
        for bitmasks in ordered_splits(bitmask):
            assert len(bitmasks) > 1
            spaces = (self.space[b] for b in bitmasks)
            for values in itertools.product(*spaces):
                if prod(values) != value:
                    continue
                ways = (self.mp(b, v) for b, v in zip(bitmasks, values))
                for way in itertools.product(*ways):
                    yield " * ".join(way)

    def leaf(self, bitmask: int, value: int) -> Iterable[str]:
        if bitmask == bitmask & -bitmask and self.space[bitmask] == {value}:
            yield str(value)

    def mp(self, bitmask: int, value: int) -> Iterable[str]:
        yield from self.leaf(bitmask, value)
        for e in self.p(bitmask, value):
            yield f"({e})"
        for e in self.m(bitmask, value):
            yield f"({e})"

    def mpt(self, bitmask: int, value: int) -> Iterable[str]:
        yield from self.mp(bitmask, value)
        yield from self.t(bitmask, value)

    def dt(self, bitmask: int, value: int) -> Iterable[str]:
        yield from self.leaf(bitmask, value)
        yield from self.t(bitmask, value)
        yield from self.d(bitmask, value)

    def pdt(self, bitmask: int, value: int) -> Iterable[str]:
        yield from self.p(bitmask, value)
        yield from self.dt(bitmask, value)

    def mpdt(self, bitmask: int, value: int) -> Iterable[str]:
        yield from self.leaf(bitmask, value)
        yield from self.p(bitmask, value)
        yield from self.m(bitmask, value)
        yield from self.t(bitmask, value)
        yield from self.d(bitmask, value)

    def backtrack(self, target: int) -> Iterable[str]:
        bits = [2 ** i for i in range(len(self.xs))]
        seen: Set[str] = set()
        for k in range(1, len(self.xs) + 1):
            for subset in itertools.combinations(bits, k):
                for l in self.mpdt(sum(subset), target):
                    claim = f"{target} == {l}"
                    if claim in seen:
                        # The only way we should see duplicates here
                        # is if there are duplicates in the input.
                        continue
                    seen.add(claim)
                    yield claim
                    assert eval(claim), claim


def numbers(xs: List[int]) -> Numbers:
    n = len(xs)
    result: List[Set[int]] = [set()]
    for bitmask in range(1, 2 ** n):
        lsb = bitmask & -bitmask
        if bitmask == lsb:
            result.append({xs[lsb.bit_length() - 1]})
            continue
        res: Set[int] = set()
        result.append(res)
        for left, right in splits(bitmask):
            for x in result[left]:
                for y in result[right]:
                    res.add(x + y)
                    res.add(x * y)
                    if x > y:
                        res.add(x - y)
                    q, r = divmod(x, y)
                    if not r:
                        res.add(q)
    return Numbers(list(xs), result)


parser = argparse.ArgumentParser()
parser.add_argument("numbers", type=int, nargs="*")


tests = ["37 == 6 * 7 - 5", "505 == (4 / 4 + 100) * 50 / 10"]


def run_tests() -> None:
    for t in tests:
        target, *xs = list(map(int, re.findall(r"\d+", t)))
        xs.sort()
        res = numbers(xs)
        if t not in res.backtrack(target):
            print("TEST FAILED: Couldn't compute %s" % t)


def main() -> None:
    assert (1, 6) in splits(7), list(splits(7))
    assert (1, 2) in ordered_splits(3)
    assert (6, 1) in ordered_splits(7)
    run_tests()
    args = parser.parse_args()
    if not args.numbers:
        big_ones = [25, 50, 75, 100]
        small_ones = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] * 2
        targets = range(100, 1000)
        nbig = [2, 2, 2, 2, 1, 1, 0]
        trials = 100
        t4 = t5 = 0.0
        for _ in range(trials):
            n = random.choice(nbig)
            xs = random.sample(big_ones, n) + random.sample(small_ones, 6 - n)
            target = random.choice(targets)
            t1 = time.time()
            res = numbers(xs)
            t2 = time.time()
            try:
                r = next(iter(res.backtrack(target)))
                t3 = time.time()
                print(r)
            except StopIteration:
                t3 = time.time()
                print("Not possible!", target, xs)
            t4 += t2 - t1
            t5 += t3 - t2
        print(t4 / trials, t5 / trials)
        return

    *xs, target = args.numbers
    res = numbers(xs)
    for r in res.backtrack(target):
        print(r)


if __name__ == "__main__":
    main()

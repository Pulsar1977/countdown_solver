#!/usr/bin/env python3

"""
    A code to solve the mathematical puzzles of the game show Countdown.

    Input (on the command line): a target number and 6 (smaller) numbers.

    The goal is to obtain a result as close to the target as possible, by
    performing arithmetic operations (+, -, x, /) on the 6 numbers
    (not all need to be used). The numbers and operations can be chosen in
    any order, but at each stage the intermediary result has to be a
    positive integer.

    Output: all results closest to the target. Results with fewer numbers
    are listed first. The results are unique (but some can be equivalent
    if associativity is taken into account).

    Requires Python 3.6 or higher.
"""

import sys
from itertools import combinations, product, zip_longest
from functools import lru_cache

assert sys.version_info >= (3, 6)


class Solutions:
    """
        This class creates all valid arithmetic operations between numbers
        out of a given tuple.
        Input: a tuple of numbers of length n.
        Output: a dictionary, where the keys are all unique combinations of
        numbers of lengths 1 to n, and the values are the corresponding
        instances of class Group.
        The method walk() iterates over all calculations.
    """
    def __init__(self, numbers):
        self.all_numbers = numbers
        self.size = len(numbers)
        self.all_groups = self.unique_groups()

    def unique_groups(self):
        all_groups = {}
        all_numbers, size = self.all_numbers, self.size
        for m in range(1, size+1):
            for numbers in combinations(all_numbers, m):
                if numbers in all_groups:
                    continue
                all_groups[numbers] = Group(numbers, all_groups)
        return all_groups

    def walk(self):
        for group in self.all_groups.values():
            yield from group.calculations


class Group:
    """
        Creates a hierarchical tree of groups from a given tuple of numbers.
        Input: a tuple of numbers and a dictionary of (smaller) groups that
        have already been created.
        A group is partitioned into all unique unordered pairs of subgroups.
        For example: (4, 2, 1, 1) -> [(4, 2, 1) + (1), (4, 1, 1) + (2),
        (2, 1, 1) + (4), (4, 2) + (1, 1), (4, 1) + (2, 1)].
        The list of calculations is created by combining the existing
        calculations between each pair of subgroups.
        The calculation of a group (n, ) of length 1 is simply the singleton [n].
    """
    def __init__(self, numbers, all_groups):
        self.numbers = numbers
        self.size = len(numbers)
        self.partitions = list(self.partition_into_unique_pairs(all_groups))
        self.calculations = list(self.perform_calculations())

    def __repr__(self):
        return str(self.numbers)

    def partition_into_unique_pairs(self, all_groups):
        # The pairs are unordered: a pair (a, b) is equivalent to (b, a).
        # Therefore, for pairs of equal length only half of all combinations
        # need to be generated to obtain all pairs; this is set by the limit.
        if self.size == 1:
            return
        numbers, size = self.numbers, self.size
        limits = (self.halfbinom(size, size//2), )
        unique_numbers = set()
        for m, limit in zip_longest(range((size+1)//2, size), limits):
            for numbers1, numbers2 in self.paired_combinations(numbers, m, limit):
                if numbers1 in unique_numbers:
                    continue
                unique_numbers.add(numbers1)
                group1, group2 = all_groups[numbers1], all_groups[numbers2]
                yield (group1, group2)

    def perform_calculations(self):
        if self.size == 1:
            yield Calculation.singleton(self.numbers[0])
            return
        for group1, group2 in self.partitions:
            for calc1, calc2 in product(group1.calculations, group2.calculations):
                yield from Calculation.generate(calc1, calc2)

    @classmethod
    def paired_combinations(cls, numbers, m, limit):
        for cnt, numbers1 in enumerate(combinations(numbers, m), 1):
            numbers2 = tuple(cls.filtering(numbers, numbers1))
            yield (numbers1, numbers2)
            if cnt == limit:
                return

    @staticmethod
    def filtering(iterable, elements):
        # filter elements out of an iterable, return the remaining elements
        elems = iter(elements)
        k = next(elems, None)
        for n in iterable:
            if n == k:
                k = next(elems, None)
            else:
                yield n

    @staticmethod
    @lru_cache()
    def halfbinom(n, k):
        if n % 2 == 1:
            return None
        prod = 1
        for m, l in zip(reversed(range(n+1-k, n+1)), range(1, k+1)):
            prod = (prod*m)//l
        return prod//2


class Calculation:
    """
        A Calculation consists of an expression (a string) and a result (an integer).
        New calculations are generated from two given calculations, by performing
        arithmetic operations (+, -, x, /) on their results. Invalid outcomes
        (zeroes, negative numbers, fractions, trivial results) are ignored.
        For a single number, the calculation is simply the number itself.
    """
    def __init__(self, expression, result, is_singleton=False):
        self.expr = expression
        self.result = result
        self.is_singleton = is_singleton

    def __repr__(self):
        return self.expr

    @classmethod
    def singleton(cls, n):
        return cls(f"{n}", n, is_singleton=True)

    @classmethod
    def generate(cls, calca, calcb):
        if calca.result < calcb.result:
            calca, calcb = calcb, calca
        for result, op in cls.operations(calca.result, calcb.result):
            expr1 = f"{calca.expr}" if calca.is_singleton else f"({calca.expr})"
            expr2 = f"{calcb.expr}" if calcb.is_singleton else f"({calcb.expr})"
            yield cls(f"{expr1} {op} {expr2}", result)

    @staticmethod
    def operations(x, y):
        yield (x + y, '+')
        if x > y:                     # exclude non-positive results
            yield (x - y, '-')
        if y > 1 and x > 1:           # exclude trivial results
            yield (x * y, 'x')
        if y > 1 and x % y == 0:      # exclude trivial and non-integer results
            yield (x // y, '/')


def countdown_solver():
    # input: target and numbers. If you want to play with more or less than
    # 6 numbers, use the second version of 'unsorted_numbers'.
    try:
        target = int(sys.argv[1])
        unsorted_numbers = (int(sys.argv[n+2]) for n in range(6))  # for 6 numbers
#        unsorted_numbers = (int(n) for n in sys.argv[2:])         # for any numbers
        numbers = tuple(sorted(unsorted_numbers, reverse=True))
    except (IndexError, ValueError):
        print("You must provide a target and numbers!")
        return

    solutions = Solutions(numbers)
    smallest_difference = target
    bestresults = []
    for calculation in solutions.walk():
        diff = abs(calculation.result - target)
        if diff <= smallest_difference:
            if diff < smallest_difference:
                bestresults = [calculation]
                smallest_difference = diff
            else:
                bestresults.append(calculation)
    output(target, smallest_difference, bestresults)


def output(target, diff, results):
    print(f"\nThe closest results differ from {target} by {diff}. They are:\n")
    for calculation in results:
        print(f"{calculation.result} = {calculation.expr}")


if __name__ == "__main__":
    countdown_solver()

# countdown_solver
A Python code to solve the mathematical puzzles of the game show Countdown.

---

Countdown is a game show, originally from France (_Des chiffres et des lettres_),
which has been broadcast in many countries.  It consists of 'letters' rounds and
'numbers' rounds. \
The rules of a numbers round are as follows (from
[wikipedia](https://en.wikipedia.org/wiki/Countdown_(game_show)#Numbers_round)):

> The contestant in control chooses six of 24 shuffled face-down number tiles,
arranged into two groups: 20 "small numbers" (two each of 1 through 10),
and four "large numbers" of 25, 50, 75 and 100. \
The contestant decides how many large numbers are to be used, from none to all four,
after which the six tiles are randomly drawn and placed on the board. \
A random three-digit target number is then generated, and the contestants have
30 seconds to work out a sequence of calculations with the numbers whose
final result is as close to the target number as possible. \
They may use only the four basic operations of addition, subtraction,
multiplication and division, and do not have to use all six numbers. \
A number may not be used more times than it appears on the board. Fractions are
not allowed, and only positive integers may be obtained as a result at any
stage of the calculation.

---

#### Example:

Target: 809 \
Numbers: 50, 75, 9, 1, 1, 5 \
Solution: 75/5 = 15. 15 + 1 = 16. 50 x 16 = 800. 800 + 9 = 809.  Or in short:
809 = (50 x ((75 / 5) + 1)) + 9

This Python code is designed to solve such puzzles. Given a target and 6 numbers on the
command line, it will generate all solutions as close to the target as possible;
solutions with fewer numbers are listed first. \
Each solution is a unique sequence of operations. Solutions that differ only
by commutative operations (a + b versus b + a; a x b versus b x a) are only listed once,
contrary to solutions that differ by associative operations
(solutions involving (a + (b + c)) and ((a + b) + c) will both be listed).
Trivial operations (multiplying or dividing by 1, operations involving 0) are excluded.

---

The algorithm works as follows:

1. The numbers are put into a tuple of length 6 in descending order. Then, all unique
subgroups of lengths 1 to 6 are created, the smallest groups first.\
**Example**: (75, 50, 5, 9, 1, 1) -> {(75), (50), (9), (5), (1),
(75, 50), (75, 9), (75, 5), ..., (75, 50, 9, 5, 1, 1)}.

2. Next, the groups are organised into a hierarchical tree: every group is partitioned
into all unique unordered pairs of its non-empty subgroups.\
**Example**: (9, 5, 1, 1) -> [(9, 5, 1) + (1), (9, 1, 1) + (5), (5, 1, 1) + (9),
(9, 5) + (1, 1), (9, 1) + (5, 1)].

3. Within each group of numbers, the calculations are performed and the results are
stored. For groups of length 1, the result is simply the number itself. For larger
groups, the calculations are carried out on every pair of subgroups: in each pair, all
results of the first subgroup are combined with all results of the second subgroup
using +, -, x and /, and the valid outcomes are stored.\
**Example**: (75, 5) consists of the pair ((75), (5)). The result of (75) is 75; the
result of (5) is 5; the results of (75, 5) are [75+5=80, 75-5=70, 75*5=375, 75/5=15].

4. In this manner, all results are generated, from the smallest groups to the largest.
Finally, the algorithm iterates through all results and selects the ones that are the
closest match to the target number.

---

#### Example:

```
>>> countdown_solver.py 809 50 75 9 1 1 5

The closest results differ from 809 by 0. They are:

809 = (50 x ((75 / 5) + 1)) + 9
809 = ((75 x 5) x (1 + 1)) + (50 + 9)
809 = ((75 x (1 + 1)) x 5) + (50 + 9)
809 = (75 x (5 x (1 + 1))) + (50 + 9)
809 = (((75 x 5) x (1 + 1)) + 50) + 9
809 = (((75 x (1 + 1)) x 5) + 50) + 9
809 = ((75 x (5 x (1 + 1))) + 50) + 9
809 = (((75 x 5) x (1 + 1)) + 9) + 50
809 = (((75 x (1 + 1)) x 5) + 9) + 50
809 = ((75 x (5 x (1 + 1))) + 9) + 50
```

**Requires Python 3.6 or higher.**

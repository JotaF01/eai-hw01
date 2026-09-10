#!/usr/bin/env python3
"""The sliding-tile puzzle itself: state, moves, and the solvability constraint.

Nothing in here knows about search. A state is a plain tuple of n*n ints, row
major, with 0 for the blank:

    (5, 1, 2, 3,          5  1  2  3
     4, 6, 8, 7,     ==   4  6  8  7
     9, 0, 10, 11,        9  .  10 11
     12, 13, 14, 15)      12 13 14 15

Tuples are hashable and immutable, so they drop straight into the `set` of
closed nodes and the `dict` of g-values that A* needs. That is the whole reason
for the representation.

THE CONSTRAINT (why half of all boards are unsolvable)
-----------------------------------------------------
Every legal move swaps the blank with a neighbour. Two things happen at once:

  1. the permutation of the 16 cells is multiplied by a transposition, so its
     parity flips;
  2. the blank moves one step, so the parity of its taxicab distance from home
     flips too.

Their sum is therefore invariant. The goal has sum 0 (even), so:

    a state is solvable  <=>  perm_parity(state) + blank_taxicab(state) is even

That is exact for any board size and, unlike the textbook "count inversions"
rule, for any goal - including the deck's goal with the blank in the CORNER.
`Puzzle.solvable()` is the only gate; every constructor here goes through it.
"""
from __future__ import annotations

import random

# blank moves; (row delta, col delta, name). The name describes where the BLANK
# goes, so a solution path reads as a sequence of blank moves.
MOVES = ((-1, 0, "U"), (1, 0, "D"), (0, -1, "L"), (0, 1, "R"))
OPPOSITE = {"U": "D", "D": "U", "L": "R", "R": "L"}


class Puzzle:
    """An n x n sliding-tile problem: a goal, the moves, and the constraint.

    n = 3 gives the 8-puzzle of the slides, n = 4 the 15-puzzle. Nothing below
    is hard-coded to either.
    """

    def __init__(self, size: int = 4, goal: tuple[int, ...] | None = None):
        if size < 2:
            raise ValueError("size must be at least 2")
        self.n = size
        self.cells = size * size
        # default goal: blank in the TOP-LEFT corner, 1..n^2-1 after it. This is
        # the goal on slide 36 of eai-01-search (_ 1 2 / 3 4 5 / 6 7 8), not the more
        # common blank-last convention. Pass `goal=` for the other one.
        self.goal = tuple(goal) if goal else tuple(range(self.cells))
        self.validate(self.goal)
        # goal_pos[tile] = (row, col) it belongs in - used by every heuristic
        self.goal_pos = [(0, 0)] * self.cells
        for i, tile in enumerate(self.goal):
            self.goal_pos[tile] = divmod(i, self.n)
        self.blank_home = self.goal_pos[0]

    # ---------------------------------------------------------------- validity

    def validate(self, state) -> tuple[int, ...]:
        """Reject anything that is not a permutation of 0..n^2-1."""
        state = tuple(state)
        if len(state) != self.cells or sorted(state) != list(range(self.cells)):
            raise ValueError(
                f"a {self.n}x{self.n} board must be a permutation of "
                f"0..{self.cells - 1}, got {state}"
            )
        return state

    def perm_parity(self, state) -> int:
        """0 if the permutation state -> goal is even, 1 if odd.

        Counted by cycle decomposition, which is O(n^2) and, unlike inversion
        counting, needs no assumption about where the blank lives in the goal.
        """
        where = {tile: i for i, tile in enumerate(state)}
        target = [where[tile] for tile in self.goal]  # target[i] = index in state
        seen = [False] * self.cells
        parity = 0
        for i in range(self.cells):
            if seen[i]:
                continue
            length = 0
            j = i
            while not seen[j]:
                seen[j] = True
                j = target[j]
                length += 1
            parity ^= (length - 1) & 1  # a k-cycle is k-1 transpositions
        return parity

    def blank_taxicab(self, state) -> int:
        r, c = divmod(state.index(0), self.n)
        gr, gc = self.blank_home
        return abs(r - gr) + abs(c - gc)

    def solvable(self, state) -> bool:
        """The invariant above. Half of all boards fail it - by construction."""
        state = self.validate(state)
        return (self.perm_parity(state) + self.blank_taxicab(state)) % 2 == 0

    def require_solvable(self, state) -> tuple[int, ...]:
        state = self.validate(state)
        if not self.solvable(state):
            raise ValueError(
                "this board is in the OTHER orbit - no sequence of moves reaches "
                "the goal. Swap any two non-blank tiles to fix it.\n"
                + self.render(state)
            )
        return state

    # ------------------------------------------------------------------- moves

    def neighbors(self, state):
        """Yield (next_state, move) for each legal blank move. Every move costs 1."""
        blank = state.index(0)
        br, bc = divmod(blank, self.n)
        for dr, dc, name in MOVES:
            r, c = br + dr, bc + dc
            if 0 <= r < self.n and 0 <= c < self.n:
                swap = r * self.n + c
                nxt = list(state)
                nxt[blank], nxt[swap] = nxt[swap], 0
                yield tuple(nxt), name

    def apply(self, state, move: str):
        for nxt, name in self.neighbors(state):
            if name == move:
                return nxt
        raise ValueError(f"move {move!r} is illegal from\n{self.render(state)}")

    def is_goal(self, state) -> bool:
        return tuple(state) == self.goal

    # -------------------------------------------------------------- generation

    def scramble(self, moves: int = 40, seed: int | None = None):
        """A random WALK back from the goal - solvable by construction.

        `moves` is an upper bound on the optimal solution length, not the
        optimal length itself: the walk undoes itself sometimes. It is the knob
        that keeps a classroom demo finishing before the bell.
        """
        rng = random.Random(seed)
        state, last = self.goal, None
        for _ in range(moves):
            options = [(s, m) for s, m in self.neighbors(state)
                       if last is None or m != OPPOSITE[last]]
            state, last = rng.choice(options)
        return state

    def random_state(self, seed: int | None = None):
        """A uniformly random SOLVABLE board - i.e. the hard end of the pool.

        Shuffle, then repair parity by swapping two non-blank tiles. For the
        15-puzzle these average ~53 moves to solve, which is out of reach for
        plain A* and is exactly why `idastar.py` exists.
        """
        rng = random.Random(seed)
        state = list(range(self.cells))
        rng.shuffle(state)
        if not self.solvable(tuple(state)):
            i, j = [k for k, t in enumerate(state) if t != 0][:2]
            state[i], state[j] = state[j], state[i]
        return tuple(state)

    # ------------------------------------------------------------------- text

    def parse(self, text: str):
        """Read "7 2 4 / 5 _ 6 / 8 3 1" (or newlines, or 0 for the blank)."""
        tokens = text.replace("/", " ").replace("|", " ").split()
        state = tuple(0 if t in ("_", ".", "0", "x") else int(t) for t in tokens)
        return self.validate(state)

    def render(self, state, cell: int | None = None) -> str:
        w = cell or len(str(self.cells - 1))
        rows = []
        for r in range(self.n):
            row = state[r * self.n:(r + 1) * self.n]
            rows.append(" ".join(("_" if t == 0 else str(t)).rjust(w) for t in row))
        return "\n".join(rows)

    def render_path(self, state, moves) -> str:
        """Every board along a solution, side by side, wrapped to the terminal."""
        boards = [self.render(state)]
        labels = ["start"]
        for m in moves:
            state = self.apply(state, m)
            boards.append(self.render(state))
            labels.append(m)
        out, per_line = [], max(1, 76 // (self.n * (len(str(self.cells - 1)) + 1) + 4))
        for i in range(0, len(boards), per_line):
            chunk, tags = boards[i:i + per_line], labels[i:i + per_line]
            width = max(len(l.split("\n")[0]) for l in chunk) + 4
            out.append("".join(t.center(width) for t in tags))
            for r in range(self.n):
                out.append("".join(b.split("\n")[r].center(width) for b in chunk))
            out.append("")
        return "\n".join(out)


# The two boards that appear in the deck (session-01/eai-01-search.md, slides 20 and 36).
def reversed_board(size: int = 4, blank_last: bool = True) -> tuple[int, ...]:
    """Every tile in reverse order - which is impossible on an even board.

        4x4:  15 14 13 12 / 11 10 9 8 / 7 6 5 4 / 3 2 1 _     no solution exists
        3x3:   8  7  6 /  5  4  3 /  2  1 _                    solvable in 30 moves

    It is the most convincing unsolvable board to show a class, because nothing
    about it looks wrong: it is perfectly ordered, just backwards.

    The reason is the parity invariant and nothing else. Reversing n^2-1 tiles is
    (n^2-1)//2 swaps, and the blank never leaves home, so

        3x3:  8 tiles ->  4 swaps -> even -> reachable
        4x4: 15 tiles ->  7 swaps -> ODD  -> unreachable
        5x5: 24 tiles -> 12 swaps -> even -> reachable
        6x6: 35 tiles -> 17 swaps -> ODD  -> unreachable

    So the same idea - "put them all backwards" - flips between possible and
    impossible as the board grows. Half of all boards are unreachable, and this
    is a member of that half you can write down from memory.
    """
    tiles = list(range(1, size * size))[::-1]
    return tuple(tiles + [0]) if blank_last else tuple([0] + tiles)


# slide 20, the DFS/BFS trees - with the spiral goal that board is posed against
EIGHT_PUZZLE_DFS = ("2 8 3 / 1 6 4 / 7 _ 5",
                    "1 2 3 / 8 _ 4 / 7 6 5")
# slide 36, the A* board
EIGHT_PUZZLE_ASTAR = ("7 2 4 / 5 _ 6 / 8 3 1",
                      "_ 1 2 / 3 4 5 / 6 7 8")


if __name__ == "__main__":
    p = Puzzle(3, goal=Puzzle(3).parse(EIGHT_PUZZLE_ASTAR[1]))
    start = p.parse(EIGHT_PUZZLE_ASTAR[0])
    print(p.render(start), "\nsolvable:", p.solvable(start))

#!/usr/bin/env python3
"""Check a proposed solution: does this move sequence solve this board?

    python3 verify.py --start "7 2 4 / 5 _ 6 / 8 3 1" \
                      --goal  "_ 1 2 / 3 4 5 / 6 7 8" \
                      --moves "L U R D D L U R R U L L D R R D L L U R R U L D L U"

    python3 verify.py --blank-last --start "..." --moves-file student.txt
    python3 verify.py --blank-last --start "..." --moves - < student.txt

Exit code 0 if the moves solve the board, 1 if not - so it can be used in a
script or test workflow.

WHAT A MOVE MEANS
-----------------
A move names WHERE THE BLANK GOES: `L` slides the blank one square left, which
slides the tile on its left one square right. That is the convention required by
the Homework 01 submission format.

Students often write the opposite - the direction the TILE moves. Rather than
argue, pass `--moves-are tile` and the same sequence is read the other way
round. Both are legitimate; only silence about which one is in use is not.

WHAT IS CHECKED
---------------
1. the start board is a permutation of 0..n^2-1, and is solvable at all;
2. every move is legal - the blank cannot leave the board;
3. the final board equals the goal.

A sequence can fail three different ways, and they need different feedback:
an illegal move (step 12 pushes the blank off the edge), a legal sequence that
ends somewhere else, or a board that was never solvable to begin with.
"""
from __future__ import annotations

import argparse
import sys

from board import OPPOSITE, Puzzle

WORDS = {"U": "U", "D": "D", "L": "L", "R": "R",
         "UP": "U", "DOWN": "D", "LEFT": "L", "RIGHT": "R",
         "↑": "U", "↓": "D", "←": "L", "→": "R",
         "^": "U", "V": "D", "<": "L", ">": "R"}


def parse_moves(text: str, moves_are: str = "blank") -> list[str]:
    """Read a solution in whatever shape a student pasted it.

    Accepts "L U R D", "l,u,r,d", "LURD", "left up right down", arrows, and
    newlines. Raises ValueError naming the first token it cannot read.
    """
    for sep in ",;|/\n\t":
        text = text.replace(sep, " ")
    tokens = text.upper().split()
    if len(tokens) == 1 and len(tokens[0]) > 1 and set(tokens[0]) <= set("UDLR"):
        tokens = list(tokens[0])          # "LURD" written with no separators
    moves = []
    for i, token in enumerate(tokens, 1):
        if token not in WORDS:
            raise ValueError(f"move {i}: cannot read {token!r} - "
                             "use U D L R (or up/down/left/right, or arrows)")
        move = WORDS[token]
        moves.append(OPPOSITE[move] if moves_are == "tile" else move)
    return moves


def check(puzzle: Puzzle, start, moves: list[str]):
    """Replay the moves. Returns (state, failed_at, reason).

    `failed_at` is the 1-based index of the first illegal move, or None if the
    whole sequence was legal. Reaching the goal is a separate question - ask
    `puzzle.is_goal(state)` - because "legal but wrong" is the interesting case.
    """
    state = puzzle.require_solvable(start)
    for i, move in enumerate(moves, 1):
        legal = {m: nxt for nxt, m in puzzle.neighbors(state)}
        if move not in legal:
            edge = {"U": "top", "D": "bottom", "L": "left", "R": "right"}[move]
            return state, i, (f"move {i} is {move}, but the blank is already "
                              f"against the {edge} edge")
        state = legal[move]
    return state, None, ""


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--start", required=True, help='e.g. "7 2 4 / 5 _ 6 / 8 3 1"')
    ap.add_argument("--goal", help="default: the blank in the top-left corner")
    ap.add_argument("--blank-last", action="store_true",
                    help="goal 1..n^2-1 then the blank")
    ap.add_argument("--moves", help='the solution, or "-" to read stdin')
    ap.add_argument("--moves-file", help="read the solution from a file")
    ap.add_argument("--moves-are", choices=("blank", "tile"), default="blank",
                    help="does a letter say where the BLANK goes (default) or "
                         "the direction the TILE slides?")
    ap.add_argument("--show", action="store_true", help="draw every board")
    args = ap.parse_args(argv)

    size = round(len(args.start.replace("/", " ").split()) ** 0.5)
    scratch = Puzzle(size)
    goal = (scratch.parse(args.goal) if args.goal else
            tuple(list(range(1, size * size)) + [0]) if args.blank_last else None)
    puzzle = Puzzle(size, goal=goal)

    text = args.moves
    if args.moves_file:
        text = open(args.moves_file).read()
    elif text == "-" or text is None:
        text = sys.stdin.read()

    try:
        start = puzzle.require_solvable(puzzle.parse(args.start))
        moves = parse_moves(text, args.moves_are)
    except ValueError as bad:                 # unreadable, or in the other orbit
        print(bad, file=sys.stderr)
        return 2

    print(puzzle.render(start))
    print(f"\n{len(moves)} move{'' if len(moves) == 1 else 's'} submitted"
          + ("" if args.moves_are == "blank" else "  (read as tile directions)"))

    state, failed_at, reason = check(puzzle, start, moves)

    if args.show:
        print("\n" + puzzle.render_path(start, moves[:(failed_at or len(moves) + 1) - 1]))

    if failed_at:
        print(f"\nILLEGAL: {reason}")
        print(f"the board after {failed_at - 1} legal moves:\n{puzzle.render(state)}")
        return 1
    if not puzzle.is_goal(state):
        wrong = sum(1 for i, t in enumerate(state) if t and t != puzzle.goal[i])
        print(f"\nNOT SOLVED: every move was legal, but the board ends here "
              f"with {wrong} tiles out of place:\n{puzzle.render(state)}")
        return 1

    print(f"\nSOLVED in {len(moves)} move{'' if len(moves) == 1 else 's'}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

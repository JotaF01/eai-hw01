#!/usr/bin/env python3
"""Validate the standardized Homework 01 puzzle submission.

    python3 check_submission.py path/to/puzzle-solutions.json

The checker validates the submission record and replays every reported
successful solution. It is intentionally a format checker, not a grader.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from board import Puzzle
from verify import check, parse_moves

REQUIRED = {
    "board_id", "algorithm", "start", "goal", "moves_are", "moves", "found",
    "solution_length", "solution_cost", "expanded", "generated", "peak_frontier",
    "runtime_seconds", "cutoff", "optimality", "verified",
}
ALGORITHMS = {"dfs", "bfs", "greedy", "astar", "ucs", "iddfs", "idastar", "other"}


def fail(label: str, message: str):
    raise ValueError(f"{label}: {message}")


def number(value, label: str, *, integer=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
        fail(label, "must be a non-negative number")
    if integer and not isinstance(value, int):
        fail(label, "must be a non-negative integer")


def standard_board_text(text: str, label: str) -> int:
    """Require the course notation: rows separated by / and _ for the blank."""
    if not isinstance(text, str):
        fail(label, "must be a board-state string")
    rows = [row.strip() for row in text.split("/")]
    if len(rows) < 2 or any(not row for row in rows):
        fail(label, "must use / to separate rows")
    size = len(rows)
    tokens = [row.split() for row in rows]
    if any(len(row) != size for row in tokens):
        fail(label, f"must have {size} tiles in each of its {size} rows")
    flat = [tile for row in tokens for tile in row]
    if flat.count("_") != 1:
        fail(label, "must use exactly one _ for the blank (not 0 or .)")
    if any(tile in {"0", ".", "x"} for tile in flat):
        fail(label, "must use _ for the blank (not 0, ., or x)")
    return size


def puzzle_for(record: dict, label: str) -> tuple[Puzzle, tuple[int, ...]]:
    size = standard_board_text(record["start"], f"{label}.start")
    goal_size = standard_board_text(record["goal"], f"{label}.goal")
    if goal_size != size:
        fail(label, "start and goal must have the same board size")
    scratch = Puzzle(size)
    try:
        goal = scratch.parse(record["goal"])
        puzzle = Puzzle(size, goal=goal)
        return puzzle, puzzle.require_solvable(puzzle.parse(record["start"]))
    except ValueError as error:
        fail(label, str(error))


def validate_record(record, index: int):
    label = f"puzzle_results[{index}]"
    if not isinstance(record, dict):
        fail(label, "must be an object")
    missing = REQUIRED - record.keys()
    if missing:
        fail(label, "missing " + ", ".join(sorted(missing)))
    if not isinstance(record["board_id"], str) or not record["board_id"].strip():
        fail(label, "board_id must be a non-empty string")
    if record["algorithm"] not in ALGORITHMS:
        fail(label, "algorithm must be one of " + ", ".join(sorted(ALGORITHMS)))
    if record["moves_are"] != "blank":
        fail(label, "moves_are must be 'blank'")
    if not isinstance(record["moves"], list) or not all(isinstance(m, str) for m in record["moves"]):
        fail(label, "moves must be an array of move strings")
    if not isinstance(record["found"], bool) or not isinstance(record["verified"], bool):
        fail(label, "found and verified must be true or false")
    if record["optimality"] not in {"yes", "no", "unknown"}:
        fail(label, "optimality must be yes, no, or unknown")
    if record["cutoff"] is not None and not isinstance(record["cutoff"], str):
        fail(label, "cutoff must be a string or null")
    for field in ("expanded", "generated", "peak_frontier"):
        number(record[field], f"{label}.{field}", integer=True)
    number(record["runtime_seconds"], f"{label}.runtime_seconds")

    puzzle, start = puzzle_for(record, label)
    try:
        moves = parse_moves(" ".join(record["moves"]))
    except ValueError as error:
        fail(label, str(error))
    state, failed_at, _ = check(puzzle, start, moves)
    solved = failed_at is None and puzzle.is_goal(state)

    if record["found"]:
        if not solved:
            fail(label, "found is true but the moves do not reach the stated goal")
        if not record["verified"]:
            fail(label, "a found solution must have verified: true")
        for field in ("solution_length", "solution_cost"):
            if record[field] != len(moves):
                fail(label, f"{field} must equal the {len(moves)} reported moves")
    else:
        if moves or record["verified"]:
            fail(label, "an unsuccessful run must use no moves and verified: false")
        if record["solution_length"] is not None or record["solution_cost"] is not None:
            fail(label, "an unsuccessful run must use null solution_length and solution_cost")


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print("usage: python3 check_submission.py puzzle-solutions.json", file=sys.stderr)
        return 2
    try:
        data = json.loads(Path(argv[0]).read_text())
        if not isinstance(data, dict) or data.get("assignment") != "homework-01":
            fail("submission", "assignment must be 'homework-01'")
        records = data.get("puzzle_results")
        if not isinstance(records, list) or not records:
            fail("submission", "puzzle_results must be a non-empty array")
        for index, record in enumerate(records):
            validate_record(record, index)
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"INVALID: {error}", file=sys.stderr)
        return 1
    print(f"VALID: {len(records)} puzzle result(s) checked.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

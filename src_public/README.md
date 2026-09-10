# Homework 01 — public starter and validation files

This is the student-facing source directory for Homework 01. It contains
starter code, data, visualization support, and solution validators. It does
**not** contain implementations of the search algorithms students are required
to develop.

## Railway search

Choose either the browser or Python route:

- **Browser:** open `index.html` directly. The page loads `student.js`.
  `student.js` contains the worked BFS example and the function stubs where you
  implement the other searches. Each search yields snapshots of its current
  node, frontier, and visited set; `index.html` uses those snapshots to
  visualize your algorithm and displays the route it returns.
- **Python:** open `Astar-railway.ipynb`. It contains the same worked BFS
  example, TODO cells for the other searches, and plotting/measurement support.

The browser uses `graph-data.js`; the notebook uses `graph.json`. These contain
the same supplied railway network and are not files you need to modify.

## 15-puzzle validation

The `puzzle15/` directory contains validation tools, not search solutions:

- `verify.py` replays a sequence of blank moves and checks whether it legally
  reaches the stated goal.
- `check_submission.py` validates the structure and consistency of
  `puzzle-solutions.json`, then replays every result marked as found.
- `board.py` provides the board parsing and move mechanics needed by both
  validators.

For example:

```sh
cd src_public/puzzle15
python3 verify.py --start "<assigned board>" --goal "<assigned goal>" --moves "U R D ..."
python3 check_submission.py ../../puzzle-solutions.json
```

These tools can establish that a move sequence is legal and reaches the goal.
They do not generate a solution, implement greedy best-first search or A*, or
prove that a submitted solution is optimal.

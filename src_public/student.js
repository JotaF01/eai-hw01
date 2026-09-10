/* ============================================================
   CSC 448/548 — Evolutionary Artificial Intelligence — Search lab
   THIS IS THE ONLY FILE YOU NEED TO EDIT.

   Every algorithm is a GENERATOR. Each time you are about to
   expand a node, `yield` a snapshot; the visualiser draws it.
   When you reach the goal, `return` a path (array of city ids).

   The `p` argument gives you:
     p.start, p.goal            city ids (strings)
     p.neighbors(id)            -> [{ to, mi }, ...]
     p.h(id)                    -> straight-line miles from id to the goal
     p.reconstruct(parent, id)  -> array of ids from start to id
     p.w                        -> heuristic weight from the slider

   A snapshot is: { current, frontier, visited }
   ============================================================ */

// ---------- WORKED EXAMPLE: breadth-first search ----------
function* bfs(p) {
  const parent = new Map([[p.start, null]]);
  const frontier = [p.start];
  const visited = new Set();

  while (frontier.length > 0) {
    const node = frontier.shift();          // QUEUE: take from the front
    if (visited.has(node)) continue;
    visited.add(node);

    yield { current: node, frontier: [...frontier], visited: [...visited] };

    if (node === p.goal) return p.reconstruct(parent, node);

    for (const { to } of p.neighbors(node)) {
      if (!visited.has(to) && !parent.has(to)) {
        parent.set(to, node);
        frontier.push(to);                  // QUEUE: add to the back
      }
    }
  }
  return null;                              // no path
}

// ---------- TODO 1: depth-first search ----------
// Hint: identical to bfs() except for ONE line. Which one?
function* dfs(p) {
  return null;
}

// ---------- TODO 2: uniform-cost search (Dijkstra) ----------
// Expand the frontier node with the smallest g (cost from start).
// Hint: keep a `g` Map; pick the frontier entry with the smallest g.
function* ucs(p) {
  return null;
}

// ---------- TODO 3: greedy best-first search ----------
// Expand the frontier node with the smallest h (estimate to goal).
// Watch what it does between Denver and the east coast.
function* greedy(p) {
  return null;
}

// ---------- TODO 4: A* ----------
// Expand the frontier node with the smallest f = g + p.w * h.
// With p.w = 1 this is A*. Try the slider at 0 and at 3 afterwards.
function* astar(p) {
  return null;
}

window.ALGORITHMS = { bfs, dfs, ucs, greedy, astar };

import json
import math
import time
import heapq
from pathlib import Path

GRAPH_PATH = Path (__file__).resolve().parent.parent / "src_public" / "graph.json"
G = json.loads(GRAPH_PATH.read_text())

CITY = {c["id"]: c for c in G["cities"]}
ADJ = {c: [] for c in CITY}
for e in G["edges"]:
    ADJ[e["a"]].append((e["b"], e["mi"]))
    ADJ[e["b"]].append((e["a"], e["mi"]))
for c in ADJ:
    ADJ[c].sort()

DC = "Washington, District of Columbia"
SF = "San Francisco, California"

def straight_line_miles(a, b):
    A, B = CITY[a], CITY[b]
    p1, p2 = math.radians(A["lat"]), math.radians(B["lat"])
    dphi = p2 - p1
    dlam = math.radians(B["lon"]-A["lon"])
    x = math.sin(dphi/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dlam/2)**2
    return 2 * 3958.8 * math.asin(math.sqrt(x))

class Problem:
    def __init__(self, start=DC, goal=SF, w=1.0):
        self.start, self.goal, self.w = start, goal, w
    def neighbors(self, city):
        return ADJ[city]

    def h(self, city):
        return straight_line_miles(city, self.goal)
    def path(self, parent, city):
        out = []
        while city is not None:
            out.append(city)
            city = parent[city]
        return out[::-1]

def route_cost(path):
    return sum(dict(ADJ[a])[b]for a, b in zip (path, path[1:]))

class Meters:
    def __init__(self):
        self.expanded = 0
        self.generated = 0
        self.peak_frontier = 0

    def saw_frontier(self, size):
        if size > self.peak_frontier:
            self.peak_frontier = size

def bfs(p, m):
    from collections import deque

    parent = {p.start:None}
    frontier = deque([p.start])
    visited = set()

    while frontier:
        m.saw_frontier(len(frontier))
        city = frontier.popleft()
        if city in visited:
            continue
        visited.add(city)
        m.expanded += 1

        if city == p.goal:
            return p.path(parent, city)

        for nxt, mi in p.neighbors(city):
            m.generated += 1
            if nxt not in visited and nxt not in parent:
                parent[nxt]=city
                frontier.append(nxt)
    return None

def run(alg, start=DC, goal=SF, w=1.0):
    p = Problem(start, goal, w)
    m = Meters()
    t0 = time.perf_counter()
    path = alg(p, m)
    elapsed = time.perf_counter() - t0

    return{
        "found": path is not None,
        "path": path or [],
        "cost": round(route_cost(path))if path else None,
        "stops": len(path)-1 if path else None,
        "expanded":m.expanded,
        "generated":m.generated,
        "peak_frontier":m.peak_frontier,
        "runtime":elapsed,
    }

if __name__ =="__main__":
    r = run(bfs)
    print(f"BFS:{r['cost']}mi,{r['stops']}stops, "
          f"expanded {r['expanded']},generated {r['generated']},"
          f"peak frontier {r['peak_frontier']}, {r['runtime']:.4f}s")
    print("->".join(c.split(",")[0]for c in r["path"]))

def dfs(p, m):

    parent = {p.start:None}
    frontier = [p.start]
    visited = set()

    while frontier:
        m.saw_frontier(len(frontier))
        city = frontier.pop()
        if city in visited:
            continue
        visited.add(city)
        m.expanded += 1

        if city == p.goal:
            return p.path(parent, city)

        for nxt, mi in p.neighbors(city):
            m.generated += 1
            if nxt not in visited and nxt not in parent:
                parent[nxt]=city
                frontier.append(nxt)
    return None

if __name__ =="__main__":
    r = run(dfs)
    print(f"DFS:{r['cost']}mi,{r['stops']}stops, "
          f"expanded {r['expanded']},generated {r['generated']},"
          f"peak frontier {r['peak_frontier']}, {r['runtime']:.4f}s")
    print("->".join(c.split(",")[0]for c in r["path"]))

def greedy (p, m):
    tie = 0
    parent = {p.start: None}
    frontier = [(p.h(p.start), tie, p.start)]
    seen = {p.start}
    visited = set()

    while frontier:
        m.saw_frontier(len(frontier))
        _f, _t, city = heapq.heappop(frontier)
        if city in visited:
            continue
        visited.add(city)
        m.expanded += 1

        if city == p.goal:
            return p.path(parent, city)

        for nxt, mi in p.neighbors(city):
            m.generated += 1
            if nxt not in visited and nxt not in seen:
                seen.add(nxt)
                parent[nxt]=city
                tie+=1
                heapq.heappush(frontier, (p.h(nxt), tie, nxt))
    return None

def astar(p,m):
    tie = 0
    parent={p.start:None}
    g = {p.start:0.0}
    frontier = [(p.w*p.h(p.start), tie, p.start)]
    closed =set()

    while frontier:
        m.saw_frontier(len(frontier))
        _f, _t, city = heapq.heappop(frontier)
        if city in closed:
            continue
        closed.add(city)
        m.expanded += 1

        if city == p.goal:
            return p.path(parent, city)
        
        for nxt, mi in p.neighbors(city):
            m.generated += 1
            tentative = g[city]+mi
            if tentative < g.get(nxt, math.inf):
                g[nxt]=tentative
                parent[nxt]=city
                tie+=1
                heapq.heappush(frontier, (tentative+p.w*p.h(nxt),tie, nxt))
    return None

if __name__ =="__main__":
    r = run(greedy)
    print(f"Greedy:{r['cost']}mi,{r['stops']}stops, "
          f"expanded {r['expanded']},generated {r['generated']},"
          f"peak frontier {r['peak_frontier']}, {r['runtime']:.4f}s")

    r = run(astar)
    print(f"A*: {r['cost']} mi, {r['stops']} stops, "
          f"expanded {r['expanded']}, generated {r['generated']}, "
          f"peak frontier {r['peak_frontier']}, {r['runtime']:.4f}s")
    print(" -> ".join(c.split(",")[0] for c in r["path"]))
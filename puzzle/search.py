import sys, time, heapq, itertools
sys.path.insert(0, "../src_public/puzzle15")
from board import Puzzle

scratch = Puzzle(4)
GOAL = scratch.parse("1 2 3 4 / 5 6 7 8 / 9 10 11 12/13 14 15 _")
PZ = Puzzle(4, goal=GOAL)

def manhattan(state):
    total = 0
    for i,v in enumerate(state):
        if v==0:
            continue
        total += abs(i // 4 - (v - 1) // 4) + abs(i % 4 - (v - 1) % 4)
    return total

b1 = PZ.parse("1 2 7 3 / 5 6 _ 4 /9 10 11 8 / 13 14 15 12")
print(manhattan(b1))

class Meters:
    def __init__(self):
        self.expanded = 0
        self.generated = 0
        self.peak_frontier = 0

    def saw_frontier(self, size):
        if size > self.peak_frontier:
            self.peak_frontier = size

def astar(start,m):
    tie = 0
    parent={start:None}
    g = {start:0}
    frontier = [(manhattan(start), tie, start)]
    closed =set()

    while frontier:
        m.saw_frontier(len(frontier))
        _f, _t, state = heapq.heappop(frontier)
        if state in closed:
            continue
        closed.add(state)
        m.expanded += 1

        if PZ.is_goal(state):
            moves = []
            cur = state
            while parent[cur]is not None:
                prev, mv = parent[cur]
                moves.append(mv)
                cur = prev
            moves.reverse()
            return moves
        
        for nxt, mv in PZ.neighbors(state):
            m.generated += 1
            tentative = g[state]+1
            if tentative < g.get(nxt, float("inf")):
                g[nxt]=tentative
                parent[nxt]=(state,mv)
                tie+=1
                heapq.heappush(frontier, (tentative+manhattan(nxt),tie, nxt))
    return None

b1 = PZ.parse("1 2 7 3 / 5 6 _ 4 /9 10 11 8 / 13 14 15 12")
m = Meters()
print(astar(b1,m),m.expanded,m.generated,m.peak_frontier)

def greedy(start,m):
    tie = 0
    parent={start:None}
    g = {start:0}
    frontier = [(manhattan(start), tie, start)]
    closed =set()

    while frontier:
        m.saw_frontier(len(frontier))
        _f, _t, state = heapq.heappop(frontier)
        if state in closed:
            continue
        closed.add(state)
        m.expanded += 1

        if PZ.is_goal(state):
            moves = []
            cur = state
            while parent[cur]is not None:
                prev, mv = parent[cur]
                moves.append(mv)
                cur = prev
            moves.reverse()
            return moves
        
        for nxt, mv in PZ.neighbors(state):
            m.generated += 1
            tentative = g[state]+1
            if tentative < g.get(nxt, float("inf")):
                g[nxt]=tentative
                parent[nxt]=(state,mv)
                tie+=1
                heapq.heappush(frontier, (manhattan(nxt),tie, nxt))
    return None

b1 = PZ.parse("1 2 7 3 / 5 6 _ 4 / 9 10 11 8 / 13 14 15 12")
b5 = PZ.parse("6 11 2 3 / 9 _ 5 10 / 13 1 15 4 / 14 8 12 7")

m = Meters()
print("astar  b1", astar(b1, m), m.expanded, m.generated, m.peak_frontier)

m = Meters()
print("greedy b1", greedy(b1, m), m.expanded, m.generated, m.peak_frontier)

m = Meters()
r = astar(b5, m)
print("astar  b5", len(r), m.expanded, m.peak_frontier)

m = Meters()
r = greedy(b5, m)
print("greedy b5", len(r), m.expanded, m.peak_frontier)
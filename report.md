# Homework 1  Search strategies on routes and the 15-puzzle
Name: Jesus Ramirez Ardila
Date: 9/9/2026
 
## 1. Problem models
 
### Part A 
- **State:** a city id, for example `"St. Louis, Missouri"` (110 cities)
- **Initial state:** Washington, District of Columbia
- **Action:** take one track to a neighbor city (244 tracks, both directions)
- **Step cost:** the miles of that track, the `mi` field of the edge; all costs are > 0
- **Goal test:** `city == "San Francisco, California"`
- **Solution cost:** total miles of the route. **Solution length:** number of stops (edges)
- **Heuristic:** `h(n)` = great-circle miles from `n` to San Francisco
The meta block of `graph.json` says that track weight = great-circle miles × 1.15
(a winding factor). So `h(n)` is always smaller than or equal to the real miles that
are left. The heuristic never overestimates, so it is admissible.
 
The state is a city, not a route. This means that two different ways to arrive at
St. Louis are the same state. That is why graph-search duplicate detection works
here: a visited set can drop the second arrival, and each city only needs to
remember one parent.
 

 
## 2. Strategies
 
| strategy | frontier rule | duplicate detection | cutoff |
|---|---|---|---|
| DFS | LIFO stack | graph search: a city enters the frontier once and is expanded once | not needed — duplicate detection stops the search after at most 110 states |
| BFS | FIFO queue | graph search: a city enters the frontier once and is expanded once | none |
| Greedy best-first | priority queue on `f(n) = h(n)` only | closed set; a city is added to the queue once | none |
| A* (w = 1) | priority queue on `f(n) = g(n) + w·h(n)` | closed set plus a `g` map; a city goes back in the queue only if the new `g` is smaller | none |
 
All algorithms use the same counters, so the rows of the tables can be compared.
A node is **expanded** when it is taken out of the frontier and its neighbors are
asked for. A node is **generated** when it is produced as a neighbor, before any
duplicate check. **Peak frontier** is the biggest size the frontier ever had.
**Runtime** is the time of the search call only, without loading or printing.
 
## 3. Results
 
### Railway (Washington, D.C. → San Francisco, California)
 
| strategy | found? | cost / miles | stops | expanded | generated | peak frontier | runtime (s) | optimal? | note |
|---|---|---|---|---|---|---|---|---|---|
| DFS | yes | 5371 | 26 | 82 | 353 | 34 | 0.0002 | no | LIFO frontier; 2172 miles more than the best route |
| BFS | yes | 3551 | 14 | 109 | 480 | 17 | 0.0004 | no | FIFO frontier; fewest stops, but 352 miles more |
| Greedy best-first | yes | 3253 | 16 | 17 | 82 | 34 | 0.0004 | no | uses `h` only, never looks at `g`; 54 miles more |
| A* (w = 1) | yes | **3199** | 17 | 89 | 403 | 28 | 0.0006 | yes | `f = g + h` with an admissible heuristic |
 

 
**Routes**
 
- **A\* — 3199 mi, 17 stops:** Washington → Pittsburgh → Columbus → Dayton →
  Indianapolis → St. Louis → Springfield → Tulsa → Oklahoma City → Amarillo →
  Albuquerque → Phoenix → Riverside → Lancaster → Bakersfield → Fresno → Stockton →
  San Francisco
- **Greedy — 3253 mi, 16 stops:** Washington → Pittsburgh → Columbus → Cincinnati →
  Indianapolis → St. Louis → Kansas City → Wichita → Amarillo → Albuquerque → Phoenix →
  Riverside → Lancaster → Bakersfield → Fresno → Stockton → San Francisco
- **BFS — 3551 mi, 14 stops:** Washington → Pittsburgh → Columbus → Cincinnati →
  Indianapolis → St. Louis → Kansas City → Wichita → Amarillo → Fort Collins →
  Salt Lake City → Boise City → Reno → Sacramento → San Francisco
- **DFS — 5371 mi, 26 stops:** Washington → Virginia Beach → Raleigh → Greensboro →
  Charlotte → Columbia → Savannah → Jacksonville → Tallahassee → Montgomery → Mobile →
  New Orleans → Baton Rouge → Shreveport → Waco → Killeen → Lubbock → El Paso → Tucson →
  San Diego → Riverside → Las Vegas → Salt Lake City → Boise City → Reno → Stockton →
  San Francisco
### Puzzle

 
## 4. Analysis
1. Why does BFS return a different railway route from A*?
2. Greedy best-first vs A*: what does greedy ignore, and what did it cost or save?
3. Which strategy expanded the fewest railway nodes? Did it return the cheapest route?
4. On the assigned puzzle board, how did greedy and A* differ?
5. Under what assumptions is the A* solution optimal?
6. Which measurement if memory were the limiting resource?
7. If you added an optional strategy, what did it trade for its result?
8. If you implemented IDA*, when was its lower memory worth its repeated work?
## 5. Reproducibility
- **Language** Python 3.13.14
- **Machine:** Windows
- **Commands:**
```
  python railway/search.py
```
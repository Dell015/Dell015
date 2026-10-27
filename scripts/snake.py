#!/usr/bin/env python3
"""Pixel snake for a GitHub contribution graph.
The snake eats every day that has contributions and grows by one cell for each one.
Usage: snake.py USER OUT.svg      (reads GH_TOKEN from the environment, uses `gh api graphql`)
       snake.py --json data.json OUT.svg   (offline test: the calendar JSON from the GraphQL API)
"""
import json, subprocess, sys

QUERY = """query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{
totalContributions weeks{contributionDays{contributionCount contributionLevel weekday}}}}}}"""

F={}
def f(c,*rows): F[c]=rows
f("A","01110","10001","10001","11111","10001","10001","10001")
f("B","11110","10001","10001","11110","10001","10001","11110")
f("C","01110","10001","10000","10000","10000","10001","01110")
f("D","11110","10001","10001","10001","10001","10001","11110")
f("E","11111","10000","10000","11110","10000","10000","11111")
f("F","11111","10000","10000","11110","10000","10000","10000")
f("G","01110","10001","10000","10111","10001","10001","01111")
f("H","10001","10001","10001","11111","10001","10001","10001")
f("I","01110","00100","00100","00100","00100","00100","01110")
f("J","00111","00010","00010","00010","00010","10010","01100")
f("K","10001","10010","10100","11000","10100","10010","10001")
f("L","10000","10000","10000","10000","10000","10000","11111")
f("M","10001","11011","10101","10101","10001","10001","10001")
f("N","10001","11001","10101","10011","10001","10001","10001")
f("O","01110","10001","10001","10001","10001","10001","01110")
f("P","11110","10001","10001","11110","10000","10000","10000")
f("Q","01110","10001","10001","10001","10101","10010","01101")
f("R","11110","10001","10001","11110","10100","10010","10001")
f("S","01111","10000","10000","01110","00001","00001","11110")
f("T","11111","00100","00100","00100","00100","00100","00100")
f("U","10001","10001","10001","10001","10001","10001","01110")
f("V","10001","10001","10001","10001","10001","01010","00100")
f("W","10001","10001","10001","10101","10101","11011","10001")
f("X","10001","10001","01010","00100","01010","10001","10001")
f("Y","10001","10001","01010","00100","00100","00100","00100")
f("Z","11111","00001","00010","00100","01000","10000","11111")
f("0","01110","10001","10011","10101","11001","10001","01110")
f("1","00100","01100","00100","00100","00100","00100","01110")
f("2","01110","10001","00001","00010","00100","01000","11111")
f("3","11110","00001","00001","01110","00001","00001","11110")
f("4","00010","00110","01010","10010","11111","00010","00010")
f("5","11111","10000","11110","00001","00001","10001","01110")
f("6","00110","01000","10000","11110","10001","10001","01110")
f("7","11111","00001","00010","00100","01000","01000","01000")
f("8","01110","10001","10001","01110","10001","10001","01110")
f("9","01110","10001","10001","01111","00001","00010","01100")
f(" ","00000","00000","00000","00000","00000","00000","00000")
f("-","00000","00000","00000","11111","00000","00000","00000")
f(".","00000","00000","00000","00000","00000","01100","01100")
f(",","00000","00000","00000","00000","01100","00100","01000")
f(":","00000","01100","01100","00000","01100","01100","00000")
f("/","00001","00001","00010","00100","01000","10000","10000")
f("+","00000","00100","00100","11111","00100","00100","00000")
f(">","10000","01000","00100","00010","00100","01000","10000")
f("_","00000","00000","00000","00000","00000","00000","11111")
f("&","01100","10010","10100","01000","10101","10010","01101")
f("*","00000","10101","01110","11111","01110","10101","00000")
BG="#0d0d0f";PANEL="#151518";LINE="#2a2a30";WHITE="#f2f2f2";GRAY="#8a8a93";RED="#D11A2A";GREEN="#3ddc84"
def width(s,sc): return len(s)*6*sc-sc
def ptext(s,x,y,sc,fill):
    d=[]
    for i,ch in enumerate(s):
        g=F[ch]
        for r,row in enumerate(g):
            c=0
            while c<5:
                if row[c]=="1":
                    e=c
                    while e<5 and row[e]=="1": e+=1
                    d.append(f"M{x+(i*6+c)*sc} {y+r*sc}h{(e-c)*sc}v{sc}h-{(e-c)*sc}z"); c=e
                else: c+=1
    return f'<path d="{"".join(d)}" fill="{fill}"/>'


def load(argv):
    if argv[1] == "--json":
        return json.load(open(argv[2])), argv[3]
    out = subprocess.run(["gh", "api", "graphql", "-f", f"query={QUERY}", "-F", f"login={argv[1]}"],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)["data"]["user"]["contributionsCollection"]["contributionCalendar"], argv[2]

LV = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}
GREEN = {1: "#0e4429", 2: "#006d32", 3: "#26a641", 4: "#39d353"}
EMPTY = "#1b1b20"; SNAKE = "#D11A2A"; HEAD = "#ff4b5a"; START_LEN = 4
CELL, GAP, STEP = 13, 3, 0.07

def simulate(grid, ncols):
    """Chase the nearest contribution, avoid trapping itself. Returns the list of cells visited (one per step)."""
    import random
    from collections import deque
    rng = random.Random(7)
    def nbrs(p):
        c, r = p
        for d in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (c + d[0], r + d[1])
            if q in grid: yield q
    food = {p for p, lv in grid.items() if lv}
    start = (0, 0) if (0, 0) in grid else next(iter(grid))
    body = deque([start]); path = [start]; lens = [START_LEN]
    length = START_LEN; eaten = 0
    def reach(head, blocked, cap):
        seen = {head}; dq = deque([head])
        while dq and len(seen) < cap:
            p = dq.popleft()
            for q in nbrs(p):
                if q not in seen and q not in blocked: seen.add(q); dq.append(q)
        return len(seen)
    for _ in range(3000):
        if not food: break
        head = body[0]
        grow = False
        # after this move the tail leaves unless we are still growing to `length`
        def blocked_after(newhead):
            cells = [newhead] + list(body)
            keep = cells[:length]
            return set(keep[1:]) , keep
        # BFS from head over cells free of the body (tail is free because it moves)
        occ = set(list(body)[: max(length - 1, 0)])
        prev = {head: None}; dist = {head: 0}; dq = deque([head]); found = []
        while dq:
            p = dq.popleft()
            nb = list(nbrs(p)); rng.shuffle(nb)
            for q in nb:
                if q in prev or q in occ: continue
                prev[q] = p; dist[q] = dist[p] + 1; dq.append(q)
                if q in food: found.append(q)
        move = None
        for tgt in found[:6]:
            p = tgt
            while prev[p] != head: p = prev[p]
            blk, keep = blocked_after(p)
            if reach(p, blk, length + 4) >= min(length + 4, 24):
                move = p; break
        if move is None:
            options = []
            for q in nbrs(head):
                if q in occ: continue
                blk, keep = blocked_after(q)
                options.append((reach(q, blk, 400), rng.random(), q))
            if not options:
                # boxed in: shed the back half of the body and keep going
                length = max(START_LEN, length // 2)
                while len(body) > length: body.pop()
                continue
            move = max(options)[2]
        body.appendleft(move)
        if move in food:
            food.discard(move); length += 1; eaten += 1
        while len(body) > length: body.pop()
        path.append(move); lens.append(length)
    return path, lens

def build(cal):
    weeks = cal["weeks"]
    grid = {}
    for c, wk in enumerate(weeks):
        for d in wk["contributionDays"]:
            grid[(c, d["weekday"])] = LV[d["contributionLevel"]]
    route, lens = simulate(grid, len(weeks))
    cells, seen_food = [], set()
    for p in route:
        lv = grid[p]
        if lv and p not in seen_food: seen_food.add(p); cells.append((p[0], p[1], lv))
        else: cells.append((p[0], p[1], 0))
    n = len(cells)
    length = lens
    final = lens[-1]
    def L(j): return length[j] if j < n else final
    free = []
    j = 0
    for i in range(n):
        while j - L(j) + 1 <= i: j += 1
        free.append(j)
    total_steps = free[-1] + 6
    T = total_steps * STEP
    pad, top = 16, 52
    width = pad * 2 + len(weeks) * (CELL + GAP) - GAP
    height = top + 7 * (CELL + GAP) - GAP + pad + 6
    o = []
    o.append(f'<rect width="{width}" height="{height}" fill="#0d0d0f"/>')
    o.append(f'<rect x="3" y="3" width="{width-6}" height="{height-6}" fill="none" stroke="#2a2a30" stroke-width="4"/>')
    for a in (0, width - 8):
        for b in (0, height - 8):
            o.append(f'<rect x="{a}" y="{b}" width="8" height="8" fill="#0d0d0f"/>')
    o.append(ptext("CONTRIBUTIONS", pad, 18, 2, "#8a8a93"))
    o.append(ptext(f"{cal['totalContributions']} IN THE LAST YEAR", pad + 13 * 12 + 14, 18, 2, "#f2f2f2"))
    def pos(c, r): return pad + c * (CELL + GAP), top + r * (CELL + GAP)
    # background cells + food (food disappears the first time the head reaches it)
    eat_step = {}
    for i, (c, r, lv) in enumerate(cells):
        if lv: eat_step[(c, r)] = i
    for (c, r), lv in grid.items():
        x, y = pos(c, r)
        o.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" fill="{EMPTY}"/>')
        if lv and (c, r) in eat_step:
            te = (eat_step[(c, r)] + 1) * STEP / T
            o.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" fill="{GREEN[lv]}">'
                     f'<animate attributeName="opacity" values="1;0;0" keyTimes="0;{te:.5f};1" dur="{T:.2f}s" repeatCount="indefinite" calcMode="discrete"/></rect>')
        elif lv:
            o.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" fill="{GREEN[lv]}"/>')
    # snake body: each path cell is red from the step the head enters it until the tail leaves it
    for i, (c, r, lv) in enumerate(cells):
        x, y = pos(c, r)
        a = max(i * STEP / T, 0.00001); b = min(free[i] * STEP / T, 0.99999)
        o.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" fill="{SNAKE}" opacity="0">'
                 f'<animate attributeName="opacity" values="0;1;0;0" keyTimes="0;{a:.5f};{b:.5f};1" dur="{T:.2f}s" repeatCount="indefinite" calcMode="discrete"/></rect>')
    for i, (c, r, lv) in enumerate(cells):
        x, y = pos(c, r)
        a = max(i * STEP / T, 0.00001); b = min((i + 1) * STEP / T, 0.99999)
        o.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" fill="{HEAD}" opacity="0">'
                 f'<animate attributeName="opacity" values="0;1;0;0" keyTimes="0;{a:.5f};{b:.5f};1" dur="{T:.2f}s" repeatCount="indefinite" calcMode="discrete"/></rect>')
    label = "Pixel snake eating my GitHub contributions and growing longer with every one"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
            f'shape-rendering="crispEdges" role="img" aria-label="{label}">' + "".join(o) + "</svg>"), final

if __name__ == "__main__":
    cal, out = load(sys.argv)
    svg, final = build(cal)
    open(out, "w").write(svg)
    print(f"wrote {out}: {len(svg)//1024} KB, final snake length {final}")

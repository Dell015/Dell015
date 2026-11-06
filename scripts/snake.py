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


CUR = ["1000000","1100000","1210000","1221000","1222100","1222210",
       "1222221","1222111","1211000","1101100","1000110","0000110"]
CREW = [("RANDEL", "#D11A2A"), ("UI", "#22d3ee"), ("UX", "#facc15"), ("DB", "#a78bfa"), ("ANI", "#f472b6")]

def cursor_svg(name, color, keys, T):
    """keys: [(t_seconds, x, y)] -> a named multiplayer cursor gliding through them."""
    keys = sorted(keys)
    if keys[0][0] > 0: keys.insert(0, (0.0,) + keys[0][1:])
    if keys[-1][0] < T: keys.append((T,) + keys[-1][1:])
    kt = ";".join(f"{min(1, max(0, k[0] / T)):.5f}" for k in keys)
    vs = ";".join(f"{k[1]:.0f} {k[2]:.0f}" for k in keys)
    out_, in_ = [], []
    for r, row in enumerate(CUR):
        for c, ch in enumerate(row):
            if ch == "1": out_.append(f"M{c*2} {r*2}h2v2h-2z")
            elif ch == "2": in_.append(f"M{c*2} {r*2}h2v2h-2z")
    tagw = width(name, 1) + 12
    return (f'<g><animateTransform attributeName="transform" type="translate" dur="{T:.2f}s" repeatCount="indefinite" '
            f'keyTimes="{kt}" values="{vs}"/>'
            f'<path d="{"".join(in_)}" fill="{color}"/><path d="{"".join(out_)}" fill="{WHITE}"/>'
            f'<g transform="translate(12 22)"><rect width="{tagw}" height="15" fill="{color}"/>'
            + ptext(name, 6, 4, 1, BG if color != "#D11A2A" else WHITE) + '</g></g>')

def swarm(cells, T, pos, w, h, ncols):
    """A design team riding along: three cursors chase the snake's head, one marquee-selects
    patches of the graph with a size badge, one hovers the header."""
    import random
    rng = random.Random(15)
    n = len(cells)
    o = []
    def head_xy(i):
        c, r, _ = cells[max(0, min(n - 1, i))]
        x, y = pos(c, r)
        return x + CELL // 2, y + CELL // 2
    every = 5
    for k, (name, col) in enumerate(CREW[1:4]):
        lag = 6 + k * 9
        ox, oy = [(10, 8), (-26, 12), (6, -30)][k]
        keys = []
        for i in range(0, n + every, every):
            x, y = head_xy(i - lag)
            keys.append((i * STEP, x + ox, y + oy))
        o.append(cursor_svg(name, col, keys, T))
    # marquee selections (RANDEL)
    keys = [(0, w - 120, 8)]
    t, gx0, gy0 = 1.0, pos(0, 0)[0], pos(0, 0)[1]
    sels = []
    while t < T - 3:
        cw, ch = rng.randint(4, 12), rng.randint(2, 5)
        c0, r0 = rng.randint(0, max(0, ncols - cw)), rng.randint(0, 7 - ch)
        x0, y0 = pos(c0, r0)
        x1, y1 = x0 + cw * (CELL + GAP) - GAP, y0 + ch * (CELL + GAP) - GAP
        keys += [(t, x0 - 3, y0 - 3), (t + 0.7, x1 + 3, y1 + 3), (t + 1.8, x1 + 20, y1 + 10)]
        sels.append((t, t + 0.7, t + 1.6, x0 - 3, y0 - 3, x1 - x0 + 6, y1 - y0 + 6, f"{cw} X {ch}"))
        t += rng.uniform(3.0, 4.5)
    for (a, b, e, x, y, sw, sh, lab) in sels:
        def k(v): return f"{min(1, max(0, v / T)):.5f}"
        vis = (f'<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;{k(a)};{k(a+.01)};{k(e)};{k(e+.01)};1" '
               f'dur="{T:.2f}s" repeatCount="indefinite" calcMode="discrete"/>')
        grow = lambda attr, full: (f'<animate attributeName="{attr}" values="0;0;{full};{full}" keyTimes="0;{k(a)};{k(b)};1" '
                                   f'dur="{T:.2f}s" repeatCount="indefinite"/>')
        bw = width(lab, 1) + 10
        o.append(f'<g opacity="0">{vis}<rect x="{x}" y="{y}" width="0" height="0" fill="#D11A2A" fill-opacity=".1" '
                 f'stroke="#D11A2A" stroke-width="2">{grow("width", sw)}{grow("height", sh)}</rect>'
                 f'<g transform="translate({x + sw - bw} {y + sh + 4})" opacity="0">'
                 f'<animate attributeName="opacity" values="0;0;1;1" keyTimes="0;{k(b)};{k(b+.01)};1" dur="{T:.2f}s" repeatCount="indefinite" calcMode="discrete"/>'
                 f'<rect width="{bw}" height="13" fill="#D11A2A"/>' + ptext(lab, 5, 3, 1, WHITE) + '</g></g>')
    o.append(cursor_svg(*CREW[0], keys + [(T, w - 120, 8)], T))
    # ANI parks on the header and taps the count
    hx = 16 + 13 * 12 + 14
    keys = [(0, w + 40, 30)]
    t = 0.5
    while t < T:
        keys += [(t, hx + rng.randint(0, 200), 30 + rng.randint(-4, 4)), (t + 2.5, hx + rng.randint(260, 420), 34)]
        t += 5
    o.append(cursor_svg(*CREW[4], keys, T))
    return "".join(o)

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
    W_ = pad * 2 + len(weeks) * (CELL + GAP) - GAP
    height = top + 7 * (CELL + GAP) - GAP + pad + 6
    o = []
    o.append(f'<rect width="{W_}" height="{height}" fill="#0d0d0f"/>')
    o.append(f'<rect x="3" y="3" width="{W_-6}" height="{height-6}" fill="none" stroke="#2a2a30" stroke-width="4"/>')
    for a in (0, W_ - 8):
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
    o.append(swarm(cells, T, pos, W_, height, len(weeks)))
    label = "Pixel snake eating my GitHub contributions while a swarm of multiplayer design cursors chases it"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W_}" height="{height}" viewBox="0 0 {W_} {height}" '
            f'shape-rendering="crispEdges" role="img" aria-label="{label}">' + "".join(o) + "</svg>"), final

if __name__ == "__main__":
    cal, out = load(sys.argv)
    svg, final = build(cal)
    open(out, "w").write(svg)
    print(f"wrote {out}: {len(svg)//1024} KB, final snake length {final}")

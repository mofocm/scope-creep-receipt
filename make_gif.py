"""Renders a Claude Code looking GIF of the scope-creep-receipt mod. Numbers are fake on purpose."""
from PIL import Image, ImageDraw, ImageFont
import os, random, sys

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/Desktop/claude-receipt-meme.gif")
SZ = 21
FONT = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", SZ)
BOLD = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", SZ, index=1)
CW = FONT.getlength("M")
LH = 27
W, H = 1000, 960
PAD = 40
TOPY = 70
COLS = int((W - 2 * PAD) // CW)

BG = (24, 24, 27)
FG = (214, 214, 214)
DIM = (128, 128, 134)
ORANGE = (217, 119, 87)
COL = {"yellow": (229, 192, 123), "cyan": (86, 182, 194), "magenta": (198, 120, 221),
       "blue": (97, 175, 239), "green": (127, 190, 110), "red": (224, 108, 117),
       "dim": DIM, "orange": ORANGE, None: FG}

WIDTH = 40
def dots(l, v): return l + " " + "." * max(2, WIDTH - len(l) - len(v) - 2) + " " + v
def center(t): return " " * max(0, (WIDTH - len(t)) // 2) + t

ASKED = "fix one typo in the readme"
READS, EDITS, CMDS, MIN, TOK = 43, 17, 9, "4.2", "312k"
RECEIPT = [
    ("v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^", "dim", False),
    (center("DEPT. OF ONE SMALL THING"), "yellow", True),
    (center("receipt #0042"), "dim", False),
    ("-" * WIDTH, "dim", False),
    (dots("YOU ASKED FOR", '"fix one typo"'), None, False),
    (dots('tabs opened "just to check"', str(READS)), "cyan", False),
    (dots("side quests started", str(EDITS)), "magenta", False),
    (dots("things run on a hunch", str(CMDS)), "blue", False),
    (dots("min of vibing in limbo", MIN), None, False),
    (dots("tokens spent on intention", TOK), None, False),
    ("-" * WIDTH, "dim", False),
    (dots("TOTAL", "1 thing (allegedly)"), None, True),
    (center("*** FULL ANXIETY COSPLAY ***"), "red", True),
    (center("43 tabs open. it is fine."), "dim", False),
    (center("tip not included. refunds: later"), "dim", False),
    (center("thank you for vibing"), "dim", False),
    (center("▏▎▍▌▋▊▉█ ▕▏▎▍▌▋▊▉█ ▕▏▎▍▌▋▊▉█"), "dim", False),
    ("^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v", "dim", False),
]

# ---- transcript lines: list of segments [(text, color, bold)] or special markers
def seg(*parts): return list(parts)

WELCOME = [
    seg(("╭" + "─" * 52 + "╮", "orange", False)),
    seg(("│ ", "orange", False), ("✻ ", "orange", False), ("Welcome to ", None, False), ("Claude Code", None, True), ("!", None, False), (" " * 29 + "│", "orange", False)),
    seg(("│" + " " * 52 + "│", "orange", False)),
    seg(("│   ", "orange", False), ("/help for help, /status for your current setup", "dim", False), ("  │", "orange", False)),
    seg(("│" + " " * 52 + "│", "orange", False)),
    seg(("│   ", "orange", False), ("cwd: /Users/carlo/projects/my-app", "dim", False), (" " * 16 + "│", "orange", False)),
    seg(("╰" + "─" * 52 + "╯", "orange", False)),
    seg(("", None, False)),
]

FILES = ["README.md", "package.json", "src/index.ts", "src/utils/format.ts", "src/utils/date.ts", "src/components/Button.tsx",
         "src/components/Header.tsx", "src/hooks/useAuth.ts", "docs/setup.md", "docs/api.md", "tsconfig.json", "CHANGELOG.md",
         "src/lib/api.ts", "src/lib/db.ts", "tests/format.test.ts", "CONTRIBUTING.md", ".github/workflows/ci.yml", "src/types.ts"]
random.seed(7)

def tool(name, arg, result):
    return [seg(("● ", "green", False), (name, None, True), (f"({arg})", None, False)),
            seg(("  └ ", "dim", False), (result, "dim", False))]

def tool_calls():
    """43 reads, 17 edits, 9 commands, mixed. Returns a flat list of call blocks."""
    reads = []
    for i in range(READS):
        f = FILES[i % len(FILES)]
        k = i % 3
        if k == 0: reads.append(tool("Read", f, f"Read {random.randint(12, 240)} lines"))
        elif k == 1: reads.append(tool("Search", f'pattern: "recieve", path: "{f.rsplit("/", 1)[0] if "/" in f else "."}"', f"Found {random.randint(1, 14)} files"))
        else: reads.append(tool("Read", f, f"Read {random.randint(12, 240)} lines"))
    edits = [tool("Update", FILES[(i * 5) % len(FILES)], f"Updated {FILES[(i * 5) % len(FILES)]} with {random.randint(1, 6)} additions and {random.randint(1, 4)} removals") for i in range(EDITS)]
    cmds = [tool("Bash", c, r) for c, r in [
        ("git status", "On branch main"), ("npm test", "Tests: 3 failed, 41 passed"), ("npm run lint", "12 warnings"),
        ("git diff --stat", "17 files changed"), ("npm run build", "Build succeeded"), ("ls -la", "total 312"),
        ("grep -rn recieve .", "14 matches"), ("npm test", "Tests: 1 failed, 43 passed"), ("npx prettier --write .", "58 files formatted")]]
    mixed = []
    r, e, c = list(reads), list(edits), list(cmds)
    while r or e or c:
        for lst, n in ((r, 5), (e, 2), (c, 1)):
            for _ in range(n):
                if lst: mixed.append(lst.pop(0))
    return mixed

def glyph_circle(d, x, y, color):
    d.ellipse((x + 3, y + 9, x + 15, y + 21), fill=color)

def draw_line(d, x, y, parts):
    cx = x
    for s, c, b in parts:
        if s.startswith("● ") and c == "green":
            glyph_circle(d, cx, y, COL["green"]); cx += CW * 2; s = s[2:]
        d.text((cx, y), s, font=BOLD if b else FONT, fill=COL[c])
        cx += FONT.getlength(s)

def render(transcript, status=None, receipt_rows=0, button=False, typed=None, flash=False):
    im = Image.new("RGB", (W, H), (10, 10, 12))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((12, 12, W - 12, H - 12), 14, fill=BG)
    for i, col in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse((34 + i * 26, 30, 48 + i * 26, 44), fill=col)
    d.text((W / 2, 38), "claude  —  my-app", font=FONT, fill=DIM, anchor="mm")

    # bottom up
    y_bottom = H - 30
    hint_y = y_bottom - LH
    d.text((PAD + CW * 2, hint_y), "? for shortcuts", font=FONT, fill=DIM)
    box_h = LH + 18
    box_y = hint_y - box_h - 4
    d.rounded_rectangle((PAD, box_y, W - PAD, box_y + box_h), 8, outline=(90, 90, 96), width=2)
    d.text((PAD + 16, box_y + 9), "> " + (typed or ""), font=FONT, fill=FG)
    if typed is not None and (len(typed) % 2 == 0 or typed == ASKED):
        d.rectangle((PAD + 16 + CW * (2 + len(typed)), box_y + 11, PAD + 16 + CW * (3 + len(typed)) - 2, box_y + 11 + LH - 6), fill=FG)

    y = box_y - 8
    # button / receipt band
    if button:
        y -= LH
        d.rounded_rectangle((PAD + CW, y + 1, PAD + CW * 12, y + LH - 2), 6, outline=DIM, width=2)
        d.text((PAD + CW * 2, y + 2), "tear off", font=FONT, fill=FG)
    if receipt_rows:
        y -= LH * receipt_rows
        for i, (s, c, b) in enumerate(RECEIPT[:receipt_rows]):
            color = c
            if i == 12 and flash: color = None
            d.text((PAD + CW, y + i * LH), s, font=BOLD if b else FONT, fill=COL[color])
        y -= 4
    if status:
        y -= LH
        d.text((PAD, y), status, font=FONT, fill=COL["orange"])
        y -= 4

    # transcript tail
    lines = transcript
    room = int((y - TOPY) // LH)
    tail = lines[-room:] if room > 0 else []
    ty = y - LH * len(tail)
    for parts in tail:
        draw_line(d, PAD, ty, parts)
        ty += LH
    return im

frames, durs = [], []
def add(im, ms): frames.append(im); durs.append(ms)

transcript = list(WELCOME)
add(render(transcript, typed=""), 700)
for i in range(1, len(ASKED) + 1):
    add(render(transcript, typed=ASKED[:i]), 55)
add(render(transcript, typed=ASKED), 500)

transcript += [seg(("> " + ASKED, None, False)), seg(("", None, False))]
spin = "✻✽✶✳✢"
state = {"k": 0}
def status(sec, tok):
    state["k"] += 1
    return f"{spin[state['k'] % 5]} Pondering… ({sec}s · ↑ {tok}k tokens · esc to interrupt)"

calls = tool_calls()
blocks_total = len(calls)
cum_tok = 0
for n, block in enumerate(calls):
    transcript += block + [seg(("", None, False))]
    cum_tok += 312 / blocks_total
    sec = int(252 * (n + 1) / blocks_total)
    ms = 420 if n < 4 else 85
    add(render(transcript, status(sec, round(cum_tok, 1))), ms)

transcript += [seg(("● ", "green", False), ("Fixed the typo. ", None, False), ("I also updated 17 files, which felt related.", None, False)), seg(("", None, False))]
add(render(transcript, typed=None), 900)

for n in range(1, len(RECEIPT) + 1):
    add(render(transcript, receipt_rows=n), 150 if n < 12 else 280)
for k in range(6):
    add(render(transcript, receipt_rows=len(RECEIPT), flash=(k % 2 == 0)), 160)
add(render(transcript, receipt_rows=len(RECEIPT), button=True), 3200)

frames[0].save(OUT, save_all=True, append_images=frames[1:], duration=durs, loop=0, optimize=True)
frames[-1].save(OUT.replace(".gif", "-still.png"))
print(OUT, len(frames), "frames", os.path.getsize(OUT) // 1024, "KB")

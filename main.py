#!/usr/bin/env python3
"""One image that sums up the world news of Wednesday 18 November 2026.

Pure standard library: the program draws a newspaper front page pixel by
pixel (own 5x7 bitmap font, own vector shapes) and encodes it as a PNG with
its own encoder. No network, no files read, no timestamps: two runs write
identical bytes.

Run:  python3 main.py            (writes entry.png next to out/ or /output)
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---- palette ------------------------------------------------------------
PAPER = (247, 241, 227)   # warm newsprint
INK = (27, 27, 27)
NAVY = (22, 35, 63)
RED = (179, 35, 42)
GOLD = (201, 162, 39)
GOLD_LT = (232, 196, 90)
TEAL = (31, 111, 107)
BLUE = (46, 90, 136)
SKY = (178, 214, 235)
SEA = (64, 120, 168)
WHITE = (255, 255, 255)
PANEL = (255, 255, 255)
BORDER = (190, 178, 150)
GREY = (96, 92, 82)
LIGHT = (233, 225, 206)
CRIMSON = (178, 44, 54)
GREEN = (46, 125, 70)


# ---- 5x7 bitmap font (own design, '.' empty, '#' filled) ----------------
def _g(*rows):
    return rows


FONT = {
    "A": _g(".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": _g("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": _g(".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": _g("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": _g("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": _g("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": _g(".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": _g("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": _g(".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": _g("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": _g("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": _g("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": _g("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": _g("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    "O": _g(".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": _g("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": _g(".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": _g("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": _g(".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": _g("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": _g("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": _g("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": _g("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": _g("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": _g("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": _g("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": _g(".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    "1": _g("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": _g(".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": _g("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": _g("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": _g("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": _g(".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": _g("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    "8": _g(".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": _g(".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": _g(".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": _g(".....", ".....", ".....", ".....", ".....", ".....", ".##.."),
    ",": _g(".....", ".....", ".....", ".....", ".....", ".##..", ".#..."),
    ":": _g(".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": _g(".....", ".##..", ".##..", ".....", ".##..", ".#...", "....."),
    "-": _g(".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    "'": _g("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "/": _g("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "(": _g("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
    ")": _g("##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."),
    "&": _g(".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "!": _g("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": _g(".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "%": _g("##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"),
    "+": _g(".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "=": _g(".....", ".....", "#####", ".....", "#####", ".....", "....."),
    '"': _g(".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    "|": _g("..#..", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "\u00b7": _g(".....", ".....", ".##..", ".##..", ".....", ".....", "....."),
}


def text_width(text, scale):
    """Pixel width of text at the given scale (6 px advance per glyph)."""
    return len(text) * 6 * scale


def wrap_text(text, scale, max_width):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    words = text.split(" ")
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---- canvas ---------------------------------------------------------------
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.buf = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def px(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i], self.buf[i + 1], self.buf[i + 2] = color

    def fill_rect(self, x, y, w, h, color):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.buf[i], self.buf[i + 1], self.buf[i + 2] = color

    def rect(self, x, y, w, h, color, t=1):
        self.fill_rect(x, y, w, t, color)
        self.fill_rect(x, y + h - t, w, t, color)
        self.fill_rect(x, y, t, h, color)
        self.fill_rect(x + w - t, y, t, h, color)

    def hline(self, x0, x1, y, color, t=1):
        self.fill_rect(min(x0, x1), y, abs(x1 - x0) + 1, t, color)

    def vline(self, x, y0, y1, color, t=1):
        self.fill_rect(x, min(y0, y1), t, abs(y1 - y0) + 1, color)

    def line(self, x0, y0, x1, y1, color, t=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        x, y = x0, y0
        while True:
            self.fill_rect(x - t // 2, y - t // 2, t, t, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def disc(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            dx = int((r * r - (yy - cy) ** 2) ** 0.5) if abs(yy - cy) <= r else 0
            self.hline(cx - dx, cx + dx, yy, color)

    def ring(self, cx, cy, r, color, t=2):
        for k in range(t):
            rr = r - k
            for deg in range(0, 360):
                import math
                a = deg * math.pi / 180.0
                self.px(int(cx + rr * math.cos(a)), int(cy + rr * math.sin(a)), color)

    def poly(self, pts, color):
        """Scanline fill of a simple polygon."""
        import math
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                self.hline(int(xs[k]), int(xs[k + 1]), y, color)

    def star(self, cx, cy, r_out, r_in, color, rot=-90):
        import math
        pts = []
        for i in range(10):
            r = r_out if i % 2 == 0 else r_in
            a = (rot + i * 36) * math.pi / 180.0
            pts.append((int(cx + r * math.cos(a)), int(cy + r * math.sin(a))))
        self.poly(pts, color)

    def draw_text(self, x, y, text, scale, color):
        text = text.upper()
        cx = x
        for ch in text:
            glyph = FONT.get(ch, FONT[" "])
            for row, bits in enumerate(glyph):
                for col, bit in enumerate(bits):
                    if bit == "#":
                        self.fill_rect(cx + col * scale, y + row * scale,
                                       scale, scale, color)
            cx += 6 * scale
        return cx - x

    def text_centered(self, y, text, scale, color, cx=None):
        w = text_width(text, scale)
        x = (self.w - w) // 2 if cx is None else cx - w // 2
        self.draw_text(x, y, text, scale, color)
        return x


# ---- icons (small drawn pictograms, one per story) ------------------------
def icon_flags(c, x, y, s):
    """Three summit flags (US, China, Russia) on poles over a gold ribbon."""
    import math
    # sky
    c.fill_rect(x, y, s, s, SKY)
    # ground
    c.fill_rect(x, y + int(s * 0.78), s, s - int(s * 0.78), (120, 160, 110))
    flags = [
        ("us", (178, 34, 52)),
        ("cn", (222, 41, 16)),
        ("ru", (255, 255, 255)),
    ]
    fw, fh = int(s * 0.26), int(s * 0.20)
    for i, (kind, _) in enumerate(flags):
        px = x + int(s * 0.06) + i * int(s * 0.31)
        py = y + int(s * 0.10)
        c.vline(px + 2, py - int(s * 0.06), py + fh + int(s * 0.42), INK, 3)
        if kind == "us":
            for stripe in range(5):
                col = (178, 34, 52) if stripe % 2 == 0 else WHITE
                c.fill_rect(px + 4, py + stripe * (fh // 5), fw, fh // 5 + 1, col)
            c.fill_rect(px + 4, py, fw // 2, fh // 2, NAVY)
            for gx in range(3):
                for gy in range(2):
                    c.disc(px + 8 + gx * 10, py + 5 + gy * 8, 1, WHITE)
        elif kind == "cn":
            c.fill_rect(px + 4, py, fw, fh, (222, 41, 16))
            c.star(px + 12, py + 9, 6, 2, GOLD_LT)
            c.star(px + 26, py + 6, 3, 1, GOLD_LT)
            c.star(px + 30, py + 13, 3, 1, GOLD_LT)
        else:
            c.fill_rect(px + 4, py, fw, fh // 3 + 1, WHITE)
            c.fill_rect(px + 4, py + fh // 3, fw, fh // 3 + 1, BLUE)
            c.fill_rect(px + 4, py + 2 * fh // 3, fw, fh // 3 + 1, (178, 34, 52))
    # ribbon
    ry = y + int(s * 0.84)
    rw = int(s * 0.84)
    c.fill_rect(x + int(s * 0.08), ry, rw, int(s * 0.12), GOLD)
    label = "SHENZHEN"
    lx = x + int(s * 0.08) + (rw - text_width(label, 2)) // 2
    c.draw_text(lx, ry + (int(s * 0.12) - 14) // 2, label, 2, NAVY)


def icon_bridge(c, x, y, s):
    """Arched bridge over water with a blast above the deck."""
    import math
    c.fill_rect(x, y, s, s, SKY)
    c.fill_rect(x, y + int(s * 0.66), s, s - int(s * 0.66), SEA)
    for k in range(3):
        wy = y + int(s * 0.72) + k * int(s * 0.08)
        c.hline(x + int(s * 0.08), x + int(s * 0.92), wy, WHITE, 2)
    # deck
    c.fill_rect(x + int(s * 0.05), y + int(s * 0.58), int(s * 0.90), int(s * 0.05), INK)
    # arch
    for deg in range(180, 361):
        a = deg * math.pi / 180.0
        bx = int(x + s / 2 + (s * 0.42) * math.cos(a))
        by = int(y + s * 0.58 + (s * 0.30) * math.sin(a))
        c.fill_rect(bx - 2, by - 2, 4, 4, RED)
    # pillars
    c.fill_rect(x + int(s * 0.10), y + int(s * 0.30), 5, int(s * 0.30), INK)
    c.fill_rect(x + int(s * 0.85), y + int(s * 0.30), 5, int(s * 0.30), INK)
    # blast starburst above deck
    bx, by = x + int(s * 0.52), y + int(s * 0.34)
    c.star(bx, by, int(s * 0.20), int(s * 0.07), GOLD_LT)
    c.star(bx, by, int(s * 0.11), int(s * 0.04), RED)


def icon_virus(c, x, y, s):
    """Spiky virus particle."""
    import math
    c.fill_rect(x, y, s, s, (250, 235, 220))
    cx, cy, r = x + s // 2, y + s // 2, int(s * 0.26)
    for k in range(12):
        a = k * 30 * math.pi / 180.0
        x0 = int(cx + r * math.cos(a))
        y0 = int(cy + r * math.sin(a))
        x1 = int(cx + (r + int(s * 0.13)) * math.cos(a))
        y1 = int(cy + (r + int(s * 0.13)) * math.sin(a))
        c.line(x0, y0, x1, y1, CRIMSON, 4)
        c.disc(x1, y1, 4, CRIMSON)
    c.disc(cx, cy, r, CRIMSON)
    c.disc(cx - r // 3, cy - r // 3, r // 3, (214, 90, 100))
    c.disc(cx + r // 3, cy + r // 4, r // 5, (214, 90, 100))


def icon_chip(c, x, y, s):
    """AI chip with pins."""
    c.fill_rect(x, y, s, s, (235, 238, 245))
    body = int(s * 0.58)
    bx, by = x + (s - body) // 2, y + (s - body) // 2
    for k in range(5):
        off = int(s * 0.08) + k * int(s * 0.15)
        c.fill_rect(x + off, by - int(s * 0.07), 5, int(s * 0.07), INK)
        c.fill_rect(x + off, by + body, 5, int(s * 0.07), INK)
        c.fill_rect(bx - int(s * 0.07), y + off, int(s * 0.07), 5, INK)
        c.fill_rect(bx + body, y + off, int(s * 0.07), 5, INK)
    c.fill_rect(bx, by, body, body, NAVY)
    c.fill_rect(bx + 8, by + 8, body - 16, body - 16, (38, 58, 96))
    c.draw_text(bx + 14, by + body // 2 - 4, "AI", 2, GOLD_LT)


def icon_storm(c, x, y, s):
    """Cyclone spiral over a coastline."""
    import math
    c.fill_rect(x, y, s, s, SKY)
    c.fill_rect(x, y + int(s * 0.80), s, s - int(s * 0.80), (150, 190, 140))
    cx, cy = x + s // 2, y + int(s * 0.44)
    prev = None
    for step in range(0, 540, 4):
        a = step * math.pi / 180.0
        r = int(s * 0.05) + step * int(s * 0.055) // 90
        px = int(cx + r * math.cos(a))
        py = int(cy + r * math.sin(a) * 0.85)
        if prev is not None:
            c.line(prev[0], prev[1], px, py, TEAL, 5)
        prev = (px, py)
    c.disc(cx, cy, 6, TEAL)
    # rain
    for k in range(5):
        rx = x + int(s * 0.12) + k * int(s * 0.17)
        c.line(rx, y + int(s * 0.62), rx - 6, y + int(s * 0.74), BLUE, 3)


# ---- page -------------------------------------------------------------------
def draw_page(c):
    # masthead
    c.fill_rect(0, 0, W, 118, NAVY)
    # small globes flanking the title
    for gx in (36, W - 36 - 64):
        c.ring(gx + 32, 59, 30, GOLD_LT, 3)
        c.line(gx + 6, 59, gx + 58, 59, GOLD_LT, 2)
        c.line(gx + 32, 31, gx + 32, 87, GOLD_LT, 2)
        c.disc(gx + 32, 59, 4, GOLD_LT)
    c.text_centered(20, "THE WORLD IN ONE DAY", 6, WHITE)
    c.text_centered(76, "WEDNESDAY  -  18 NOVEMBER 2026", 3, GOLD_LT)
    c.fill_rect(0, 118, W, 6, RED)
    c.text_centered(130, "SIX STORIES FROM A DAY OF SUMMITS, STRIKES AND STORMS", 2, GREY)

    # ---- lead story ----
    lead = (24, 158, 976, 252)
    c.fill_rect(*lead[:2], lead[2], lead[3], PANEL)
    c.rect(*lead[:2], lead[2], lead[3], BORDER, 2)
    c.draw_text(48, 176, "APEC  -  SHENZHEN  -  DIPLOMACY", 2, RED)
    headline = "APEC OPENS AS TRUMP, XI AND PUTIN SET FIRST TRILATERAL SUMMIT"
    lines = wrap_text(headline, 3, 600)
    yy = 206
    for ln in lines:
        c.draw_text(48, yy, ln, 3, INK)
        yy += 24
    deck = ("The Asia-Pacific summit opens in Shenzhen. Trump flies in from "
            "Quad talks in Manila, where leaders unveiled a new maritime "
            "plan. The three leaders meet tomorrow.")
    lines = wrap_text(deck, 2, 600)
    yy += 10
    for ln in lines:
        c.draw_text(48, yy, ln, 2, (58, 54, 46))
        yy += 17
    icon_flags(c, 700, 178, 216)

    # ---- story panels ----
    panels = [
        (24, 426, 476, 256, "UKRAINE  -  EUROPE", "UKRAINE HITS CRIMEA BRIDGE",
         "Kyiv says its strike damaged the key link to the peninsula as "
         "Russia pounds bridges near the capital. Talks loom as leaders "
         "head to China.", icon_bridge),
        (524, 426, 476, 256, "HEALTH  -  UNITED STATES", "US LOSES MEASLES-FREE STATUS",
         "More than 5,400 cases this year, the worst outbreak in over "
         "three decades, as health officials warn the disease is "
         "spreading again.", icon_virus),
        (24, 698, 476, 256, "TECH  -  MARKETS", "NVIDIA REVENUE DOUBLES",
         "The chipmaker reports a revenue boom as Washington tightens AI "
         "chip export curbs, closing a loophole used to reach Chinese "
         "firms.", icon_chip),
        (524, 698, 476, 256, "WEATHER  -  INDIA", "CYCLONE AKVAN NEARS INDIA",
         "The storm bears down on Andhra Pradesh, with landfall expected "
         "on 20 November, as coastal states brace for heavy rain and "
         "high winds.", icon_storm),
    ]
    for (px, py, pw, ph, kicker, head, deck, icon) in panels:
        c.fill_rect(px, py, pw, ph, PANEL)
        c.rect(px, py, pw, ph, BORDER, 2)
        c.draw_text(px + 20, py + 16, kicker, 2, RED)
        lines = wrap_text(head, 3, pw - 40)
        yy = py + 44
        for ln in lines:
            c.draw_text(px + 20, yy, ln, 3, INK)
            yy += 24
        icon(c, px + 20, yy + 8, 108)
        dlines = wrap_text(deck, 2, pw - 20 - 108 - 28)
        dy = yy + 10
        for ln in dlines:
            c.draw_text(px + 20 + 108 + 16, dy, ln, 2, (58, 54, 46))
            dy += 17

    # ---- ticker ----
    c.fill_rect(0, 968, W, 56, NAVY)
    ticker = ("ALSO TODAY: DHONI RETIRES FROM IPL  \u00b7  MONGOLIA PRESIDENT RESIGNS  "
              "\u00b7  RUSSIAN PLANE CRASH KILLS 19  \u00b7  JAPAN PROTESTS AIRSPACE VIOLATION")
    tlines = wrap_text(ticker, 2, W - 48)
    yy = 978
    for ln in tlines:
        c.draw_text(24, yy, ln, 2, WHITE)
        yy += 17


# ---- PNG encoding -----------------------------------------------------------
def png_bytes(c):
    raw = bytearray()
    stride = c.w * 3
    for y in range(c.h):
        raw.append(0)  # filter: none
        raw += c.buf[y * stride:(y + 1) * stride]
    data = zlib.compress(bytes(raw), 9)

    def chunk(kind, payload):
        out = struct.pack(">I", len(payload)) + kind + payload
        out += struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", c.w, c.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", data) + chunk(b"IEND", b""))


def main():
    canvas = Canvas(W, H, PAPER)
    draw_page(canvas)
    blob = png_bytes(canvas)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    try:
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, "entry.png")
        with open(path, "wb") as f:
            f.write(blob)
    except OSError:
        os.makedirs("out", exist_ok=True)
        path = os.path.join("out", "entry.png")
        with open(path, "wb") as f:
            f.write(blob)
    print(f"wrote {path} ({len(blob)} bytes, {W}x{H})")


if __name__ == "__main__":
    main()

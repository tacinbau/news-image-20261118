#!/usr/bin/env python3
"""THE WORLD -- front page summing up world news of Wednesday 18 November 2026.

Pure standard library. Draws a 1024x1024 newspaper front page with a
hand-built bitmap font and a hand-built PNG encoder, then writes it to
/output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png).

Deterministic: no clock, no randomness, no network, no file reads.
Two runs write byte-identical files.
"""

import math
import os
import struct
import zlib

# ---------------------------------------------------------------- canvas

WIDTH = 1024
HEIGHT = 1024

PAPER = (247, 243, 232)   # off-white newsprint
INK = (20, 20, 20)        # headline ink
GREY = (96, 96, 92)       # secondary ink
RED = (185, 28, 28)       # accent red
BLUE = (29, 78, 216)      # accent blue
NAVY = (23, 37, 84)       # dark band behind the lead illustration
SEA = (147, 197, 253)     # pale blue for sea lines
SAND = (214, 186, 120)    # island sand
GOLD = (180, 130, 29)     # third flag-bar colour


# ---------------------------------------------------------------- font
# A 5x7 bitmap font, drawn from scratch. Each glyph is seven rows of five
# bits, "1" for ink. Only capitals, digits and common punctuation: every
# string the page prints is upper-cased before drawing.

FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "*": ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
}

GLYPH_W = 5
GLYPH_H = 7


def text_width(text, scale):
    """Pixel width of text drawn at the given scale (no trailing gap)."""
    if not text:
        return 0
    return len(text) * 6 * scale - scale


def wrap_text(text, max_width, scale):
    """Split text into lines that fit max_width pixels at scale."""
    words = text.split(" ")
    lines = []
    current = ""
    for word in words:
        trial = word if not current else current + " " + word
        if text_width(trial, scale) <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


# ---------------------------------------------------------------- drawing

class Page:
    def __init__(self, width, height, background):
        self.width = width
        self.height = height
        self.pixels = bytearray(background * (width * height))

    def put(self, x, y, colour):
        if 0 <= x < self.width and 0 <= y < self.height:
            i = (y * self.width + x) * 3
            self.pixels[i] = colour[0]
            self.pixels[i + 1] = colour[1]
            self.pixels[i + 2] = colour[2]

    def fill_rect(self, x, y, w, h, colour):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.width, x + w)
        y1 = min(self.height, y + h)
        for yy in range(y0, y1):
            base = (yy * self.width + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.pixels[i] = colour[0]
                self.pixels[i + 1] = colour[1]
                self.pixels[i + 2] = colour[2]

    def hline(self, x, y, w, colour, thick=1):
        self.fill_rect(x, y, w, thick, colour)

    def vline(self, x, y, h, colour, thick=1):
        self.fill_rect(x, y, thick, h, colour)

    def line(self, x0, y0, x1, y1, colour, thick=1):
        """Bresenham line, with square stamps for thickness."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        half = thick // 2
        while True:
            self.fill_rect(x0 - half, y0 - half, thick, thick, colour)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def filled_circle(self, cx, cy, r, colour):
        for yy in range(cy - r, cy + r + 1):
            span = int(math.sqrt(max(0, r * r - (yy - cy) * (yy - cy))))
            self.fill_rect(cx - span, yy, span * 2 + 1, 1, colour)

    def circle_outline(self, cx, cy, r, colour):
        steps = max(24, r * 4)
        for k in range(steps + 1):
            a = 2.0 * math.pi * k / steps
            self.put(cx + int(r * math.cos(a)), cy + int(r * math.sin(a)), colour)

    def arc(self, cx, cy, r, start_deg, end_deg, colour):
        """Plot an arc of a circle, angles in degrees, 0 = east."""
        steps = max(8, int(abs(end_deg - start_deg)))
        for k in range(steps + 1):
            a = math.radians(start_deg + (end_deg - start_deg) * k / steps)
            self.put(cx + int(r * math.cos(a)), cy + int(r * math.sin(a)), colour)

    def wave(self, x0, x1, base_y, amp, colour, thick=1):
        """A gentle sine wave line, left to right."""
        prev = None
        for x in range(x0, x1 + 1):
            y = base_y + int(amp * math.sin((x - x0) * 0.09))
            if prev is not None:
                self.line(prev[0], prev[1], x, y, colour, thick)
            prev = (x, y)

    def draw_text(self, x, y, text, scale, colour):
        """Draw upper-cased text; unknown glyphs become a blank."""
        clean = text.upper().replace("—", "-").replace("’", "'")
        cx = x
        for ch in clean:
            glyph = FONT.get(ch)
            if glyph is None:
                cx += 6 * scale
                continue
            for row in range(GLYPH_H):
                bits = glyph[row]
                for col in range(GLYPH_W):
                    if bits[col] == "1":
                        self.fill_rect(
                            cx + col * scale, y + row * scale,
                            scale, scale, colour,
                        )
            cx += 6 * scale
        return cx

    def draw_text_centred(self, cx, y, text, scale, colour):
        self.draw_text(cx - text_width(text.upper(), scale) // 2, y, text, scale, colour)

    def draw_block(self, x, y, lines, scale, colour, leading):
        for line in lines:
            self.draw_text(x, y, line, scale, colour)
            y += leading
        return y


# ---------------------------------------------------------------- PNG

def _chunk(kind, data):
    out = struct.pack(">I", len(data))
    out += kind
    out += data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def encode_png(page):
    """Minimal deterministic PNG: RGB, no interlace, filter 0, level 6."""
    raw = bytearray()
    row_len = page.width * 3
    for y in range(page.height):
        raw.append(0)  # filter type 0 (None) on every row
        start = y * row_len
        raw += page.pixels[start:start + row_len]
    ihdr = struct.pack(
        ">IIBBBBB", page.width, page.height, 8, 2, 0, 0, 0,
    )
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", ihdr)
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 6))
    png += _chunk(b"IEND", b"")
    return png


# ---------------------------------------------------------------- content

MARGIN = 28
LEFT = MARGIN
RIGHT = WIDTH - MARGIN
FULL = RIGHT - LEFT
COL_W = (FULL - 24) // 2
RIGHT_COL_X = LEFT + COL_W + 24

LEAD_HEADLINE = "U.S. STRIKES IRAN'S QESHM ISLAND AS IRAN HITS BAHRAIN AND KUWAIT"
LEAD_BODY = (
    "US FIGHTER JETS STRUCK A REVOLUTIONARY GUARD MISSILE SITE ON QESHM "
    "ISLAND. IRAN ANSWERED WITH DRONES AIMED AT BAHRAIN AND KUWAIT, "
    "TARGETING US RADAR AND PATRIOT MISSILE SITES."
)

KERCH_HEADLINE = "KERCH BRIDGE PARTLY COLLAPSES UNDER UKRAINIAN ATTACK"
KERCH_BODY = (
    "UKRAINE STRUCK THE BRIDGE LINKING RUSSIA TO CRIMEA FOR A SECOND DAY. "
    "PART OF ITS ROAD SPAN COLLAPSED INTO THE STRAIT BELOW."
)

SHENZHEN_HEADLINE = "SHENZHEN HOSTS APEC AS TRUMP, XI AND PUTIN PREPARE TRILATERAL SUMMIT"
SHENZHEN_BODY = (
    "XI JINPING HOSTS THE APEC SUMMIT IN SHENZHEN AND MET PUTIN THERE. "
    "TRUMP, XI AND PUTIN HOLD A FIRST-EVER TRILATERAL SUMMIT TOMORROW, "
    "AFTER TRUMP'S QUAD TALKS IN MANILA."
)

PELTOLA_HEADLINE = "PELTOLA WINS ALASKA SENATE SEAT"
PELTOLA_BODY = "DEMOCRATS NOW HOLD 56 SEATS IN THE US SENATE."

EBOLA_HEADLINE = "EBOLA IN DR CONGO MORE THAN DOUBLES"
EBOLA_BODY = (
    "OVER 11,000 CASES AND 5,400 DEATHS. NEARLY 3 IN 4 INFECTED "
    "CHILDREN UNDER 5 DIE."
)

TICKER = [
    "CATEGORY 5 CYCLONE XAVIER HITS NORTHERN COOK ISLANDS",
    "RUSSIAN MILITARY PLANE CRASHES IN SIBERIA, 19 DEAD",
    "6.0 QUAKE STRIKES PAPUA NEW GUINEA; 5.3 IN ROMANIA",
    "US LOSES MEASLES-FREE STATUS AFTER 26 YEARS",
    "ISRAEL'S PRESIDENT TAPS EISENKOT TO FORM GOVERNMENT",
    "COLD KILLS DISPLACED PEOPLE IN GAZA TENTS",
    "MS DHONI RETIRES FROM IPL",
    "MICROSOFT UNVEILS SEVEN IN-HOUSE AI MODELS",
]


# ---------------------------------------------------------------- artwork

def draw_lead_art(page, x, y, w, h):
    """Abstract Persian Gulf scene: sea, missile-trail arcs, target dots."""
    page.fill_rect(x, y, w, h, NAVY)
    # Sea at the bottom of the band.
    page.wave(x + 8, x + w - 8, y + h - 18, 3, SEA, 2)
    page.wave(x + 8, x + w - 8, y + h - 8, 3, SEA, 2)
    page.draw_text(x + 14, y + 10, "THE PERSIAN GULF", 2, SEA)
    # Small jet silhouette (triangle bar) at the left, trails arcing right.
    page.fill_rect(x + 30, y + 34, 26, 6, PAPER)
    page.line(x + 56, y + 37, x + 78, y + 37, PAPER, 3)
    # Two shallow arcs, kept inside the band: their centres sit well below
    # it, so only the cap of each circle shows.
    page.arc(x + 330, y + 200, 170, 240, 300, PAPER)
    page.arc(x + 330, y + 215, 185, 245, 295, RED)
    # Island under the Qeshm target.
    page.filled_circle(x + 660, y + 40, 18, SAND)
    # Targets: red dots with paper labels.
    page.filled_circle(x + 660, y + 38, 7, RED)
    page.circle_outline(x + 660, y + 38, 12, RED)
    page.draw_text(x + 678, y + 31, "QESHM", 2, PAPER)
    for tx, ty, label in ((x + 470, y + 26, "BAHRAIN"), (x + 330, y + 22, "KUWAIT")):
        page.filled_circle(tx, ty, 7, RED)
        page.circle_outline(tx, ty, 12, RED)
        page.draw_text(tx - text_width(label, 2) // 2, ty + 18, label, 2, PAPER)


def draw_bridge_art(page, x, y, w, h):
    """Broken Kerch Bridge: two deck spans, a fallen span, water below."""
    deck_y = y + 16
    # Left span (Russia side) and right span (Crimea side).
    page.fill_rect(x, deck_y, 190, 8, INK)
    page.fill_rect(x + w - 190, deck_y, 190, 8, INK)
    # Support pillars.
    page.fill_rect(x + 60, deck_y + 8, 10, 26, INK)
    page.fill_rect(x + w - 70, deck_y + 8, 10, 26, INK)
    # Fallen middle span, tilted down into the strait.
    page.line(x + 196, deck_y + 4, x + w - 196, deck_y + 32, INK, 7)
    # Water.
    page.wave(x, x + w, y + h - 14, 3, BLUE, 2)
    page.wave(x, x + w, y + h - 6, 3, BLUE, 2)
    page.draw_text(x + 4, deck_y - 14, "RUSSIA", 2, GREY)
    label = "CRIMEA"
    page.draw_text(x + w - text_width(label, 2) - 4, deck_y - 14, label, 2, GREY)


def draw_skyline_art(page, x, y, w, h):
    """Shenzhen skyline under three coloured bars for the three leaders."""
    # Legend row: coloured squares plus country names.
    legend = [(RED, "USA"), (BLUE, "CHINA"), (GOLD, "RUSSIA")]
    lx = x + 4
    for colour, name in legend:
        page.fill_rect(lx, y + 2, 12, 12, colour)
        page.draw_text(lx + 18, y + 2, name, 2, INK)
        lx += 18 + text_width(name, 2) + 26
    # Skyline blocks first, then the three tall bars on top of them.
    base = y + h - 4
    heights = [26, 30, 22, 28, 18, 30, 24, 28, 20]
    sx = x
    for bh in heights:
        page.fill_rect(sx, base - bh, 34, bh, INK)
        sx += 52
    bars = [(RED, 26), (BLUE, 30), (GOLD, 22)]
    bx = x + 30
    for colour, bh in bars:
        page.fill_rect(bx, base - bh, 22, bh, colour)
        bx += 150
    page.hline(x, base, w, INK, 2)


# ---------------------------------------------------------------- layout

def build_page():
    page = Page(WIDTH, HEIGHT, PAPER)

    # ---- masthead ----
    page.draw_text_centred(WIDTH // 2, 16, "THE WORLD", 10, INK)
    page.hline(LEFT, 100, FULL, INK, 2)
    page.draw_text_centred(WIDTH // 2, 108, "WEDNESDAY, 18 NOVEMBER 2026", 3, INK)
    page.draw_text_centred(
        WIDTH // 2, 134, "THE DAY'S WORLD NEWS IN ONE IMAGE", 2, RED,
    )
    page.hline(LEFT, 156, FULL, RED, 3)
    page.hline(LEFT, 162, FULL, INK, 1)

    # ---- lead story ----
    y = 176
    page.draw_text(LEFT, y, "LEAD STORY: MIDDLE EAST", 2, RED)
    y += 22
    headline = wrap_text(LEAD_HEADLINE, FULL, 4)
    y = page.draw_block(LEFT, y, headline, 4, INK, 30)
    y += 6
    body = wrap_text(LEAD_BODY, FULL, 2)
    y = page.draw_block(LEFT, y, body, 2, INK, 17)
    y += 10
    draw_lead_art(page, LEFT, y, FULL, 80)
    y += 80 + 12
    page.hline(LEFT, y, FULL, INK, 2)
    y += 10

    # ---- stories 2 and 3, side by side ----
    row_top = y
    row_end = row_top
    for col_x, kicker, headline_text, body_text, art in (
        (LEFT, "UKRAINE", KERCH_HEADLINE, KERCH_BODY, draw_bridge_art),
        (RIGHT_COL_X, "ASIA-PACIFIC", SHENZHEN_HEADLINE, SHENZHEN_BODY, draw_skyline_art),
    ):
        cy = row_top
        page.draw_text(col_x, cy, kicker, 2, RED)
        cy += 22
        lines = wrap_text(headline_text, COL_W, 3)
        cy = page.draw_block(col_x, cy, lines, 3, INK, 23)
        cy += 6
        lines = wrap_text(body_text, COL_W, 2)
        cy = page.draw_block(col_x, cy, lines, 2, INK, 17)
        cy += 8
        art(page, col_x, cy, COL_W, 52)
        row_end = max(row_end, cy + 52)
    y = row_end + 12
    page.hline(LEFT, y, FULL, INK, 2)
    y += 10

    # ---- stories 4 and 5, compact ----
    row_top = y
    row_end = row_top
    for col_x, kicker, headline_text, body_text in (
        (LEFT, "UNITED STATES", PELTOLA_HEADLINE, PELTOLA_BODY),
        (RIGHT_COL_X, "HEALTH", EBOLA_HEADLINE, EBOLA_BODY),
    ):
        cy = row_top
        page.draw_text(col_x, cy, kicker, 2, RED)
        cy += 22
        lines = wrap_text(headline_text, COL_W, 3)
        cy = page.draw_block(col_x, cy, lines, 3, INK, 23)
        cy += 6
        lines = wrap_text(body_text, COL_W, 2)
        cy = page.draw_block(col_x, cy, lines, 2, INK, 17)
        row_end = max(row_end, cy)
    y = row_end + 10
    page.hline(LEFT, y, FULL, INK, 2)
    y += 10

    # ---- ticker strip ----
    band_h = 4 + 14 + 2 + 8 * 15 + 4
    page.fill_rect(LEFT, y, FULL, band_h, RED)
    ty = y + 4
    page.draw_text(LEFT + 10, ty, "ALSO TODAY", 2, PAPER)
    ty += 16
    for item in TICKER:
        page.fill_rect(LEFT + 10, ty + 3, 8, 8, PAPER)
        page.draw_text(LEFT + 26, ty, item, 2, PAPER)
        ty += 15
    y += band_h + 6

    # ---- footer ----
    page.draw_text_centred(
        WIDTH // 2, y, "18 NOVEMBER 2026 - EVENTS REPORTED ON THIS DAY", 2, INK,
    )
    return page


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = encode_png(build_page())
    with open(os.path.join(out_dir, "entry.png"), "wb") as fh:
        fh.write(data)


if __name__ == "__main__":
    main()

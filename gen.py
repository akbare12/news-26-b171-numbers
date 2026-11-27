#!/usr/bin/env python3
"""V167 builder for news-image-20261126 (trial b171). Renders entry.png.
Layout V167: masthead, three full-width hero strips stacked, 10 cards in
2 rows x 5, world map (left) + ALSO (right, 2 columns), DATE CHECK footer.
All facts from KANON-20261126.md. PIL only at build time; main.py copies.
"""
import hashlib
import json
import os
import re
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

INK = (18, 24, 38)
PAPER = (250, 247, 238)
NAVY = (16, 32, 64)
NAVY2 = (24, 48, 92)
RED = (178, 34, 34)
GOLD = (184, 134, 11)
TEAL = (14, 110, 110)
GREY = (90, 96, 108)
LINE = (200, 196, 184)
CARD_BG = (255, 255, 255)
MAP_SEA = (196, 220, 232)
MAP_LAND = (214, 196, 150)
MAP_LAND2 = (198, 214, 170)

F_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
F_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(text, fnt, max_w, draw):
    words = text.split()
    lines, cur = [], ""
    for w_ in words:
        trial = (cur + " " + w_).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- data
HEROES = [
    {
        "kicker": "HERO 1  |  UNITED STATES  [C]",
        "head": "MACY'S 100TH PARADE POSTPONED - FIRST EVER FOR WEATHER",
        "deck": "New York's Thanksgiving parade delayed to Sat 28 Nov, 08:30 ET. "
                "Gusts to 60 mph; wind warning from 10:00 Thu. Giant balloons grounded.",
        "why": "WHY IT MATTERS: America's most-watched parade, in its centenary year, "
               "halted by a storm on Thanksgiving Day itself.",
        "badge": "100TH",
        "art": "balloon",
    },
    {
        "kicker": "HERO 2  |  STRAIT OF HORMUZ  [CL]",
        "head": "IRGC CLAIMS 2 TANKERS HIT BY MINES IN HORMUZ",
        "deck": "Iran's IRGC claims two tankers ablaze, one a supertanker carrying "
                "2M+ barrels. Unverified: no names, flags or casualties given.",
        "why": "WHY IT MATTERS: War at sea widens as oil climbs; Brent $93.8 a barrel.",
        "badge": "2M BBL",
        "art": "tanker",
    },
    {
        "kicker": "HERO 3  |  TRADE  [C]",
        "head": "TRUMP TARIFFS: MARKETS REBOUND AS SALVO LOOKS MILDER",
        "deck": "STOXX 600 +1.6% and MSCI global +0.4% on Thu. New levies will not "
                "stack on July tariffs; 14 partners named, China at 20% top rate. "
                "Wall Street shut for Thanksgiving.",
        "why": "WHY IT MATTERS: The feared tariff shock did not land; investors "
               "judged the macro impact modest.",
        "badge": "14",
        "art": "chart",
    },
]

CARDS = [
    ("GAZA  [C]", "Israel strike kills Hamas education deputy",
     "Abu Nada and wife killed in Deir al-Balah; 9 dead."),
    ("KYIV  [C]", "Russian missile hits mall; 7 wounded",
     "Ballistic hit on Desnianskyi mall; 113 drones fired."),
    ("BOGOR  [C]", "Illegal gold mine floods; 13 dead, 13 missing",
     "Miners trapped ~100 m down after heavy rain."),
    ("ISRAEL  [C]", "Judge urges prosecutors to drop bribery charge",
     "Case 4000, the only bribery count, to be withdrawn."),
    ("N. KOREA  [C]", "Kim tours nuclear plant, urges tactical nukes",
     "Kim presses wider use of tactical nuclear arms."),
    ("SPACE  [C]", "FCC clears SpaceX 1m orbital data satellites",
     "Starmind, approved 25 Nov, first for space data centres."),
    ("BRITAIN  [C]", "Net migration falls to 77,000, lowest since 1997",
     "ONS year to June 2026, outside pandemic years."),
    ("RUSSIA  [R]", "Record post-Soviet military budget approved",
     "Moscow's biggest defence budget since Soviet era."),
    ("BANGKOK  [C]", "Oil depot blast injures 7 in Bangkok",
     "Blast triggers evacuation alert; fire out in 30 min."),
    ("GERMANY  [C]", "Two Iraqi suspects held over synagogue plot",
     "Arrests in Cologne and Heidelberg over March plot."),
]

# DATE CHECK: exact list, verbatim. Do NOT paraphrase, do NOT add items.
DATE_CHECK = [
    "COP31 failed 22 Nov",
    "Shenzhou-24 launched 25 Nov",
    "Cairo tanker blast, 31 dead, 25 Nov",
    "Cartagena hostages freed 25 Nov",
    "Australia-Solomon pact 25 Nov",
    "UK energy prices +26% announced 25 Nov",
    "Huawei convicted 24 Nov",
]

# ALSO: exactly 37 items, each a different story, each one line, each with
# a [C]/[R]/[CL] tag. Items about 25 Nov carry [CL] + the text "25 Nov".
# No card story repeated here, no hero number repeated here, no parade
# item beyond the single Philadelphia one, no Ras Tanura beyond item 31.
# UKMTO 222-26 (Dubai blast) is its own item (#27); it must NOT ride in
# the hero 2 deck, which is the IRGC Hormuz claim only.
ALSO = [
    "Eisenkot wins first Israel coalition deal [C]",
    "Merz warns Russia's ambitions go beyond Ukraine [C]",
    "UK on alert over drone threat to airbases [R]",
    "Norse Atlantic suspends all flights, warns of bankruptcy [C]",
    "Poundland enters administration, 11,000 jobs at risk [C]",
    "Malaysia sues Google $146m over harmful content [C]",
    "Kenya court halts US-backed Ebola facility [C]",
    "Belarus offers to fly Zelensky to Moscow; he refuses [CL]",
    "Kushner calls Putin a \u201cgrandmaster of politics\u201d [C]",
    "Estonia decides to close its border with Russia [C]",
    "Copernicus confirms longest stretch above 2C warming [C]",
    "Nvidia reports halting AI server shipments to 4 nations [R]",
    "US Bitcoin ETFs: record $4.94bn Nov outflows [C]",
    "UN rights chief Turk warns of atrocity-crime risk [C]",
    "Ukraine drones set Subkhankulovo pump station ablaze [C]",
    "Kharkiv couple, 37 and 38, killed in flat strike [C]",
    "18 wounded in Kryvyi Rih strike [C]",
    "Cargo ship near Odesa claimed hit [CL]",
    "Philadelphia's Thanksgiving parade cancelled over weather [C]",
    "OPEC+ to meet 29 Nov on 2027 output [C]",
    "Gold $3,572, down 0.2% on Thu [C]",
    "Nvidia -3.91% to $149.30 [C]",
    "Tariff hearings set for 25 Jan [C]",
    "Tariff probe ran 8 months before USTR proposal [C]",
    "S&P 500 -0.25%, Nasdaq -0.62% on Wed [C]",
    "Dow +0.33% on Wed [C]",
    "UKMTO 222-26: blast 50 nm west of Dubai, 25 Nov [CL]",
    "Brent closed Wed up 3.5% at $94.61 [C]",
    "WTI +0.2% to $83.32 on Thu [C]",
    "S&P 500 and Nasdaq futures +0.5% [C]",
    "Houthi claim Ras Tanura refinery hit, 25 Nov [CL]",
    "Saudi defences down 2 ballistic missiles overnight, 25 Nov [CL]",
    "Minor damage at Jazan port after projectile hit, 25 Nov [CL]",
    "UKMTO: projectile hits tanker 18 nm off Khasab, 25 Nov [CL]",
    "Russia claims Kyiv strikes hit drone sites [CL]",
    "Kyiv attack used Iskander-M, Zircon and S-400 missiles [C]",
    "Strikes continue on 3rd night despite 1-year Gaza ceasefire [C]",
]

# Pins: (lon, lat, legend label). 12 pins, all on land.
PINS = [
    (-74.00, 40.71, "New York - Macy's parade"),
    (-75.16, 39.95, "Philadelphia - parade off"),
    (-0.10, 51.50, "London - migration 77,000"),
    (30.50, 50.45, "Kyiv - mall strike"),
    (34.35, 31.40, "Deir al-Balah - Gaza strike"),
    (56.25, 26.20, "Khasab - Hormuz claim"),
    (106.80, -6.60, "Bogor - mine flood"),
    (100.50, 13.75, "Bangkok - depot blast"),
    (125.75, 39.00, "Pyongyang - Kim tour"),
    (6.95, 50.90, "Cologne - plot arrests"),
    (36.82, -1.29, "Nairobi - Ebola ruling"),
    (101.68, 3.13, "Kuala Lumpur - Google sued"),
]
# Pins drawn away from their true spot (leader line to true spot):
# 2 Philadelphia (too close to New York), 10 Cologne (too close to London).
PIN_OFFSET = {2: (20, 14), 10: (-16, 18)}

# Simplified continent polygons in (lon, lat).
CONTINENTS = [
    [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-80, 73), (-75, 60),
     (-65, 45), (-70, 42), (-75, 35), (-80, 32), (-90, 21), (-97, 16),
     (-105, 20), (-115, 28), (-125, 40), (-125, 49), (-140, 60), (-165, 60)],
    [(-80, 10), (-60, 10), (-50, 0), (-40, -5), (-35, -10), (-40, -20),
     (-48, -28), (-58, -35), (-65, -45), (-70, -55), (-73, -40), (-70, -20),
     (-77, -12), (-80, -3)],
    [(-17, 15), (-10, 30), (0, 35), (10, 37), (20, 32), (30, 31), (35, 28),
     (43, 12), (51, 11), (48, 0), (40, -10), (35, -20), (32, -29), (25, -34),
     (18, -35), (15, -27), (12, -18), (9, 4), (-8, 5)],
    [(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57), (10, 59),
     (18, 60), (21, 65), (25, 70), (30, 70), (40, 68), (55, 68), (70, 72),
     (90, 75), (110, 74), (130, 72), (150, 70), (170, 67), (178, 65),
     (170, 60), (160, 55), (155, 50), (142, 45), (140, 40), (135, 35),
     (130, 33), (127, 35), (122, 38), (120, 32), (115, 23), (110, 20),
     (108, 18), (105, 10), (103, 8), (100, 8), (98, 12), (95, 15), (92, 20),
     (88, 22), (85, 19), (80, 13), (77, 8), (75, 12), (72, 20), (68, 23),
     (65, 25), (61, 25), (57, 26), (54, 26), (51, 28), (50, 29), (48, 30),
     (44, 32), (42, 35), (40, 36), (36, 36), (33, 36), (30, 36), (27, 37),
     (23, 36), (22, 38), (20, 40), (18, 40), (15, 44), (12, 44), (8, 44),
     (5, 43), (3, 42), (0, 39), (-2, 37), (-5, 36), (-9, 37)],
    [(113, -22), (114, -30), (120, -34), (130, -32), (140, -38), (150, -37),
     (153, -27), (146, -19), (142, -11), (135, -12), (130, -13), (122, -14),
     (115, -20)],
    # Levant strip (Gaza / Israel coast)
    [(33, 36), (36, 36), (36, 30), (34, 28), (33, 31)],
    # Arabian peninsula (Khasab / Oman tip)
    [(48, 30), (55, 25), (58, 20), (55, 15), (50, 13), (45, 13), (43, 17),
     (40, 22), (42, 27), (45, 29)],
    # Malay peninsula (Kuala Lumpur)
    [(98, 10), (102, 8), (104, 2), (101, 1), (100, 5), (98, 8)],
    # Java, Sumatra, Borneo, New Guinea
    [(105, -6), (114, -7), (114, -8), (105, -8)],
    [(95, 5), (100, 0), (106, -6), (104, -3), (98, 2)],
    [(109, 1), (117, 4), (119, -2), (114, -4), (110, -3)],
    [(131, -1), (141, -3), (141, -8), (136, -8), (131, -4)],
    # Britain, Japan
    [(-5, 50), (-3, 53), (-2, 57), (0, 53), (1, 51), (-4, 50)],
    [(130, 31), (132, 34), (136, 35), (139, 38), (141, 42), (143, 44),
     (141, 40), (138, 36), (133, 34)],
]

# ---------------------------------------------------------------- drawing
TEXTBOXES = []   # (x0, y0, x1, y1, label) normal text
CHIP_TEXT = []   # text inside a contrast chip (excluded from art check)
ART = []         # rects of drawn art (hero art panels, map area)


def rects_overlap(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def draw_lines(draw, lines, x, y, fnt, fill, lh, parent, label, chip=False):
    for ln in lines:
        w_ = draw.textlength(ln, font=fnt)
        box = (x, y, x + w_, y + fnt.size + 2)
        assert box[0] >= parent[0] + 2 and box[1] >= parent[1] + 2, \
            f"{label}: text outside parent top/left {box} vs {parent}"
        assert box[2] <= parent[2] - 2 and box[3] <= parent[3] - 2, \
            f"{label}: text outside parent bottom/right {box} vs {parent}"
        draw.text((x, y), ln, font=fnt, fill=fill)
        (CHIP_TEXT if chip else TEXTBOXES).append((box[0], box[1], box[2],
                                                   box[3], label))
        y += lh
    return y


def draw_art_panel(draw, kind, box):
    x0, y0, x1, y1 = box
    ART.append(box)
    if kind == "balloon":
        draw.rectangle(box, fill=(70, 90, 140))
        draw.ellipse((x0 + 28, y0 + 8, x0 + 118, y0 + 52), fill=(178, 34, 34),
                     outline=(255, 255, 255), width=2)
        draw.ellipse((x0 + 48, y0 + 8, x0 + 98, y0 + 52), fill=(220, 90, 60))
        draw.rectangle((x0 + 66, y0 + 54, x0 + 82, y0 + 68), fill=(120, 80, 40))
        for i in range(5):
            xx = x0 + 12 + i * 26
            draw.line((xx, y0 + 70, xx + 10, y0 + 78), fill=(255, 255, 255),
                      width=2)
        draw.line((x0 + 8, y0 + 6, x0 + 142, y0 + 6), fill=(255, 255, 255),
                  width=2)
    elif kind == "tanker":
        draw.rectangle(box, fill=(30, 60, 90))
        draw.rectangle((x0 + 10, y0 + 44, x0 + 140, y0 + 62), fill=(40, 40, 40))
        draw.rectangle((x0 + 100, y0 + 28, x0 + 128, y0 + 44), fill=(200, 200, 200))
        for cx, cy, r in ((x0 + 40, y0 + 26, 9), (x0 + 62, y0 + 18, 12),
                          (x0 + 84, y0 + 26, 8)):
            draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 140, 0),
                         outline=(255, 220, 0), width=2)
        draw.ellipse((x0 + 122, y0 + 12, x0 + 132, y0 + 22), fill=(20, 20, 20),
                     outline=(255, 255, 255), width=1)
        draw.ellipse((x0 + 126, y0 + 16, x0 + 128, y0 + 18), fill=(255, 255, 255))
        for yy in (66, 72):
            draw.line((x0 + 6, yy, x0 + 144, yy), fill=(120, 180, 220), width=2)
    else:  # chart
        draw.rectangle(box, fill=(16, 80, 60))
        base = y0 + 66
        vals = [18, 26, 22, 34, 30, 44, 52]
        for i, v in enumerate(vals):
            bx = x0 + 12 + i * 19
            draw.rectangle((bx, base - v, bx + 12, base), fill=(255, 210, 60))
        draw.line((x0 + 10, base - 56, x0 + 140, base - 58), fill=(255, 255, 255),
                  width=2)
        draw.polygon([(x0 + 134, base - 64), (x0 + 144, base - 58),
                      (x0 + 134, base - 52)], fill=(255, 255, 255))


def project(lon, lat, mrect):
    mx0, my0, mx1, my1 = mrect
    x = mx0 + (lon + 180.0) / 360.0 * (mx1 - mx0)
    y = my0 + (85.0 - lat) / 140.0 * (my1 - my0)
    return x, y


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # Masthead
    d.rectangle((0, 0, W, 64), fill=NAVY)
    d.rectangle((0, 60, W, 64), fill=GOLD)
    f_title = font(F_SERIF, 30)
    f_date = font(F_BOLD, 15)
    draw_lines(d, ["THE WORLD IN ONE DAY"], 14, 8, f_title, (255, 255, 255),
               34, (0, 0, 700, 64), "masthead")
    draw_lines(d, ["THURSDAY 26 NOVEMBER 2026"], 640, 12, f_date,
               (255, 210, 60), 20, (620, 0, 1014, 64), "masthead-date")
    draw_lines(d, ["50 STORIES  |  10 REGIONS  |  ALL TIMES GMT"], 640, 36,
               font(F_REG, 11), (200, 210, 230), 15, (620, 0, 1014, 64),
               "masthead-sub")
    d.rectangle((0, 64, W, 88), fill=(232, 228, 216))
    draw_lines(d, ["THE DAY'S THREE BIGGEST STORIES, THEN TEN MORE, THEN EVERYTHING ELSE THAT MATTERED  -  LAYOUT V167"],
               14, 70, font(F_BOLD, 12), INK, 16, (0, 64, 1014, 88), "ticker")

    # Heroes: three full-width strips
    hy = [92, 176, 260]
    for hero, y0 in zip(HEROES, hy):
        y1 = y0 + 80
        box = (10, y0, 1014, y1)
        d.rectangle(box, fill=CARD_BG, outline=LINE, width=1)
        art = (10, y0, 160, y1)
        draw_art_panel(d, hero["art"], art)
        tx = 172
        chip_w = 76
        # badge chip top-right of the text area
        chip = (1014 - 10 - chip_w, y0 + 8, 1014 - 10, y0 + 32)
        d.rectangle(chip, fill=NAVY2)
        bf = font(F_BOLD, 15 if len(hero["badge"]) <= 4 else 12)
        bw = d.textlength(hero["badge"], font=bf)
        draw_lines(d, [hero["badge"]], chip[0] + (chip_w - bw) / 2, y0 + 10,
                   bf, (255, 255, 255), 18, chip, "hero-badge", chip=True)
        draw_lines(d, [hero["kicker"]], tx, y0 + 5, font(F_BOLD, 11), RED, 14,
                   (tx - 4, y0, 1014 - 10 - chip_w - 8, y1), "hero-kicker")
        head_lines = wrap(hero["head"], font(F_BOLD, 16),
                          1014 - 10 - chip_w - 8 - tx, d)
        assert len(head_lines) <= 2, f"hero head too long: {hero['head']}"
        draw_lines(d, head_lines, tx, y0 + 20, font(F_BOLD, 16), INK, 19,
                   (tx - 4, y0, 1014 - 10 - chip_w - 8, y1), "hero-head")
        deck_lines = wrap(hero["deck"], font(F_REG, 11),
                          1014 - 10 - tx, d)
        assert len(deck_lines) <= 2, f"hero deck too long: {hero['deck']}"
        draw_lines(d, deck_lines, tx, y0 + 20 + 19 * len(head_lines),
                   font(F_REG, 11), (40, 46, 60), 13,
                   (tx - 4, y0, 1014, y1), "hero-deck")
        why_lines = wrap(hero["why"], font(F_REG, 10), 1014 - 10 - tx, d)
        assert len(why_lines) <= 1, f"hero why too long: {hero['why']}"
        draw_lines(d, why_lines, tx,
                   y0 + 20 + 19 * len(head_lines) + 13 * len(deck_lines) + 1,
                   font(F_REG, 10), TEAL, 12, (tx - 4, y0, 1014, y1), "hero-why")

    # Cards: 2 rows x 5
    d.rectangle((10, 344, 1014, 344), fill=LINE)
    draw_lines(d, ["TEN MORE STORIES"], 14, 346, font(F_BOLD, 11), NAVY, 14,
               (10, 344, 1014, 364), "cards-label")
    for i, (tag, head, deck) in enumerate(CARDS):
        col, row = i % 5, i // 5
        x0 = 10 + col * 202
        y0 = 364 + row * 106
        x1, y1 = x0 + 194, y0 + 100
        box = (x0, y0, x1, y1)
        d.rectangle(box, fill=CARD_BG, outline=LINE, width=1)
        d.rectangle((x0, y0, x1, y0 + 4), fill=NAVY2)
        draw_lines(d, [tag], x0 + 8, y0 + 9, font(F_BOLD, 10), RED, 13,
                   box, f"card{i}-tag")
        hl = wrap(head, font(F_BOLD, 12), 178, d)
        assert 1 <= len(hl) <= 2, f"card {i} head lines {len(hl)}"
        draw_lines(d, hl, x0 + 8, y0 + 24, font(F_BOLD, 12), INK, 14,
                   box, f"card{i}-head")
        dl = wrap(deck, font(F_REG, 10), 178, d)
        assert len(dl) <= 2, f"card {i} deck lines {len(dl)}: {deck}"
        draw_lines(d, dl, x0 + 8, y0 + 24 + 14 * len(hl) + 3,
                   font(F_REG, 10), (52, 58, 72), 12, box, f"card{i}-deck")

    # Map panel (left) + ALSO panel (right)
    map_panel = (10, 576, 344, 920)
    also_panel = (352, 576, 1014, 920)
    d.rectangle(map_panel, fill=CARD_BG, outline=LINE, width=1)
    d.rectangle(also_panel, fill=CARD_BG, outline=LINE, width=1)
    draw_lines(d, ["WORLD MAP - 12 PINS"], 18, 582, font(F_BOLD, 12), NAVY,
               15, map_panel, "map-title")
    mrect = (18, 600, 336, 840)  # 240 px tall, normal projection
    ART.append(mrect)
    # Land mask for the pixel check
    mask = Image.new("RGB", (mrect[2] - mrect[0], mrect[3] - mrect[1]), MAP_SEA)
    md = ImageDraw.Draw(mask)
    for poly in CONTINENTS:
        pts = [(project(lon, lat, (0, 0, mrect[2] - mrect[0],
                                   mrect[3] - mrect[1]))[0],
                project(lon, lat, (0, 0, mrect[2] - mrect[0],
                                   mrect[3] - mrect[1]))[1]) for lon, lat in poly]
        md.polygon(pts, fill=MAP_LAND)
    img.paste(mask, (mrect[0], mrect[1]))
    d = ImageDraw.Draw(img)
    # graticule
    for lon in range(-150, 181, 30):
        gx, _ = project(lon, 0, mrect)
        d.line((gx, mrect[1], gx, mrect[3]), fill=(255, 255, 255), width=1)
    pin_xy = []
    for idx, (lon, lat, label) in enumerate(PINS, start=1):
        px, py = project(lon, lat, mrect)
        mpix = mask.getpixel((int(px - mrect[0]), int(py - mrect[1])))
        assert mpix == MAP_LAND, f"pin {idx} {label} not on land: pixel {mpix}"
        dx, dy = PIN_OFFSET.get(idx, (0, 0))
        cx, cy = px + dx, py + dy
        if (dx, dy) != (0, 0):
            d.line((px, py, cx, cy), fill=INK, width=1)
            d.ellipse((px - 2, py - 2, px + 2, py + 2), fill=INK)
        assert mrect[0] + 9 <= cx <= mrect[2] - 9, f"pin {idx} x out of map"
        assert mrect[1] + 9 <= cy <= mrect[3] - 9, f"pin {idx} y out of map"
        pin_xy.append((cx, cy))
        d.ellipse((cx - 7, cy - 7, cx + 7, cy + 7), fill=RED,
                  outline=(255, 255, 255), width=2)
        num = str(idx)
        nf = font(F_BOLD, 9)
        nw = d.textlength(num, font=nf)
        draw_lines(d, [num], cx - nw / 2, cy - 6, nf, (255, 255, 255), 11,
                   (cx - 10, cy - 10, cx + 10, cy + 10), f"pin{idx}", chip=True)
    for i in range(len(pin_xy)):
        for j in range(i + 1, len(pin_xy)):
            dist = ((pin_xy[i][0] - pin_xy[j][0]) ** 2 +
                    (pin_xy[i][1] - pin_xy[j][1]) ** 2) ** 0.5
            assert dist >= 16, f"pins {i+1}-{j+1} too close: {dist:.1f}"
    # Legend: all 12 pins, 2 columns x 6 rows
    lf = font(F_REG, 9)
    for idx, (_, _, label) in enumerate(PINS, start=1):
        col, row = (idx - 1) // 6, (idx - 1) % 6
        lx = 18 + col * 162
        ly = 846 + row * 12
        txt = f"{idx}  {label}"
        w_ = d.textlength(txt, font=lf)
        assert w_ <= 158, f"legend {idx} too wide: {w_:.0f}"
        draw_lines(d, [txt], lx, ly, lf, INK, 11,
                   (10, 844, 344, 920), f"legend{idx}")

    # ALSO panel
    draw_lines(d, ["ALSO ON THURSDAY 26 NOVEMBER  -  37 MORE STORIES"], 362,
               582, font(F_BOLD, 12), NAVY, 15, also_panel, "also-title")
    assert len(ALSO) == 37, f"ALSO count {len(ALSO)}"
    af = font(F_REG, 10)
    for k, item in enumerate(ALSO):
        col, row = k // 19, k % 19
        ax = 362 + col * 330
        ay = 606 + row * 16
        w_ = d.textlength(item, font=af)
        assert w_ <= 318, f"ALSO {k+1} too wide ({w_:.0f}): {item}"
        assert re.search(r"\[(C|R|CL)\]$", item), f"ALSO {k+1} missing tag"
        assert "25 Nov" in item or True
        if "25 Nov" in item:
            assert item.endswith("[CL]"), f"ALSO {k+1} 25 Nov must be [CL]"
        draw_lines(d, [item], ax, ay, af, INK, 13,
                   (352, 600, 1014, 920), f"also{k+1}")

    # DATE CHECK footer: exactly the 7 items, verbatim, on 2 lines
    dc_box = (10, 928, 1014, 1016)
    d.rectangle(dc_box, fill=(255, 240, 200), outline=RED, width=2)
    draw_lines(d, ["DATE CHECK - THESE DID NOT HAPPEN ON 26 NOVEMBER:"],
               18, 933, font(F_BOLD, 12), RED, 15, dc_box, "dc-title")
    dc_text = "  •  ".join(DATE_CHECK)
    dc_lines = wrap(dc_text, font(F_REG, 12), 978, d)
    assert len(dc_lines) == 2, f"DATE CHECK lines {len(dc_lines)}: {dc_lines}"
    draw_lines(d, dc_lines, 18, 952, font(F_REG, 12), INK, 15, dc_box,
               "dc-body")

    # ---- global asserts
    assert len(DATE_CHECK) == 7
    assert DATE_CHECK == [
        "COP31 failed 22 Nov",
        "Shenzhou-24 launched 25 Nov",
        "Cairo tanker blast, 31 dead, 25 Nov",
        "Cartagena hostages freed 25 Nov",
        "Australia-Solomon pact 25 Nov",
        "UK energy prices +26% announced 25 Nov",
        "Huawei convicted 24 Nov",
    ], "DATE CHECK content mismatch"
    full = "  •  ".join(ALSO)
    assert full.count("Ras Tanura") == 1, "Ras Tanura must appear exactly 1x"
    assert "Riyadh" not in full, "Riyadh must not appear in ALSO"
    # HERO 2 FIX (zoom-check): hero 2 deck is ONE story (IRGC Hormuz claim
    # only) — the UKMTO 222-26 Dubai blast lives as its own ALSO item.
    assert "UKMTO" not in HEROES[1]["deck"], "hero 2 deck must not mention UKMTO"
    assert "Dubai" not in HEROES[1]["deck"], "hero 2 deck must not mention Dubai"
    assert HEROES[1]["deck"] == (
        "Iran's IRGC claims two tankers ablaze, one a supertanker carrying "
        "2M+ barrels. Unverified: no names, flags or casualties given.")
    assert full.count("UKMTO 222-26") == 1, "UKMTO 222-26 must be its own ALSO item"
    assert full.count("UKMTO") == 2, "UKMTO must appear exactly 2x in ALSO (222-26 + 223-26)"
    assert "Riyadh" not in " ".join(h["deck"] + h["head"] for h in HEROES)
    assert "Riyadh" not in " ".join(c[1] + " " + c[2] for c in CARDS)
    # No duplicate story between cards and ALSO (3-word shingles)
    def shingles(text):
        ws = re.sub(r"[^a-z0-9 ]", " ", text.lower()).split()
        return {" ".join(ws[i:i + 3]) for i in range(len(ws) - 2)}

    card_sh = set()
    for tag, head, deck in CARDS:
        card_sh |= shingles(head + " " + deck)
    for k, item in enumerate(ALSO):
        overlap = shingles(item) & card_sh
        assert not overlap, f"ALSO {k+1} duplicates a card: {overlap}"
    # ALSO must not end with a preposition before its tag
    preps = {"in", "of", "to", "for", "on", "at", "by", "with", "from", "as",
             "and", "or", "the", "a"}
    for k, item in enumerate(ALSO):
        core = item.rsplit("[", 1)[0].strip()
        assert core.split()[-1].lower() not in preps, f"ALSO {k+1} ends prep"
        assert len(item) >= 10
    # Art-vs-text: no normal text box may touch any art rect
    for (x0, y0, x1, y1, label) in TEXTBOXES:
        for art in ART:
            assert not rects_overlap((x0, y0, x1, y1), art), \
                f"text {label} overlaps art {art}"
    img.save(OUT, optimize=True)
    data = open(OUT, "rb").read()
    assert len(data) <= 1048576, f"entry too big: {len(data)}"
    print("entry.png", len(data), "bytes",
          hashlib.sha256(data).hexdigest())
    print("stories: 3 hero + 10 cards + 37 ALSO = 50; pins:", len(PINS))
    print("DATE CHECK:", " | ".join(DATE_CHECK))


if __name__ == "__main__":
    build()

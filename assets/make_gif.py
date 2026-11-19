"""Render the README demo GIF: pop-up flashcards over a desktop.

Pure-PIL frame generation, same approach as the other tools in the series.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 720, 460
DESK = (32, 35, 44)
CARD = (250, 250, 252)
CARD_EDGE = (200, 205, 215)
BLUE = (43, 108, 176)
GRAY = (113, 128, 141)
DARK = (45, 55, 72)
GREEN = (39, 103, 73)
RED = (155, 44, 44)
TERM = (16, 18, 24)
TGREEN = (80, 220, 120)
TACCENT = (90, 160, 255)
TWHITE = (220, 224, 232)

CARDS = [
    ("ambiguous", "/æmˈbɪɡjuəs/", "adj. 模棱两可的",
     "His answer was deliberately ambiguous."),
    ("deteriorate", "/dɪˈtɪəriəreɪt/", "v. 恶化，变坏",
     "His health deteriorated rapidly."),
    ("surplus", "/ˈsɜːpləs/", "n. 盈余，过剩",
     "The country has a trade surplus."),
]


FONTS = r"C:\Windows\Fonts"


def load_font(size=16, cjk=False):
    """Latin/IPA text needs segoeui; Chinese meaning needs msyh."""
    order = (("msyh.ttc", "msyh.ttf") if cjk
             else ("segoeui.ttf", "arial.ttf", "msyh.ttc"))
    for n in order:
        try:
            return ImageFont.truetype(f"{FONTS}\\{n}", size)
        except OSError:
            continue
    return ImageFont.load_default()


def load_mono(size=15):
    try:
        return ImageFont.truetype(f"{FONTS}\\consola.ttf", size)
    except OSError:
        return ImageFont.load_default()


def draw_desktop():
    img = Image.new("RGB", (W, H), DESK)
    d = ImageDraw.Draw(img)
    d.text((18, 14), "VocabPill — a word, a pill, every 30 minutes",
           fill=(150, 156, 170), font=load_font(14))
    # terminal window at the bottom
    d.rounded_rectangle((60, 320, 660, 440), 10, fill=TERM, outline=(70, 75, 90))
    d.rectangle((60, 320, 660, 344), fill=(45, 48, 58))
    d.text((74, 325), "cmd — vocabpill", fill=(130, 136, 148), font=load_mono(12))
    return img


def draw_card(img, word, phon, meaning, ex, revealed):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 210, 60, 510, 300
    d.rounded_rectangle((x0, y0, x1, y1), 14, fill=CARD, outline=CARD_EDGE, width=2)
    # title bar dot
    d.ellipse((x1 - 20, y0 + 10, x1 - 12, y0 + 18), fill=(225, 120, 120))
    cx = (x0 + x1) // 2
    d.text((cx, y0 + 28), word, fill=BLUE, font=load_font(30), anchor="ma")
    d.text((cx, y0 + 72), phon, fill=GRAY, font=load_font(16), anchor="ma")
    if revealed:
        d.text((x0 + 24, y0 + 108), meaning, fill=DARK, font=load_font(19, cjk=True),
               anchor="la")
        d.text((x0 + 24, y0 + 146), "e.g. " + ex, fill=(74, 85, 104),
               font=load_font(14), anchor="la")
        for i, (label, color) in enumerate((("认识", GREEN), ("不认识", RED))):
            bx = x0 + 40 + i * 130
            d.rounded_rectangle((bx, y0 + 195, bx + 110, y0 + 230), 8,
                                fill=color, outline=color)
            d.text((bx + 55, y0 + 205), label, fill=(255, 255, 255),
                   font=load_font(16, cjk=True), anchor="ma")
    else:
        d.rounded_rectangle((x0 + 95, y0 + 185, x0 + 205, y0 + 220), 8,
                            outline=GRAY, width=2)
        d.text((x0 + 150, y0 + 194), "显示答案", fill=GRAY, font=load_font(16, cjk=True),
               anchor="ma")
    return img


def draw_terminal(img, lines):
    d = ImageDraw.Draw(img)
    f = load_mono(14)
    y = 352
    for text, color in lines:
        d.text((80, y), text, fill=color, font=f)
        y += 24
    return img


def scene_frames(word_idx, revealed, stats=False, hold=1):
    word, phon, meaning, ex = CARDS[word_idx]
    frames = []
    n = 3 if stats else 1
    for _ in range(n if stats else hold):
        img = draw_desktop()
        if not stats:
            draw_card(img, word, phon, meaning, ex, revealed)
        lines = [("$ vocabpill --stats --level cet6", TWHITE)]
        if stats:
            lines.append(("cet6: today 12 words | seen 58/366 | mastered 9", TGREEN))
        draw_terminal(img, lines)
        frames.append(img)
    return frames


def main():
    frames = []
    # card 1: question -> answer
    frames += scene_frames(0, revealed=False, hold=4)
    frames += scene_frames(0, revealed=True, hold=6)
    # terminal only, stats visible
    frames += scene_frames(0, revealed=True, stats=True, hold=8)
    # card 2 & 3 flash by
    frames += scene_frames(1, revealed=False, hold=3)
    frames += scene_frames(1, revealed=True, hold=3)
    frames += scene_frames(2, revealed=True, hold=5)
    frames += scene_frames(2, revealed=True, stats=True, hold=6)

    out = Path(__file__).resolve().parent / "demo.gif"
    pal = [f.convert("P", palette=Image.ADAPTIVE, colors=128) for f in frames]
    pal[0].save(out, save_all=True, append_images=pal[1:], duration=550,
                loop=0, optimize=True)
    print(f"demo -> {out} ({out.stat().st_size / 1024:.0f} KiB, {len(frames)} frames)")


if __name__ == "__main__":
    main()

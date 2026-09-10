import os
from PIL import Image, ImageDraw, ImageFont
from fetch_matches import vfb_matches, latest_played, recent_form

WIDTH = HEIGHT = 1080
RED = (227, 34, 25)
WHITE = (255, 255, 255)
DARK = (20, 20, 20)

ASSET_FONT_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "fonts")
MAC_FONT_DIR = "/System/Library/Fonts/Supplemental"


def resolve_font(asset_name, mac_name):
    asset_path = os.path.join(ASSET_FONT_DIR, asset_name)
    if os.path.exists(asset_path):
        return asset_path
    return os.path.join(MAC_FONT_DIR, mac_name)


FONT_BOLD = resolve_font("Bold.ttf", "Arial Bold.ttf")
FONT_REGULAR = resolve_font("Regular.ttf", "Arial.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


def centered_text(draw, y, text, fnt, fill, width=WIDTH):
    bbox = draw.textbbox((0, 0), text, font=fnt)
    text_width = bbox[2] - bbox[0]
    x = (width - text_width) / 2
    draw.text((x, y), text, font=fnt, fill=fill)
    return bbox[3] - bbox[1]


def form_strip(draw, results, center_x, y):
    box = 56
    gap = 14
    total_width = len(results) * box + (len(results) - 1) * gap
    x = center_x - total_width / 2
    colors = {"W": (46, 160, 67), "D": (150, 150, 150), "L": (200, 40, 40)}
    fnt = font(FONT_BOLD, 30)
    for r in results:
        draw.rounded_rectangle([x, y, x + box, y + box], radius=10, fill=colors[r])
        bbox = draw.textbbox((0, 0), r, font=fnt)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text((x + box / 2 - tw / 2, y + box / 2 - th / 2 - bbox[1]), r, font=fnt, fill=WHITE)
        x += box + gap


def build_recap(match, form, out_path):
    img = Image.new("RGB", (WIDTH, HEIGHT), RED)
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, WIDTH, 140], fill=DARK)
    centered_text(draw, 45, "VFB ROSS", font(FONT_BOLD, 54), WHITE)

    y = 220
    y += centered_text(draw, y, match["round"].upper(), font(FONT_REGULAR, 32), WHITE) + 30

    home_team = "VfB Stuttgart" if match["home"] else match["opponent"]
    away_team = match["opponent"] if match["home"] else "VfB Stuttgart"
    y += 20
    y += centered_text(draw, y, home_team, font(FONT_BOLD, 44), WHITE) + 20

    score_text = f"{match['goals_for']} - {match['goals_against']}" if match["home"] \
        else f"{match['goals_against']} - {match['goals_for']}"
    y += centered_text(draw, y, score_text, font(FONT_BOLD, 100), WHITE) + 20

    y += centered_text(draw, y, away_team, font(FONT_BOLD, 44), WHITE) + 40

    result_word = {"W": "WIN", "D": "DRAW", "L": "LOSS"}[match["result"]]
    y += centered_text(draw, y, result_word, font(FONT_BOLD, 40), WHITE) + 60

    centered_text(draw, y, match["date"], font(FONT_REGULAR, 30), WHITE)

    form_strip(draw, form, WIDTH / 2, HEIGHT - 160)
    centered_text(draw, HEIGHT - 220, "RECENT FORM", font(FONT_REGULAR, 26), WHITE)

    img.save(out_path)


if __name__ == "__main__":
    matches = vfb_matches()
    match = latest_played(matches)
    form = recent_form(matches)
    os.makedirs("output", exist_ok=True)
    out_path = f"output/{match['date']}_{match['opponent'].replace(' ', '_')}.png"
    build_recap(match, form, out_path)
    print("saved:", out_path)

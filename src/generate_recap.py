import os
import random
from PIL import Image, ImageDraw, ImageFont
from fetch_matches import vfb_matches, latest_played
from match_events import load_events

WIDTH = HEIGHT = 1080
RED = (227, 34, 25)
WHITE = (255, 255, 255)
DARK = (20, 20, 20)
INSTAGRAM_HANDLE = "@vfb.ross"

ASSET_FONT_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "fonts")
MAC_FONT_DIR = "/System/Library/Fonts/Supplemental"
CREST_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "logos", "vfb-logo2.png")
PLAYERS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "players")


def resolve_font(asset_name, mac_name):
    asset_path = os.path.join(ASSET_FONT_DIR, asset_name)
    if os.path.exists(asset_path):
        return asset_path
    return os.path.join(MAC_FONT_DIR, mac_name)


FONT_BOLD = resolve_font("Bold.ttf", "Arial Bold.ttf")
FONT_REGULAR = resolve_font("Regular.ttf", "Arial.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


def load_crest(height):
    if not os.path.exists(CREST_PATH):
        return None
    crest = Image.open(CREST_PATH).convert("RGBA")
    crest = crest.crop(crest.getbbox())
    ratio = height / crest.height
    return crest.resize((int(crest.width * ratio), height))


def photos_in(category):
    folder = os.path.join(PLAYERS_DIR, category)
    if not os.path.isdir(folder):
        return []
    return [f for f in os.listdir(folder) if not f.startswith(".")]


def pick_featured_photo(events, result):
    if events is not None and events.get("featured_player_photo"):
        return events["featured_player_photo"]

    category = "loss" if result == "L" else "win"
    pool = photos_in(category)
    return f"{category}/{random.choice(pool)}" if pool else None


def scrim_gradient(width, height, top_alpha, bottom_alpha, color=DARK):
    column = Image.new("RGBA", (1, height))
    for y in range(height):
        alpha = int(top_alpha + (bottom_alpha - top_alpha) * (y / max(height - 1, 1)))
        column.putpixel((0, y), (*color, alpha))
    return column.resize((width, height))


def load_player_photo(filename, box_width, box_height):
    if not filename:
        return None
    path = os.path.join(PLAYERS_DIR, filename)
    if not os.path.exists(path):
        return None
    photo = Image.open(path).convert("RGBA")
    box_ratio = box_width / box_height
    src_ratio = photo.width / photo.height
    if src_ratio > box_ratio:
        crop_h = photo.height
        crop_w = int(crop_h * box_ratio)
    else:
        crop_w = photo.width
        crop_h = int(crop_w / box_ratio)
    left = (photo.width - crop_w) // 2
    top = (photo.height - crop_h) // 2
    photo = photo.crop((left, top, left + crop_w, top + crop_h))
    return photo.resize((box_width, box_height))


def line_height(fnt):
    ascent, descent = fnt.getmetrics()
    return ascent + descent


def centered_text(draw, y, text, fnt, fill, width=WIDTH):
    bbox = draw.textbbox((0, 0), text, font=fnt)
    text_width = bbox[2] - bbox[0]
    x = (width - text_width) / 2
    draw.text((x, y), text, font=fnt, fill=fill)
    return line_height(fnt)


def competition_tag(draw, y, label):
    fnt = font(FONT_BOLD, 22)
    bbox = draw.textbbox((0, 0), label, font=fnt)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad_x, pad_y = 22, 8
    x0, x1 = WIDTH / 2 - tw / 2 - pad_x, WIDTH / 2 + tw / 2 + pad_x
    draw.rounded_rectangle([x0, y, x1, y + th + pad_y * 2], radius=16, outline=WHITE, width=2)
    draw.text((WIDTH / 2 - tw / 2, y + pad_y - bbox[1]), label, font=fnt, fill=WHITE)


def goal_icon(draw, x, y):
    size = 14
    draw.ellipse([x, y, x + size, y + size], fill=WHITE)


def event_row(draw, event, y, side):
    fnt = font(FONT_REGULAR, 24)
    text = f"{event['minute']}'  {event['name']}"
    icon_size, gap, gutter = 14, 10, 30
    bbox = draw.textbbox((0, 0), text, font=fnt)
    tw = bbox[2] - bbox[0]
    center = WIDTH / 2
    if side == "left":
        text_x = center - gutter - tw
        icon_x = text_x - gap - icon_size
    else:
        text_x = center + gutter
        icon_x = text_x + tw + gap
    goal_icon(draw, icon_x, y + 6)
    draw.text((text_x, y), text, font=fnt, fill=WHITE)


def minute_key(minute):
    base = minute.split("+")[0]
    return int(base) + (0.5 if "+" in minute else 0)


def team_events(events, team):
    rows = [{"minute": g["minute"], "name": g["scorer"]}
            for g in events.get("goals", []) if g["team"] == team]
    return sorted(rows, key=lambda r: minute_key(r["minute"]))


def event_lists(draw, events, y):
    row_h = 34
    for i, event in enumerate(team_events(events, "vfb")):
        event_row(draw, event, y + i * row_h, "left")
    for i, event in enumerate(team_events(events, "opponent")):
        event_row(draw, event, y + i * row_h, "right")


def draw_watermark(img, handle):
    fnt = font(FONT_REGULAR, 22)
    layer = Image.new("RGBA", (WIDTH, 40), (0, 0, 0, 0))
    layer_draw = ImageDraw.Draw(layer)
    bbox = layer_draw.textbbox((0, 0), handle, font=fnt)
    tw = bbox[2] - bbox[0]
    layer_draw.text(((WIDTH - tw) / 2, 8), handle, font=fnt, fill=(*WHITE, 190))
    img.paste(layer, (0, HEIGHT - 40), layer)


def build_recap(match, out_path, events=None):
    img = Image.new("RGB", (WIDTH, HEIGHT), RED)
    draw = ImageDraw.Draw(img)

    photo_name = pick_featured_photo(events, match["result"])
    photo = load_player_photo(photo_name, WIDTH, HEIGHT)
    if photo:
        img.paste(photo, (0, 0), photo)
        header_tint = Image.new("RGBA", (WIDTH, 140), (*DARK, 170))
        img.paste(header_tint, (0, 0), header_tint)
        draw.rectangle([0, 63, WIDTH, 77], fill=RED)
        body_scrim = scrim_gradient(WIDTH, HEIGHT - 140, 90, 200)
        img.paste(body_scrim, (0, 140), body_scrim)
    else:
        draw.rectangle([0, 0, WIDTH, 140], fill=DARK)

    crest = load_crest(110)
    if crest:
        img.paste(crest, (int(WIDTH / 2 - crest.width / 2), 15), crest)
    else:
        centered_text(draw, 45, "VFB", font(FONT_BOLD, 54), WHITE)

    if events and events.get("competition"):
        competition_tag(draw, 158, events["competition"].upper())

    home_team = "VfB Stuttgart" if match["home"] else match["opponent"]
    away_team = match["opponent"] if match["home"] else "VfB Stuttgart"
    score_text = f"{match['goals_for']} - {match['goals_against']}" if match["home"] \
        else f"{match['goals_against']} - {match['goals_for']}"
    result_word = {"W": "WIN", "D": "DRAW", "L": "LOSS"}[match["result"]]

    lines = [
        (match["round"].upper(), font(FONT_REGULAR, 32), 35),
        (home_team, font(FONT_BOLD, 44), 15),
        (score_text, font(FONT_BOLD, 100), 15),
        (away_team, font(FONT_BOLD, 44), 30),
        (result_word, font(FONT_BOLD, 40), 40),
        (match["date"], font(FONT_REGULAR, 30), 35),
    ]

    goal_rows = max(len(team_events(events, "vfb")), len(team_events(events, "opponent"))) \
        if events and events.get("goals") else 0

    content_height = sum(line_height(fnt) + gap for text, fnt, gap in lines)
    content_height += goal_rows * 34

    y = max(200, HEIGHT - 60 - content_height)
    for text, fnt, gap in lines:
        y += centered_text(draw, y, text, fnt, WHITE) + gap

    if goal_rows:
        event_lists(draw, events, y)

    draw_watermark(img, INSTAGRAM_HANDLE)

    img.save(out_path)


if __name__ == "__main__":
    matches = vfb_matches()
    match = latest_played(matches)
    events = load_events(match)
    os.makedirs("output", exist_ok=True)
    out_path = f"output/{match['date']}_{match['opponent'].replace(' ', '_')}.png"
    build_recap(match, out_path, events)
    print("saved:", out_path)

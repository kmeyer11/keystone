import urllib.request
import json
from datetime import date

TEAM = "VfB Stuttgart"
SEASON_URL = "https://raw.githubusercontent.com/openfootball/football.json/master/2026-27/de.1.json"


def load_season(url=SEASON_URL):
    with urllib.request.urlopen(url) as response:
        return json.loads(response.read())


def result_letter(gf, ga):
    if gf > ga:
        return "W"
    if gf < ga:
        return "L"
    return "D"


def normalize(match):
    is_home = match["team1"] == TEAM
    opponent = match["team2"] if is_home else match["team1"]
    score = match.get("score", {}).get("ft")
    played = score is not None

    entry = {
        "date": match["date"],
        "round": match["round"],
        "opponent": opponent,
        "home": is_home,
        "played": played,
    }

    if played:
        gf, ga = (score[0], score[1]) if is_home else (score[1], score[0])
        entry["goals_for"] = gf
        entry["goals_against"] = ga
        entry["result"] = result_letter(gf, ga)

    return entry


def vfb_matches(season=None):
    season = season or load_season()
    matches = [m for m in season["matches"] if TEAM in (m["team1"], m["team2"])]
    return [normalize(m) for m in matches]


def latest_played(matches=None):
    matches = matches or vfb_matches()
    played = [m for m in matches if m["played"]]
    return played[-1] if played else None


def recent_form(matches=None, n=5):
    matches = matches or vfb_matches()
    played = [m for m in matches if m["played"]]
    return [m["result"] for m in played[-n:]]


if __name__ == "__main__":
    matches = vfb_matches()
    last = latest_played(matches)
    print("latest played match:", last)
    print("recent form:", recent_form(matches))

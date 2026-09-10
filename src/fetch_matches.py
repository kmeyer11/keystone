import urllib.request
import urllib.error
import json

TEAM = "VfB Stuttgart"
SEASON = "2026"
COMPETITIONS = [
    ("bl1", "Bundesliga"),
    ("dfb", "DFB-Pokal"),
    ("ucl2026", "Champions League"),
    ("uel2026", "Europa League"),
    ("FTS", "Friendly"),
]
MATCHES_URL = "https://api.openligadb.de/getmatchdata/{shortcut}/{season}/Stuttgart"

KNOCKOUT_ROUNDS = {
    "Achtelfinale": "Round of 16",
    "Viertelfinale": "Quarter-Final",
    "Halbfinale": "Semi-Final",
    "Finale": "Final",
}


def load_competition(shortcut, season=SEASON):
    url = MATCHES_URL.format(shortcut=shortcut, season=season)
    with urllib.request.urlopen(url) as response:
        return json.loads(response.read())


def result_letter(gf, ga):
    if gf > ga:
        return "W"
    if gf < ga:
        return "L"
    return "D"


def round_label(group):
    name = group.get("groupName", "")
    if name in KNOCKOUT_ROUNDS:
        return KNOCKOUT_ROUNDS[name]
    if name.endswith("Runde"):
        return f"Round {name.split('.')[0].strip()}"
    return f"Matchday {group.get('groupOrderID', '')}"


def final_score(match_results):
    if not match_results:
        return None
    final = max(match_results, key=lambda r: r["resultOrderID"])
    return final["pointsTeam1"], final["pointsTeam2"]


def normalize(match, competition):
    team1, team2 = match["team1"], match["team2"]
    is_home = team1["teamName"] == TEAM
    opponent = team2["teamName"] if is_home else team1["teamName"]
    score = final_score(match["matchResults"]) if match["matchIsFinished"] else None
    played = score is not None

    entry = {
        "date": match["matchDateTime"][:10],
        "round": round_label(match["group"]),
        "opponent": opponent,
        "home": is_home,
        "played": played,
        "competition": competition,
        "vfb_team_id": team1["teamId"] if is_home else team2["teamId"],
        "raw_goals": match.get("goals", []),
    }

    if played:
        gf, ga = score if is_home else (score[1], score[0])
        entry["goals_for"] = gf
        entry["goals_against"] = ga
        entry["result"] = result_letter(gf, ga)

    return entry


def vfb_matches():
    matches = []
    for shortcut, label in COMPETITIONS:
        try:
            raw = load_competition(shortcut)
        except (urllib.error.URLError, urllib.error.HTTPError):
            continue
        matches.extend(normalize(m, label) for m in raw)
    matches.sort(key=lambda m: m["date"])
    return matches


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

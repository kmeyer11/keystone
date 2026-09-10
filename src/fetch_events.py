import json
import os
import urllib.request

from fetch_matches import vfb_matches, latest_played, TEAM
from match_events import events_path

LEAGUE_SHORTCUT = "bl1"
SEASON = "2026"
COMPETITION_LABEL = "Bundesliga"
MATCHES_URL = f"https://api.openligadb.de/getmatchdata/{LEAGUE_SHORTCUT}/{SEASON}/Stuttgart"


def load_openligadb_matches(url=MATCHES_URL):
    with urllib.request.urlopen(url) as response:
        return json.loads(response.read())


def find_finished_match(oldb_matches, date):
    for m in oldb_matches:
        if m["matchIsFinished"] and m["matchDateTime"].startswith(date):
            return m
    return None


def scoring_side(goal, vfb_team_id):
    return "vfb" if goal["scoringTeamId"] == vfb_team_id else "opponent"


def minute_label(goal):
    minute = goal["matchMinute"]
    if goal["isOvertime"] and minute > 90:
        return f"90+{minute - 90}"
    if goal["isOvertime"] and minute > 45:
        return f"45+{minute - 45}"
    return str(minute)


def build_events(oldb_match):
    team1, team2 = oldb_match["team1"], oldb_match["team2"]
    vfb_team_id = team1["teamId"] if team1["teamName"] == TEAM else team2["teamId"]
    goals = [
        {
            "minute": minute_label(g),
            "scorer": g["goalGetterName"],
            "team": scoring_side(g, vfb_team_id),
        }
        for g in oldb_match["goals"]
    ]
    return {"competition": COMPETITION_LABEL, "goals": goals}


def fetch_events_for(match):
    oldb_matches = load_openligadb_matches()
    oldb_match = find_finished_match(oldb_matches, match["date"])
    if oldb_match is None:
        raise RuntimeError(f"no finished OpenLigaDB match found for {match['date']}")
    return build_events(oldb_match)


if __name__ == "__main__":
    match = latest_played(vfb_matches())
    events = fetch_events_for(match)
    path = events_path(match)

    print(json.dumps(events, indent=2, ensure_ascii=False))

    if os.path.exists(path):
        answer = input(f"{path} already exists — overwrite? [y/N] ")
        if answer.lower() != "y":
            raise SystemExit("not overwritten")

    with open(path, "w") as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print("saved:", path)

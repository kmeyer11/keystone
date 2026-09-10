import json
import os

from fetch_matches import vfb_matches, latest_played
from match_events import events_path


def scoring_side(goal, vfb_team_id):
    return "vfb" if goal["scoringTeamId"] == vfb_team_id else "opponent"


def minute_label(goal):
    minute = goal["matchMinute"]
    if goal["isOvertime"] and minute > 90:
        return f"90+{minute - 90}"
    if goal["isOvertime"] and minute > 45:
        return f"45+{minute - 45}"
    return str(minute)


def build_events(match):
    goals = [
        {
            "minute": minute_label(g),
            "scorer": g["goalGetterName"],
            "team": scoring_side(g, match["vfb_team_id"]),
        }
        for g in match["raw_goals"]
    ]
    return {"competition": match["competition"], "goals": goals}


if __name__ == "__main__":
    match = latest_played(vfb_matches())
    events = build_events(match)
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

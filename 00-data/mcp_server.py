import os

from mcp.server.mcpserver import MCPServer

from fetch_matches import vfb_matches, latest_played, recent_form
from match_events import load_events

server = MCPServer(name="keystone-data")


def public_match(match):
    keys = ["date", "round", "opponent", "home", "played", "competition"]
    if match["played"]:
        keys += ["goals_for", "goals_against", "result"]
    return {k: match[k] for k in keys}


@server.tool()
def get_latest_result() -> dict:
    """Most recently played VfB Stuttgart match, across all competitions."""
    match = latest_played(vfb_matches())
    if match is None:
        return {"error": "no played matches found"}
    return public_match(match)


@server.tool()
def get_recent_form(n: int = 5) -> list[str]:
    """Last n results as W/D/L letters, most recent last."""
    return recent_form(vfb_matches(), n)


@server.tool()
def get_upcoming_fixtures(n: int = 5) -> list[dict]:
    """Next n unplayed VfB Stuttgart fixtures, across all competitions."""
    matches = [m for m in vfb_matches() if not m["played"]]
    return [public_match(m) for m in matches[:n]]


@server.tool()
def list_matches_with_events() -> list[dict]:
    """Matches with detailed scorer data available — use the date/opponent from here with get_match_events."""
    matches_dir = os.path.join(os.path.dirname(__file__), "matches")
    entries = []
    for filename in sorted(os.listdir(matches_dir)):
        if not filename.endswith(".json"):
            continue
        date, _, opponent_slug = filename[:-5].partition("_")
        entries.append({"date": date, "opponent": opponent_slug.replace("_", " ")})
    return entries


@server.tool()
def get_match_events(date: str, opponent: str) -> dict:
    """Scorer/competition data for one match, e.g. date='2026-09-04', opponent='1. FC Köln'."""
    events = load_events({"date": date, "opponent": opponent})
    if events is None:
        return {"error": f"no events file for {date} vs {opponent}"}
    return events


if __name__ == "__main__":
    server.run()

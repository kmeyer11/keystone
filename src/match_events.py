import json
import os

EVENTS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "matches")


def events_path(match, events_dir=EVENTS_DIR):
    filename = f"{match['date']}_{match['opponent'].replace(' ', '_')}.json"
    return os.path.join(events_dir, filename)


def load_events(match, events_dir=EVENTS_DIR):
    path = events_path(match, events_dir)
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)

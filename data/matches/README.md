# Match events

Fetched automatically by `src/fetch_events.py` from OpenLigaDB (free, no key) — see
"Data source notes" in `CLAUDE.md`. Run it after a match to populate the file below,
then run `generate_recap.py`. Nothing here is ever fabricated or guessed: it's always
real data from OpenLigaDB, or a manual edit you made yourself — `fetch_events.py` asks
before overwriting a file that already exists.

One file per match, named exactly like the recap output: `<date>_<opponent>.json`
(spaces in the opponent name become underscores) — e.g. `2026-09-04_1._FC_Köln.json`.
`generate_recap.py` looks up the file by that name and silently skips the scorer/card
list and competition tag if it isn't there.

```json
{
  "competition": "BUNDESLIGA",
  "goals": [
    {"minute": "23", "scorer": "D. Undav", "team": "vfb"},
    {"minute": "90+2", "scorer": "E. Demirovic", "team": "vfb"}
  ]
}
```

- `minute` — string, quote it even for plain numbers (`"23"` not `23`) so stoppage time
  (`"90+2"`) works the same way.
- `team` — `"vfb"` or `"opponent"`, not home/away (keeps it independent of venue).
- `goals` and `competition` are optional — fill in whatever you actually know. An absent
  or empty `goals` list is a valid, deliberate "nobody scored" — not the same as the file
  not existing at all (that just skips the scorer list/photo entirely).
- `competition` comes straight from whichever OpenLigaDB competition the match was fetched
  from — `"Bundesliga"`, `"DFB-Pokal"`, `"Champions League"`, `"Europa League"`, or
  `"Friendly"` — see "Data source notes" in `CLAUDE.md`.
- Featured player photo is picked automatically from `assets/players/` based on the match
  result — see `assets/players/README.md` for exactly how. Add
  `"featured_player_photo": "win/demirovic.jpg"` here to override it manually for one
  match.

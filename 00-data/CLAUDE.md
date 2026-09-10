# 00-data

Fetches VfB Stuttgart's fixtures, results, and per-goal scorer data — the raw factual
input every later stage builds on. Nothing here ever fabricates a fact: either OpenLigaDB
has it, or a file here was hand-edited by the project owner, or it isn't shown downstream.

## Files

- `fetch_matches.py` — pulls VfB Stuttgart's fixtures/results across five competitions
  (Bundesliga, DFB-Pokal, Champions League, Europa League, friendlies) from OpenLigaDB and
  merges them into one chronological list. Returns played and upcoming matches, each
  match's opponent, venue (home/away), competition, round label, score, and a simple
  W/D/L result letter — `latest_played()` picks the most recent finished match across
  *all* competitions combined. Also carries each match's raw OpenLigaDB goal data
  (`raw_goals`) and the VfB team id, so `fetch_events.py` doesn't need a second network
  call.
- `fetch_events.py` — builds the goal-scorer JSON for the latest played match (any
  competition) from the `raw_goals`/`vfb_team_id` that `fetch_matches.py` already fetched,
  and writes it to `matches/<date>_<opponent>.json` in the schema `match_events.py`/
  `01-recap-graphics/generate_recap.py` expect. Prints the JSON before writing and asks
  for confirmation if the file already exists (so a manual edit already made isn't
  silently clobbered). Run `python fetch_events.py` before the recap-graphics stage.
- `match_events.py` — `load_events(match)` looks up `matches/<date>_<opponent>.json` for a
  played match and returns it, or `None` if it doesn't exist.
- `matches/` — scorer/competition data per match (schema in `matches/README.md`), fetched
  automatically by `fetch_events.py`; can still be hand-edited/overridden per match.
  Tracked in git (small JSON, not generated output) — also a natural seed corpus for
  `02-captions/`'s planned RAG layer.
- `mcp_server.py` — MCP server (stdio, `mcp` package, `MCPServer` — mcp 2.x renamed this
  from `FastMCP`) wrapping `fetch_matches.py`/`match_events.py` as tools for any MCP
  client: `get_latest_result`, `get_recent_form(n)`, `get_upcoming_fixtures(n)`,
  `list_matches_with_events`, `get_match_events(date, opponent)`. Each tool returns only
  the public match fields (`public_match()`) — `raw_goals`/`vfb_team_id` stay internal to
  `fetch_matches.py`/`fetch_events.py`, not part of the tool contract. Registered for
  Claude Code in the repo-root `.mcp.json` (runs via `.venv/bin/python`, so `mcp` must be
  installed in that venv per "Setup" in the root `CLAUDE.md`).

## Data source notes

Both `fetch_matches.py` and `fetch_events.py` run on OpenLigaDB (`api.openligadb.de`) —
free, no key, German-football-specific — across five competition endpoints: `bl1`
(Bundesliga), `dfb` (DFB-Pokal), `ucl2026` (Champions League), `uel2026` (Europa League),
`FTS` (friendlies). Each gives fixtures/scores *and* per-goal scorer/minute/own-goal/
penalty/overtime data in the same response, as soon as OpenLigaDB marks a match
`matchIsFinished`. The UEFA competition shortcuts embed the season year (`ucl2026`,
`uel2026`) — bump those (and `SEASON` in `fetch_matches.py`) each summer when the new
season's shortcuts are published. Friendly coverage (`FTS`) is sparse/community-
maintained — don't expect it to reliably have VfB's own friendlies.

OpenLigaDB can lag real full-time results by anywhere from minutes to (rarely) over a day
— `fetch_matches.py`'s `played` flag and `latest_played()` only ever trust
`matchIsFinished`, never a guess. If a known-finished match isn't showing up yet, that's
OpenLigaDB not having caught up — wait for it rather than fabricating a result. A manual
one-off exception (project owner supplies the real score/scorers directly) is acceptable
since it's still a real fact, just not yet in OpenLigaDB.


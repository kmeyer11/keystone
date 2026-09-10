# Keystone

Content pipeline for a VfB Stuttgart fan Instagram account. Portfolio project demonstrating context engineering, MCP, and RAG — built with genuinely useful output (real posts), not just as a tech demo.

## What this is

Automates two things:
1. Match recap graphics — generated right after a VfB Stuttgart match from real fixture/result data.
2. (Later) Phonk-style highlight edits — real match clips cut to music.

## Structure

- `src/fetch_matches.py` — pulls VfB Stuttgart's fixtures/results across five competitions (Bundesliga, DFB-Pokal, Champions League, Europa League, friendlies) from OpenLigaDB (`api.openligadb.de`, free, no API key, German-football-specific) and merges them into one chronological list. Returns played and upcoming matches, each match's opponent, venue (home/away), competition, round label, score, and a simple W/D/L result letter — `latest_played()` picks the most recent finished match across *all* competitions combined. Also carries each match's raw OpenLigaDB goal data (`raw_goals`) and the VfB team id, so `fetch_events.py` doesn't need a second network call.
- `src/generate_recap.py` — renders a 1080x1080 Instagram-ready PNG recap graphic for the most recent played match: featured player photo filling the whole canvas behind a dark gradient (top bar keeps its thin red stripe + darker tint + crest, unchanged), competition tag, scoreline, opponent (text only — no opponent crest, by choice), date/round, and scorer list. The scorer list and competition tag only render if a matching file exists in `data/matches/` — otherwise they're silently skipped. The player photo is picked by match result (`pick_featured_photo`), independent of `data/matches/`, and the graphic falls back to a plain red background if the relevant photo folder is empty — see `assets/players/README.md`. Run from the repo root (`python src/generate_recap.py`) — it writes to `output/` relative to the current working directory.
- `src/match_events.py` — `load_events(match)` looks up `data/matches/<date>_<opponent>.json` for a played match and returns it, or `None` if it doesn't exist.
- `src/fetch_events.py` — builds the goal-scorer JSON for the latest played match (any competition) from the `raw_goals`/`vfb_team_id` that `fetch_matches.py` already fetched, and writes it to `data/matches/<date>_<opponent>.json` in the schema `match_events.py`/`generate_recap.py` expect. Prints the JSON before writing and asks for confirmation if the file already exists (so a manual edit already made isn't silently clobbered). Run from the repo root (`python src/fetch_events.py`) before `generate_recap.py`.
- `src/llm_client.py` — `ask_claude(prompt)` shells out to the `claude` CLI (`claude -p`), authenticated via `CLAUDE_CODE_OAUTH_TOKEN` — runs against the Claude Pro/Max plan's included usage, not paid API credits. Nothing calls this yet; it's the connection point for future caption generation.
- `data/matches/` — scorer/competition data per match (schema in `data/matches/README.md`), fetched automatically by `src/fetch_events.py` from OpenLigaDB; can still be hand-edited/overridden per match. Tracked in git (small JSON, not generated output) — also a natural seed corpus for the "RAG layer over past matches" mentioned below.
- `output/` — generated graphics land here, one file per match (`<date>_<opponent>.png`). Gitignored — generated, not source.
- `assets/fonts/` — brand font files for the recap graphic (falls back to macOS's Arial if empty). Font files gitignored (see Conventions).
- `assets/logos/` — VfB crest/watermark for graphics and video overlays. `vfb-logo2.png` is the active one, wired into `generate_recap.py`. Gitignored (trademarked club assets).
- `assets/players/` — player photos for the recap graphic's featured-player header, in two subfolders (`win/`, `loss/`) auto-picked based on the match result (win or draw → `win/`, loss → `loss/`) — see `assets/players/README.md` for the exact selection rule. Gitignored (copyrighted photography).
- `video/clips/` — raw match footage for the future highlight-edit pipeline. Gitignored.
- `video/music/` — phonk tracks/loops to cut edits to. Gitignored.
- `video/exports/` — rendered highlight-edit output. Gitignored.
- `.env.example` — template for `CLAUDE_CODE_OAUTH_TOKEN` (free, subscription-based) and optional/paid `HF_API_KEY_ID` / `HF_API_KEY_SECRET` for Higgsfield. Copy to `.env` (gitignored) and fill in real values — never commit `.env`.
- `requirements.txt` — Pillow, python-dotenv.

## Setup

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
claude setup-token   # one-time, opens a browser — requires Claude Pro/Max/Team/Enterprise.
                      # Paste the printed token into .env as CLAUDE_CODE_OAUTH_TOKEN.
```

`claude setup-token` mints a long-lived token tied to the subscription (not an API key), so
`src/llm_client.py` runs against the plan's included usage — no per-token billing.

## Data source notes

Both `fetch_matches.py` and `fetch_events.py` run on OpenLigaDB (`api.openligadb.de`) — free, no key, German-football-specific — across five competition endpoints: `bl1` (Bundesliga), `dfb` (DFB-Pokal), `ucl2026` (Champions League), `uel2026` (Europa League), `FTS` (friendlies). Each gives fixtures/scores *and* per-goal scorer/minute/own-goal/penalty/overtime data in the same response, as soon as OpenLigaDB marks a match `matchIsFinished`. The UEFA competition shortcuts embed the season year (`ucl2026`, `uel2026`) — bump those (and `SEASON` in `fetch_matches.py`) each summer when the new season's shortcuts are published. Friendly coverage (`FTS`) is sparse/community-maintained — don't expect it to reliably have VfB's own friendlies.

Run `fetch_events.py` after a match to populate `data/matches/*.json`, then `generate_recap.py`. Never fabricate scorer/event data by hand to fill a gap — either OpenLigaDB has it, or it isn't shown. A `data/matches/*.json` file can still be hand-edited afterward (e.g. to fix a scorer-name quirk, or set `featured_player_photo`) — `fetch_events.py` asks before overwriting an existing file. Same principle applies to the future highlight-edit feature.

## Conventions

- No code comments in the source files (project owner's preference).
- Keep functions small and single-purpose so an AI coding agent can modify one piece without needing the whole file in context.
- Team colors: VfB Stuttgart red (`#E32219`) and white, used for the recap graphic background/accents.
- `assets/fonts/*`, `assets/logos/*`, and `assets/players/*` are gitignored by content-type (only their `README.md` is tracked, plus the two OFL-licensed font files which are explicitly un-ignored) — fonts are usually non-redistributable, the club crest is trademarked, and player photos are copyrighted, so none of it belongs in a public portfolio repo. Same pattern for `video/clips/*`, `video/music/*`, `video/exports/*` — large/licensed binary media, kept local only.
- Never source club crests, player photos, or music tracks yourself from arbitrary web sources — trademark/copyright risk. Point the project owner at legitimate sources (official club channels, royalty-free/CC libraries) and let them supply the actual files.

## Not yet built

- MCP server wrapper around `fetch_matches.py` (currently a plain Python function/script — MCP-server framing is a next step, not done yet).
- RAG layer over past matches/season context to ground captions.
- Anything actually calling `src/llm_client.py` — the connection works (see Setup) but no caption-generation feature consumes it yet.
- Video/highlight-edit pipeline. The "real clips cut to music" version (per `What this is`) is a free ffmpeg job — no AI video generation needed, and that's the default plan. Higgsfield (`.env.example` has placeholder keys, per Higgsfield's own auth format) is an optional later upgrade for AI-stylized effects — it costs money (paid plans from ~$19/mo, free tier is a trivial daily credit trickle) and shouldn't be treated as a dependency until explicitly decided on.
- Instagram posting (manual for now — Meta Graph API automation is a later step, requires a Business/Creator account and app review).

# Keystone

Content pipeline for a VfB Stuttgart fan Instagram account. Portfolio project demonstrating context engineering, MCP, and RAG — built with genuinely useful output (real posts), not just as a tech demo.

## What this is

Automates two things:
1. Match recap graphics — generated right after a VfB Stuttgart match from real fixture/result data.
2. (Later) Phonk-style highlight edits — real match clips cut to music.

## Structure

- `src/fetch_matches.py` — pulls VfB Stuttgart's fixtures/results for the current Bundesliga season from the openfootball/football.json public dataset (free, no API key). Returns played and upcoming matches, each match's opponent, venue (home/away), score, and a simple W/D/L result letter.
- `src/generate_recap.py` — renders a 1080x1080 Instagram-ready PNG recap graphic for the most recent played match: featured player photo filling the whole canvas behind a dark gradient (top bar keeps its thin red stripe + darker tint + crest, unchanged), competition tag, scoreline, opponent (text only — no opponent crest, by choice), date/round, and scorer list. The scorer list, competition tag, and player photo only render if a matching file exists in `data/matches/` — otherwise they're silently skipped and the graphic falls back to a plain red background. The player photo itself is auto-picked by mood (`pick_featured_photo`) — see `assets/players/README.md`. Run from the repo root (`python src/generate_recap.py`) — it writes to `output/` relative to the current working directory.
- `src/match_events.py` — `load_events(match)` looks up `data/matches/<date>_<opponent>.json` for a played match and returns it, or `None` if it doesn't exist.
- `src/llm_client.py` — `ask_claude(prompt)` shells out to the `claude` CLI (`claude -p`), authenticated via `CLAUDE_CODE_OAUTH_TOKEN` — runs against the Claude Pro/Max plan's included usage, not paid API credits. Nothing calls this yet; it's the connection point for future caption generation.
- `data/matches/` — manually authored scorer/competition data per match (schema in `data/matches/README.md`), since the free fixtures source has none of that. Tracked in git (small hand-written JSON, not generated) — also a natural seed corpus for the "RAG layer over past matches" mentioned below.
- `output/` — generated graphics land here, one file per match (`<date>_<opponent>.png`). Gitignored — generated, not source.
- `assets/fonts/` — brand font files for the recap graphic (falls back to macOS's Arial if empty). Font files gitignored (see Conventions).
- `assets/logos/` — VfB crest/watermark for graphics and video overlays. `vfb-logo2.png` is the active one, wired into `generate_recap.py`. Gitignored (trademarked club assets).
- `assets/players/` — player photos for the recap graphic's featured-player header, in three mood subfolders (`celebration/`, `disappointed/`, `devastated/`) auto-picked based on `data/matches/*.json` — see `assets/players/README.md` for the exact selection rule. Gitignored (copyrighted photography).
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

Current source (`openfootball/football.json`, raw GitHub JSON) only has fixtures and final/half-time scores — no scorers, no match events, no lineups. That's enough for the recap graphic (score + form), but NOT enough for anything claiming "who scored" or "key moments." Solved without a paid API: scorer/card data is entered by hand into `data/matches/*.json` after each match (see `data/matches/README.md`) — the graphic just skips that section if the file isn't there yet. Still applies to the future highlight-edit feature too — don't fabricate scorer/event data to fill the gap; either it's in `data/matches/`, or it isn't shown.

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

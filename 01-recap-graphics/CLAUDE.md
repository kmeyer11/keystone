# 01-recap-graphics

Renders the 1080x1080 Instagram-ready PNG recap graphic for the most recently played
match: featured player photo filling the whole canvas behind a dark gradient (top bar
keeps its thin red stripe + darker tint + crest, unchanged), competition tag, scoreline,
opponent (text only — no opponent crest, by choice), date/round, scorer list, and an
`@vfb.ross` watermark.

## Files

- `generate_recap.py` — the renderer. Depends on `00-data/` for match facts
  (`fetch_matches.py`, `match_events.py`) — imported directly via a `sys.path.insert`
  relative to `__file__` at the top of the file (see "Conventions" in the root
  `CLAUDE.md`), not duplicated here. The scorer list and competition tag only render if a
  matching file exists in `00-data/matches/` — otherwise they're silently skipped. The
  player photo is picked by match result (`pick_featured_photo`), independent of
  `00-data/matches/`, and the graphic falls back to a plain red background if the
  relevant photo folder is empty — see `players/README.md`. Run `python generate_recap.py`
  from the repo root (or from here) — it writes to `output/` next to this file regardless
  of the current working directory.
- `players/` — player photos for the recap graphic's featured-player header, in two
  subfolders (`win/`, `loss/`) auto-picked based on the match result (win or draw → win,
  loss → loss) — see `players/README.md` for the exact selection rule. Gitignored
  (copyrighted photography).
- `output/` — generated graphics land here, one file per match
  (`<date>_<opponent>.png`). Gitignored — generated, not source.

Shared brand assets (crest, brand fonts) live one level up, in the root `assets/` folder,
not here — they're reused by `03-video-highlights/` later too.

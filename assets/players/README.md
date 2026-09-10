# Players

Player photos for the recap graphic background. Any regular photo (JPEG or PNG) works —
`generate_recap.py` (`load_player_photo`) center-crops it to fill the entire 1080x1080
canvas, with a dark gradient scrim over it so the score/text stay legible (strongest at
the bottom, lightest right below the top bar). The top bar itself (thin red stripe, dark
tint, crest) is unchanged by this — the photo fills everything below/behind it.

Two subfolders, picked automatically by `pick_featured_photo` in `generate_recap.py`
based on the match result — no manual wiring needed per match:

- `win/` — used for a win or a draw.
- `loss/` — used for a loss.

A random photo is picked from the relevant folder each time — add multiple photos for
variety across posts. If the relevant folder is empty, the graphic just skips the photo
(plain red background), same graceful-skip pattern as everything else here.

You can still force a specific photo for one match by setting `featured_player_photo`
directly in that match's `data/matches/*.json` file — it takes priority over the
automatic pick. See `data/matches/README.md`.

Gitignored (see `.gitignore`): match photography is copyrighted, so source your own
(rights you hold) and keep it local rather than committing it to a public repo.

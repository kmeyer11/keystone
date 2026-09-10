# Fonts

`Bold.ttf` — [Anton](https://fonts.google.com/specimen/Anton), used for the scoreline, team
names, and result word.
`Regular.ttf` — [Barlow Condensed](https://fonts.google.com/specimen/Barlow+Condensed)
Regular, used for the round label and date.

Both SIL Open Font License (OFL) — free to use and redistribute, so unlike most fonts
these two are tracked in git (see `.gitignore`) for reproducible output.

`generate_recap.py` looks here first and falls back to macOS's built-in Arial if this
folder is empty.

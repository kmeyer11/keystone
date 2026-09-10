# Fonts

Drop brand font files here (`.ttf`), e.g. a bold display font for scorelines and a regular
weight for body text. `generate_recap.py` looks here first (`FONT_BOLD` / `FONT_REGULAR`)
and falls back to macOS's built-in Arial if this folder is empty, so the script runs
out of the box without any font files checked in.

Not gitignored by content-type but font files themselves are excluded (see `.gitignore`) —
most non-open-license fonts aren't redistributable, so keep them local rather than pushing
them to a public portfolio repo. Open-license fonts (SIL OFL, Apache, etc.) are fine to
commit if you want reproducible output — just remove the matching gitignore line.

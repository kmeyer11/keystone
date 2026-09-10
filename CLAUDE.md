# Keystone

Content pipeline for a VfB Stuttgart fan Instagram account. Portfolio project demonstrating
context engineering, MCP, and RAG — built with genuinely useful output (real posts), not
just as a tech demo.

## Pipeline

Each numbered folder is one stage of the content pipeline, self-contained with its own
code/assets/`CLAUDE.md` — an agent working inside a stage only needs that stage's
`CLAUDE.md` in context, not the whole repo. Stages run in order; each one's script(s) can
be run directly from the repo root.

- `00-data/` — fetch VfB Stuttgart's fixtures, results, and per-goal scorer data from
  OpenLigaDB, also exposed as an MCP server (`mcp_server.py`, registered in the repo-root
  `.mcp.json`) so any MCP client — Claude Code included — can query real match data as
  tools instead of importing Python directly. **Built.**
- `01-recap-graphics/` — render the Instagram recap PNG for the most recently played
  match. **Built.**
- `02-captions/` — generate the Instagram caption text via `ask_claude()`, grounded in a
  RAG layer over past matches. **Not yet built** — the Claude connection works, nothing
  calls it yet.
- `03-video-highlights/` — cut real match clips to phonk music. **Not yet built.**
- `04-publishing/` — post the finished recap (and later, highlight video) to Instagram.
  **Not yet built** — manual for now.

See each stage's own `CLAUDE.md` for its files, data formats, and design decisions.

`assets/` (this level, not inside a stage) holds brand assets shared across stages —
crest/logo and brand fonts, reused by both the recap graphics and (later) video overlays.
Stage-specific assets (like recap-graphics' player photos) live inside that stage's own
folder instead.

One shared Python environment/`requirements.txt` for the whole repo — stages are separate
folders for context/ownership clarity, not separate installs.

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
`02-captions/llm_client.py` runs against the plan's included usage — no per-token billing.

## Conventions

- No code comments in the source files (project owner's preference).
- Keep functions small and single-purpose so an AI coding agent can modify one piece without needing the whole file in context. Same reasoning at the folder level — that's why the pipeline is split into numbered stage folders, each with its own `CLAUDE.md`.
- Team colors: VfB Stuttgart red (`#E32219`) and white, used for the recap graphic background/accents.
- `assets/fonts/*` and `assets/logos/*`, and each stage's own binary-asset subfolders (`01-recap-graphics/players/*`, `03-video-highlights/{clips,music,exports}/*`), are gitignored by content-type (only their `README.md` is tracked, plus the two OFL-licensed font files which are explicitly un-ignored) — fonts are usually non-redistributable, the club crest is trademarked, player photos are copyrighted, and match/music footage is large/licensed binary media, so none of it belongs in a public portfolio repo.
- Never source club crests, player photos, or music tracks yourself from arbitrary web sources — trademark/copyright risk. Point the project owner at legitimate sources (official club channels, royalty-free/CC libraries) and let them supply the actual files.
- Cross-stage Python imports (e.g. `01-recap-graphics/generate_recap.py` importing from `00-data/`) go through an explicit `sys.path.insert` relative to `__file__` at the top of the importing file — same relative-pathing idiom already used for asset paths, just extended to imports. Don't add a shared package/`src` layout to avoid this — it's exactly the coupling the stage-folder split is meant to keep visible and minimal.
- `.mcp.json` (repo root) registers project-scoped MCP servers for Claude Code — currently just `00-data`'s. It runs via `.venv/bin/python`, so the venv (not system Python) needs `mcp` installed. Claude Code asks for approval before running a project's `.mcp.json` servers the first time; that's expected, not a misconfiguration.

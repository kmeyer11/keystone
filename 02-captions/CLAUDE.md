# 02-captions (not yet built)

Will generate the Instagram caption text to go with each recap post, grounded in a RAG
layer over past matches/season context (`00-data/matches/`) so captions can reference real
form/history instead of generic filler.

## Files

- `llm_client.py` — `ask_claude(prompt)` shells out to the `claude` CLI (`claude -p`),
  authenticated via `CLAUDE_CODE_OAUTH_TOKEN` — runs against the Claude Pro/Max plan's
  included usage, not paid API credits (see "Setup" in the root `CLAUDE.md`). The
  connection works end to end; nothing calls it yet.

## Not yet built

- The RAG layer itself over `00-data/matches/*.json`.
- The actual caption-generation call/feature that consumes `ask_claude()`.

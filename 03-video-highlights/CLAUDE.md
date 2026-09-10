# 03-video-highlights (not yet built)

Phonk-style highlight edits — real match clips cut to music.

## Files

- `clips/` — raw match footage / source clips. Gitignored — large binary source
  material, not something to check into git.
- `music/` — phonk tracks/loops to cut edits to. Gitignored — check licensing/usage
  rights per track before publishing anything cut to it.
- `exports/` — rendered highlight-edit output lands here, one file per edit. Gitignored —
  generated, not source (mirrors how `01-recap-graphics/output/` works for recap
  graphics).

Shared brand assets (crest, brand fonts) for overlays live in the root `assets/` folder,
not here.

## Plan

Default plan is a free ffmpeg job — no AI video generation needed. Higgsfield
(`.env.example` has placeholder keys, per Higgsfield's own auth format) is an optional
later upgrade for AI-stylized effects — it costs money (paid plans from ~$19/mo, free
tier is a trivial daily credit trickle) and shouldn't be treated as a dependency until
explicitly decided on.

## Not yet built

Everything — no code here yet, only the folder scaffolding.

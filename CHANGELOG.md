# Changelog

All notable changes to this project are documented here.

## [0.1.0] - 2026-08-07

Initial scaffolding.

### Added
- 45 notes: 7 Maps of Content and 38 concept notes, carrying 88 citations across
  9 Dans-Plugins repositories.
- `docs/NOTE_FORMAT.md` — the note specification: frontmatter, pinned-SHA
  citations, wikilinks, and what not to write.
- Dependency-free Python toolchain in `tools/`: `validate.py` (format, ids,
  wikilinks, citation presence), `check_sources.py` (citations resolve on
  GitHub, drift report), `sources_index.py` (regenerates `docs/SOURCES.md`),
  and `build.py` (generates the offline explorer).
- `site/index.html` — self-contained offline explorer with rendered notes,
  backlinks, citation panel, force-directed graph, search, and a light/dark
  theme.
- `/zettelkasten-expand` and `/zettelkasten-verify` skills.
- CI enforcing validation and that the committed explorer matches the notes.

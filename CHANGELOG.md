# Changelog

All notable changes to this project are documented here.

## [Unreleased]

### Fixed
- `check_sources.py` read every failed API call as proof that the cited file was
  missing, so a GitHub timeout was reported as an `INVALID` citation and failed
  the build — which is what had left `main` red. Only a definitive 404 is now an
  invalid citation; anything the API declined to answer is `unknown`, transient
  statuses are retried, and a run that could not check everything says so on
  stderr instead of passing quietly.

## [0.2.0] - 2026-08-08

### Added
- **GraphQL tab.** A query engine over the note graph — tokenizer, parser,
  schema and executor, all in the page with no server. Types: `Query`, `Note`,
  `Source`, `Tag`, `Repository`, `Stats`. Results flip between JSON and a graph
  of exactly the notes the query touched, tracked during execution so it works
  even when the query never selects an `id`. Eight worked examples and the full
  SDL are in the left pane. Press `q`.
- **Home MOCs.** Every concept note declares `moc: <id>`, and `validate.py`
  fails unless that MOC links back — a home is mutual, not self-assigned. The
  sidebar groups by it, and an unreachable MOC is now a build failure.

### Changed
- The root map is a true map of maps: it holds no claims and routes only to
  other MOCs. `moc-medieval-factions` became a mid-level hub over the domain
  model and the architecture instead of an index of 32 of the 38 concepts.
- Dark is the default theme regardless of OS preference; only the toggle
  overrides it.
- The graph is a reusable component, shared by the main view and GraphQL
  results. The right rail collapses in both full-width views.

### Fixed
- The table of contents showed raw wikilink syntax for headings containing
  links; heading text now resolves to its display form at build time.

## [0.1.0] - 2026-08-07

Initial scaffolding.

### Added
- 45 notes: 7 Maps of Content and 38 concept notes, carrying 90 citations across
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

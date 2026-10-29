# Changelog

All notable changes to this project are documented here.

## [Unreleased]

### Fixed
- `validate.py` now rejects a citation whose `lines` starts at 0 (`lines: 0`,
  `lines: 0-12`). GitHub numbers lines from 1, so the permalink anchored
  nothing, and `check_sources.py` only checks the end of the range. A malformed
  range such as `lines: a-b` is now reported as a problem instead of crashing
  the validator with a `ValueError`.
- `validate.py` now rejects a note whose `type` does not match its directory:
  a concept note must live in `notes/concepts/` and a MOC in `notes/moc/`, as
  `docs/NOTE_FORMAT.md` describes. Before, a misplaced note passed, and the
  unreachable-MOC message named a `notes/moc/` path the file was not at.
- `validate.py` now rejects a `sources` entry that is not a citation mapping,
  such as a bare `- https://github.com/...` URL, and a `sources` value that is
  not a list. Before, such an entry was dropped without a word: next to a valid
  citation it passed, branch URL and all, and on its own the note was told it
  cited nothing.
- `--help` on `validate.py`, `check_sources.py`, `sources_index.py` and
  `build.py` now prints each tool's description as written. Before, argparse
  reflowed it into one paragraph, running the one-command-per-line `Usage:`
  examples (and `check_sources.py`'s numbered list) together.
- `build.py --help` now documents every flag. `--out` had no help text, though
  it also decides where the note pages, `sitemap.xml` and `robots.txt` are
  written, and the `Usage:` block named only `--out`, leaving out `--dataset`
  and `--version-out`.
- `build.py --version-out` now creates its directory when it does not exist,
  as `--out` and `--dataset` already did. Before, the build crashed with a
  `FileNotFoundError` after writing `index.html` and `dataset.json` but before
  the note pages, `sitemap.xml` and `robots.txt`.

## [0.3.0] - 2026-10-06

### Added
- A link-preview image. `site/og.png` (1200×630: the site name, its
  description and the domain, in the explorer's colours) is served at
  `/og.png`, and the explorer and every note page now carry `og:image`
  (`https://zettel.dansplugins.com/og.png`) with its type, width, height and
  alt text, plus `twitter:image` and a `summary_large_image` Twitter card. CI
  checks the PNG's size matches the tags and that the image serves it as
  `image/png`.
- Search and sharing metadata. `build.py` now also writes a static, crawlable
  page per note at `site/notes/<id>.html` (rendered note, sources, backlinks,
  and a link back into the explorer), `site/sitemap.xml` listing `/` and every
  note page with its `updated` date as `lastmod`, and `site/robots.txt` naming
  the sitemap. The explorer and each note page carry a meta description, a
  canonical link, `og:title`/`og:description`/`og:url`/`og:type` and a
  `twitter:card`. Absolute URLs come from the `SITE_ORIGIN` constant
  (`https://zettel.dansplugins.com`), never the environment. CI checks the new files
  are current, free of localhost URLs, and served by the image.
- `version.txt` at the repository root holds the collection's version (0.2.0,
  the latest release in this file). `build.py` writes it to the
  generated-but-committed `site/version.json` as `{"version": "..."}`, and the
  container serves that at `/version.json` with `Content-Type:
  application/json` and `Cache-Control: no-store`, so a deploy can be verified
  by the version it reports. CI checks the committed file is current and that
  the image serves it with that contract.
- A small footer line at the bottom of the sidebar linking to
  [danielstephenson.dev](https://danielstephenson.dev).
- `validate.py` enforces the `YYYY-MM-DD` form `docs/NOTE_FORMAT.md` states for
  `created` and `updated`: the value must be a zero-padded, real calendar date,
  and `updated` may not precede `created`. The rule was stated but never checked,
  and it is load-bearing — `build.py` picks the collection-wide `meta.updated`
  by string comparison, which is only chronological while every value has
  exactly that shape.
- `validate.py --check-readme` asserts the size the `README.md` prose claims —
  the "What's in it" totals and the per-cluster tree — against the collection,
  and CI runs it. Those numbers had drifted repeatedly, including once more
  since the last correction, because the validator computed every one of them
  and printed them as output rather than comparing them — so adding a note left
  the README wrong with a green build.

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

# DPC Zettelkasten

A linked knowledge base for the [Dans Plugins Community](https://github.com/Dans-Plugins)
— an Obsidian-style collection of Markdown notes about how the community's
plugins actually work, where **every claim is traceable to code**.

The rule the whole repository is built around:

> Every concept note cites at least one source of truth from a Dans-Plugins
> repository, pinned at a commit SHA.

Not a branch. A SHA. A citation to `blob/main/...` is true only until someone
pushes; a citation to a commit is true forever, and tooling can then tell you,
separately, whether the code has moved on since.

## Explore it

Open [`site/index.html`](site/index.html) in a browser. No server, no build step,
no network — the whole collection is embedded in one self-contained file.

| | |
|---|---|
| **Notes** | Rendered Markdown with working `[[wikilinks]]` |
| **Backlinks** | Every note shows what links to it, not just what it links to |
| **Sources** | Each note's citations, one click from the exact lines on GitHub |
| **Graph** | Force-directed view of the whole collection — press `g` |
| **Search** | Full-text across titles, summaries, and bodies — press `/` |

The notes also open directly in [Obsidian](https://obsidian.md/): point a vault
at this repository and wikilinks, backlinks, and the graph view all work
natively. GitHub renders them as ordinary Markdown too.

## What's in it

45 notes: 7 Maps of Content and 38 concept notes, carrying 90 citations across 9
repositories.

Start at [Dan's Plugins Community](notes/moc/moc-dans-plugins-community.md), the
root map. From there:

- [Medieval Factions Map](notes/moc/moc-medieval-factions.md) — the flagship, indexed
- [Faction Domain Model](notes/moc/moc-faction-domain-model.md) — the nouns of the simulation
- [Plugin Architecture](notes/moc/moc-plugin-architecture.md) — how it is built
- [Plugin Ecosystem](notes/moc/moc-plugin-ecosystem.md) — the library, expansions, and neighbours
- [Conventions and Process](notes/moc/moc-conventions-and-process.md) — the org's standards
- [Web and Infrastructure](notes/moc/moc-web-and-infrastructure.md) — the site and the server

## Layout

```
notes/
  moc/          Maps of Content — curated entry points, no original claims
  concepts/     One idea per note, each with pinned citations
docs/
  NOTE_FORMAT.md   The rules: frontmatter, citations, wikilinks
  SOURCES.md       Generated index of every pinned commit
tools/            Dependency-free Python 3.8+ toolchain
site/index.html   The generated explorer (committed, so it works on clone)
.claude/skills/   Skills for growing and auditing the collection
```

## Working on it

Nothing to install — the toolchain is standard library only.

```bash
python3 tools/validate.py       # frontmatter, ids, wikilinks, citation presence
python3 tools/check_sources.py  # citations resolve on GitHub; report drift  (needs `gh`)
python3 tools/sources_index.py  # regenerate docs/SOURCES.md
python3 tools/build.py          # regenerate site/index.html
```

`validate.py` and `build.py` run offline and are what CI enforces.
`check_sources.py` needs an authenticated [`gh`](https://cli.github.com/).

**After changing any note, rebuild `site/index.html` and commit it.** It is a
generated file kept in the repository so the explorer works straight from a
clone.

## Skills

Two [Claude Code](https://claude.com/claude-code) skills live in `.claude/skills/`
and are the intended way to grow and maintain the collection:

- **`/zettelkasten-expand`** — finds parts of the organization the collection
  does not yet describe, and writes grounded notes for them.
- **`/zettelkasten-verify`** — audits existing notes against their cited sources,
  reports drift, and corrects what has gone stale.

Both are described in [CONTRIBUTING.md](CONTRIBUTING.md). Neither is required —
notes are plain Markdown and can be written by hand.

## Scope

This collection describes repositories in the **Dans-Plugins** organization.
Citations to anywhere else are rejected by `validate.py`. That constraint is the
point: it is what keeps the collection a description of this codebase rather
than a general wiki about Minecraft plugins.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md), and read
[docs/NOTE_FORMAT.md](docs/NOTE_FORMAT.md) before writing a note.

Found a note that is wrong? That is the most valuable kind of issue here — open
one with the note id and the source that contradicts it.

## License

[MIT](LICENSE). The notes describe code in the Dans-Plugins organization; each
cited repository keeps its own license.

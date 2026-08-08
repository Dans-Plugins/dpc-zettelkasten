# Note format

Every file under `notes/` is a Markdown document with a YAML-ish frontmatter
block. The format is deliberately small so that `tools/` can parse it with no
third-party dependencies, and so that the same files render correctly in
[Obsidian](https://obsidian.md/), on GitHub, and in the generated explorer.

## Anatomy

```markdown
---
id: faction-power
title: Faction Power
type: concept
moc: moc-faction-domain-model
tags: [medieval-factions, domain-model]
summary: The scalar a faction accumulates from its members and vassals, which caps how much land it may hold.
created: 2026-08-07
updated: 2026-08-07
sources:
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/faction/MfFaction.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 33-51
    claim: Faction power is member power plus conditional vassal power plus optional bonus power.
---

Prose. Link to other notes with [[claimed-chunk]] or [[claimed-chunk|claims]].
```

## Frontmatter keys

| Key | Required | Meaning |
|---|---|---|
| `id` | yes | Lowercase kebab-case. **Must equal the filename** without `.md`. This is the wikilink target and the URL fragment in the explorer. |
| `title` | yes | Human-readable name. Shown as the link text when a wikilink has no label. |
| `type` | yes | `concept` or `moc`. |
| `moc` | yes for `concept` | Id of the note's **home** Map of Content. See below. |
| `summary` | yes | One sentence. Appears under the title and feeds search. |
| `tags` | no | Inline list, e.g. `[medieval-factions, persistence]`. |
| `created` / `updated` | no | `YYYY-MM-DD`. |
| `sources` | yes for `concept` | List of citations — see below. |

## Home MOCs

Every concept note declares exactly one home:

```yaml
type: concept
moc: moc-faction-domain-model
```

`validate.py` enforces three things: the id resolves, it is a `type: moc` note,
and **that MOC links back to this note**. A home is a mutual relationship, not a
label a note can claim unilaterally.

The point is that the collection has a shape rather than being 38 notes in a
heap. The home MOC is what the sidebar groups by and what the root map routes
through. A note may of course be linked from several MOCs — cross-links are the
whole idea — but exactly one of them is where it *lives*.

Maps of Content do not declare a home. They are placed by being linked from
another MOC, and the root map
[`moc-dans-plugins-community`](../notes/moc/moc-dans-plugins-community.md) is
the entry point everything hangs off. A MOC that no other MOC links and that no
note calls home is unreachable, and `validate.py` fails on it.

## Citations

**Every concept note must cite at least one source of truth from a repository in
the [Dans-Plugins](https://github.com/Dans-Plugins) organization.** This is the
rule the whole repository exists to enforce: a note that cannot point at code,
configuration, or documentation in the org is a note that has drifted into
folklore.

Each citation is a mapping:

| Key | Required | Meaning |
|---|---|---|
| `repo` | yes | `Dans-Plugins/<name>`. Citations outside the org are rejected by `validate.py`. |
| `path` | yes | Repository-relative path to the file. |
| `ref` | yes | **Full 40-character commit SHA.** Never a branch name — a branch moves and silently invalidates the claim. |
| `lines` | no | `N` or `N-M`. Narrows the permalink to the exact lines that support the claim. |
| `claim` | yes | The specific statement this citation backs up, in one sentence. Not a description of the file. |

The `claim` field is what makes verification tractable: a reviewer (or the
`/zettelkasten-verify` skill) opens the permalink and asks a single yes/no
question — *does this code say that?*

### Getting a SHA

```bash
gh api repos/Dans-Plugins/Medieval-Factions/commits/main --jq .sha
```

`docs/SOURCES.md` records the pinned commit for each repository at the time of
the last sweep, so a batch of new notes can share one consistent snapshot.

### Why pin?

A link to `blob/main/...` points at a moving target. Six months later the line
numbers are wrong, the method has been renamed, and the note quietly lies. A
pinned SHA means the citation is always *true about that commit* — and
`tools/check_sources.py` can then tell you, separately, whether the code has
moved on since.

## Links between notes

Use `[[note-id]]` or `[[note-id|display text]]`. `[[note-id#Heading]]` jumps to
a heading. Link targets are validated; a wikilink that resolves to nothing is a
build failure.

Link generously. A zettelkasten's value is in its edges, not its nodes. The
working rule: if you found yourself explaining a second idea in order to explain
this one, that second idea wants to be its own note with a link to it.

## Note types

**Concept notes** (`notes/concepts/`) hold exactly one idea. If a note needs two
`##` sections that could stand alone, it is two notes. They are the only notes
that carry citations, and they must.

**Maps of Content** (`notes/moc/`) are the entry points. A MOC holds no original
claims — it is a curated, annotated index that routes a reader through a cluster
of concept notes. MOCs may cite sources but are not required to.

The root map is a **map of maps**: it links only to other MOCs and to the notes
they route through, never adding claims of its own. Below it sits one MOC per
cluster, each owning the concept notes that name it as their home.

## Structure of a good concept note

1. **Opening paragraph** — the idea in two or three sentences, no preamble.
2. **How it works** — the mechanism, grounded in the cited code.
3. **Why it is like that** — constraints, history, trade-offs. Only when known;
   never invent rationale.
4. **Related** — a short prose paragraph linking outward, not a bare list.

Keep notes under roughly 400 words. Length is a symptom that the note is holding
more than one idea.

## What not to write

- Anything that cannot be traced to a Dans-Plugins repository.
- Design rationale that is not recorded somewhere. If the code does something
  surprising and no comment, commit message, issue, or doc explains why, say
  that the reason is not recorded rather than inventing one.
- Line-by-line code narration. Notes explain ideas; the permalink shows the code.
- Duplicated content. Link to the other note instead.

## Validation

```bash
python3 tools/validate.py        # format, ids, home MOCs, wikilinks, citations
python3 tools/check_sources.py   # citations resolve on GitHub; drift report
python3 tools/sources_index.py   # regenerate docs/SOURCES.md
python3 tools/build.py           # regenerate site/index.html
```

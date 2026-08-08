# Copilot instructions

This repository follows the DPC (Dans Plugins Community) conventions defined at
https://github.com/Dans-Plugins/dpc-conventions.

## What this repository is

A zettelkasten — a linked collection of Markdown notes describing how the
Dans-Plugins plugins work. It contains no application code. The deliverables are
notes under `notes/`, a dependency-free Python toolchain under `tools/`, and a
generated offline explorer at `site/index.html`.

## The rule that matters most

**Every concept note must cite at least one source of truth from a repository in
the Dans-Plugins organization, pinned at a full 40-character commit SHA.**

- Citations to repositories outside `Dans-Plugins/` are rejected by
  `tools/validate.py`.
- Branch refs (`main`, `develop`) are rejected. Only commit SHAs.
- Each citation carries a `claim:` field stating what that source proves. It
  must be checkable by opening the link and reading the cited lines.

## Never invent rationale

If the code does something surprising and no comment, commit message, issue, or
document explains why, write that the reason is not recorded. Do not supply a
plausible motive. A fabricated rationale is indistinguishable from a real one
once it is written down, which makes it the worst possible failure mode here.

Do not write a claim you have not read the source for. Read the file at the
pinned SHA — `git show <sha>:<path>` or `gh api` — before citing it.

## Format

Read `docs/NOTE_FORMAT.md` before writing or editing a note. In short:

- `notes/concepts/<id>.md` where the filename without `.md` equals the `id`,
  lowercase kebab-case.
- Frontmatter keys: `id`, `title`, `type` (`concept` or `moc`), `summary`,
  `tags`, `created`, `updated`, `sources`.
- Link with `[[note-id]]` or `[[note-id|label]]`. Unresolvable links fail the
  build.
- One idea per note, under roughly 400 words. Two `##` sections that could stand
  alone means it should be two notes.
- MOCs live in `notes/moc/`, hold no original claims, and route the reader.

## Toolchain

Python 3.8+, standard library only. Do not add dependencies.

```bash
python3 tools/validate.py       # offline: format, ids, wikilinks, citations
python3 tools/check_sources.py  # online: citations resolve; drift report (needs gh)
python3 tools/sources_index.py  # regenerate docs/SOURCES.md
python3 tools/build.py          # regenerate site/index.html
```

`site/index.html` and `docs/SOURCES.md` are generated but committed. Any change
to a note must be accompanied by regenerating both. CI checks this.

## Branch and PR workflow

Branch from `main`. One coherent change per pull request. State in the
description which sources you read and anything you could not verify.

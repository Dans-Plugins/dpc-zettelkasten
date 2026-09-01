# Contributing

Thanks for your interest in the DPC Zettelkasten.

## Links

- [Website](https://dansplugins.com)
- [Discord](https://discord.gg/xXtuAQ2)
- [DPC Conventions](https://github.com/Dans-Plugins/dpc-conventions)

## Requirements

- A GitHub account and Git
- Python 3.8 or later (standard library only — nothing to install)
- The [GitHub CLI](https://cli.github.com/), authenticated, if you want to run
  the citation checker

## Getting started

1. Fork the repository and clone your fork.
2. Open `site/index.html` in a browser and read a few notes to get the feel of
   the format.
3. Read [docs/NOTE_FORMAT.md](docs/NOTE_FORMAT.md). It is short and it is the
   spec.

## The one hard rule

**Every concept note must cite at least one source of truth from a repository in
the [Dans-Plugins](https://github.com/Dans-Plugins) organization, pinned at a
full 40-character commit SHA.**

A note that cannot point at code, configuration, or documentation in the org
does not belong here — not because it is uninteresting, but because there is no
way for anyone to check it later.

Two things follow that are easy to get wrong:

- **Never cite a branch.** `blob/main/...` moves. Get a SHA with
  `gh api repos/Dans-Plugins/<repo>/commits/main --jq .sha` and reuse the pins
  already recorded in [docs/SOURCES.md](docs/SOURCES.md) where you can.
- **Never invent rationale.** If the code does something surprising and no
  comment, commit message, issue, or document explains why, write that the
  reason is not recorded. A plausible-sounding invented motive is the single
  most damaging thing you can add to a collection like this, because it is
  indistinguishable from a real one.

## Adding a note

1. Create `notes/concepts/<id>.md`. The filename without `.md` **is** the id,
   lowercase kebab-case.
2. Fill in the frontmatter: `id`, `title`, `type: concept`, `summary`, `tags`,
   `created`, `updated`, and `sources`.
3. Write the note. One idea. Under about 400 words. Link out generously with
   `[[other-note]]`.
4. Add it to a Map of Content in `notes/moc/` — a note nothing links to is a
   note nobody will find. `validate.py` warns about these.
5. Run the checks and commit the rebuilt site:

```bash
python3 tools/validate.py --check-readme
python3 tools/check_sources.py --note <id>
python3 tools/sources_index.py
python3 tools/build.py
```

`site/index.html`, `site/dataset.json`, and `docs/SOURCES.md` are generated files
that are kept in the repository. Commit them alongside your note.

A new note also changes the counts `README.md` states in prose — the "What's in
it" sentence and the per-cluster tree below it. `--check-readme` fails until they
are updated, and CI runs it.

## Fixing a note

Corrections are the most valuable contributions here. If a note contradicts its
own source, say so in the pull request and quote the source.

When code has changed under a note, there are two different fixes and they are
not interchangeable:

- The claim is **still true**, the code just moved → re-pin to a newer SHA,
  update the line numbers, leave the prose alone.
- The claim is **no longer true** → rewrite the prose first, then re-pin. Do not
  re-pin a stale claim to a fresh SHA; that launders a wrong statement into a
  freshly-cited-looking one.

## Using the skills

Two Claude Code skills automate the above:

- `/zettelkasten-expand` — finds gaps and writes new grounded notes.
- `/zettelkasten-verify` — audits existing notes against their sources.

They are conveniences, not gatekeepers. Their output goes through the same
review as a hand-written note, and the same rules apply — especially the one
about never inventing rationale.

## Style

- Plain, direct prose. Assume a reader who can program but has not seen this
  codebase.
- Explain the idea, not the code line by line. The permalink shows the code.
- Prefer explaining *why* something is the way it is — but only when the reason
  is recorded somewhere you can cite.
- Use tables for enumerations, prose for arguments.
- Absolutely no duplicated content between notes. Link instead.

## Pull requests

One coherent change per pull request: a cluster of related notes, a correction,
or a tooling change — not all three. Say in the description what you checked and
what you could not.

CI has three jobs:

- **`validate`** runs `validate.py --check-readme` and `sources_index.py --check`, re-runs
  `build.py` and fails if the committed `site/index.html` or `site/dataset.json`
  differs from the result, and loads `lib/zk-graphql.js` under Node to confirm
  the engine still runs headless.
- **`citations`** runs `check_sources.py` against the live GitHub API. Drift is
  reported but never fails the build; only an invalid citation — a file missing
  at the pinned commit, or a line range past the end of the file — is a failure.
  A citation the API declined to answer for (a timeout, a rate limit, no
  credentials) is reported `unknown` rather than invalid and does not fail the
  build either, but it is counted in a warning on stderr: an outage is not a
  defect in the collection, and it is not a verification of it either.
- **`image`** builds the `Dockerfile`, serves the explorer, and checks what comes
  back: `/healthz`, content types, that the served `dataset.json` and
  `lib/zk-graphql.js` are byte-identical to the committed ones (gzipped included),
  the CORS headers and preflight, and that the container runs as uid 101.

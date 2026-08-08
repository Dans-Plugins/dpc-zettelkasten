---
name: zettelkasten-expand
description: Expand the DPC Zettelkasten — find areas of the Dans-Plugins organization the collection does not yet describe, then write grounded, cited concept notes for them. Use when asked to grow, expand, or add to the zettelkasten, to cover a specific plugin or subsystem, or when invoked as /zettelkasten-expand.
---

# Expand the zettelkasten

**Repository:** `Dans-Plugins/dpc-zettelkasten`
**Scope:** the [Dans-Plugins](https://github.com/Dans-Plugins) organization, and nowhere else.

Find what the collection does not yet describe, and write notes for it. Every
note you add must be grounded in a cited source of truth from a Dans-Plugins
repository, pinned at a commit SHA.

Read `docs/NOTE_FORMAT.md` before writing anything. It is the spec; this skill
is the process.

Arguments, if given, narrow the sweep: a repository name, a subsystem, a MOC id.
With no argument, survey the whole collection and pick the highest-value gap.

---

## Phase 1 — Understand what already exists

Never start by writing. Start by reading, or you will duplicate a note or
contradict one.

1. `git checkout main && git pull`
2. `python3 tools/validate.py` — note the count, and any orphan warnings.
3. Read `docs/SOURCES.md`. This tells you which repositories are covered, at
   which commits, and how thinly.
4. List existing note ids: `ls notes/concepts/ notes/moc/`
5. Read the MOC most relevant to the area you are considering. MOCs describe the
   intended shape of their cluster; a gap is often already named there.

**Check for an open pull request from a previous run before doing anything
else.** If one exists, finish or close it. Never open a second.

---

## Phase 2 — Find the gaps

A gap is a real idea in the codebase that no note explains. Look in this order —
the list is roughly descending in value.

### Gap type 1: dangling intent

A MOC or note refers to something in prose that has no note. These are the best
gaps: someone already decided the idea was worth naming.

### Gap type 2: uncovered subsystems in a covered repository

For a repository already cited, list its source tree and compare against
`docs/SOURCES.md`:

```bash
gh api repos/Dans-Plugins/<repo>/git/trees/<sha>?recursive=1 --jq '.tree[].path'
```

A package with a service, a repository, and a data class, and no note naming it,
is a gap.

### Gap type 3: uncovered repositories

`gh repo list Dans-Plugins --limit 100 --json name,description,primaryLanguage`.
Weigh by whether the repository holds an *idea* worth a note. A small standalone
plugin that does one obvious thing may deserve one sentence in a MOC and no
concept note at all — say so rather than padding the count.

### Gap type 4: cross-cutting patterns

The most valuable and hardest to spot: something several repositories do the
same way, which no single note owns. `MfUnlockResult`, `CommandResult`, and
`ServiceFailure` being three instances of "failures are values" is that kind of
observation. These require reading widely before they become visible.

### Gap type 5: thin coverage

A note whose subject is genuinely two ideas, or a cluster where every note cites
the same one file. Splitting a note is expansion.

**Write the candidate gaps down before choosing.** For each: the idea, why it
matters, and the file you expect to cite. If you cannot name the file, you have
not found a gap — you have found a topic.

---

## Phase 3 — Choose a batch

Take **2–6 notes** that belong together. A coherent cluster beats scattered
notes: they link to each other, they share a MOC, and they can share a pinned
snapshot.

Prefer, in order:

1. Filling a dangling reference an existing note already makes.
2. Completing a cluster that is half-covered.
3. Opening a new cluster — but only with its MOC entry, never orphaned.

Write down: the ids you will create, the MOC they attach to, and the pinned SHA
you will cite.

---

## Phase 4 — Pin the snapshot

Reuse the pin already in `docs/SOURCES.md` for a repository unless you have a
reason not to. Two notes about the same code should cite the same commit.

For a repository not yet covered:

```bash
gh api repos/Dans-Plugins/<repo>/commits/$(gh repo view Dans-Plugins/<repo> \
  --json defaultBranchRef --jq .defaultBranchRef.name) --jq .sha
```

---

## Phase 5 — Read the source. Actually read it.

For every note, before writing a word of prose, read the file at the pinned SHA:

```bash
gh api repos/Dans-Plugins/<repo>/contents/<path>?ref=<sha> --jq .content | base64 -d
```

or, with the repository cloned locally, `git show <sha>:<path>`.

Then get exact line numbers for what you will cite. `lines:` is optional, but a
citation with a precise range is worth several without.

**Do not write a claim you have not read the source for.** This is the failure
mode the whole repository exists to prevent, and it is easy to fall into when a
class name makes its behaviour seem obvious.

---

## Phase 6 — Write

Follow `docs/NOTE_FORMAT.md`. Beyond the mechanics:

**One idea per note.** If you find yourself writing a second `##` section that
could stand alone, stop and split.

**Lead with the idea, not the class.** "A claim is a single Minecraft chunk
assigned to a faction" beats "MfClaimedChunk is a data class that…". The reader
wants the concept; the permalink has the code.

**Explain why, when — and only when — you can source it.** A note that explains
why a design is the way it is, backed by a comment or commit message, is worth
five that restate what the code does.

> **Never invent rationale.** If the code does something surprising and no
> comment, commit message, issue, or document explains why, write that the
> reason is not recorded. Do not supply a plausible motive. A fabricated
> rationale is indistinguishable from a real one once written down, and it will
> survive every future verification pass because there is nothing to check it
> against. This is the one unrecoverable mistake available to you here.

Distinguish clearly in your prose:
- **What the code does** — cite it.
- **Why it does that**, per a source — cite the comment, commit, or doc.
- **What follows from it** — your reasoning, phrased as reasoning.

The third is legitimate and valuable. It just must not be dressed as the second.

**Link generously.** Every note should link to at least two others and be linked
from at least one. Wikilinks to notes in the same batch are how a cluster
becomes a cluster.

**Keep the `claim:` field checkable.** `"Faction power is member power plus
conditional vassal power"` is a claim. `"This file defines the faction class"`
is a description. The first can be falsified by reading the source; the second
cannot, which makes it useless to the verify skill.

---

## Phase 7 — Attach to a MOC

Add every new note to a Map of Content, with a clause saying what it is for —
not a bare bullet. An unlinked note is invisible.

If the batch opens a genuinely new cluster, create the MOC too, and link it from
`notes/moc/moc-dans-plugins-community.md`.

---

## Phase 8 — Verify your own work

```bash
python3 tools/validate.py
python3 tools/check_sources.py --note <each new id>
python3 tools/sources_index.py
python3 tools/build.py
```

All four must be clean. Then re-read each new note against its cited source one
final time, asking only: *does the source actually say this?* You wrote the
prose after reading the code; check it in the other direction.

---

## Phase 9 — Open the pull request

Branch: `zettelkasten/<short-topic>`.

The pull request body must state:

- Which gap this fills and how you found it.
- The notes added, and the MOC they attach to.
- The repositories and pinned SHAs cited.
- **Anything you could not verify**, explicitly. A note whose rationale is
  unsourced should say so in the note and in the PR.

Commit `site/index.html` and `docs/SOURCES.md` with the notes — they are
generated but tracked, and CI fails if they are stale.

---

## Phase 10 — Record what you did not do

Close with an honest report:

- Gaps you found and deliberately skipped, with the reason.
- Areas you looked at that do not warrant notes — this is real output, and it
  saves the next run from re-deriving it.
- Anything you noticed that suggests an existing note is wrong. **Do not fix it
  here** — that is `/zettelkasten-verify`'s job, and mixing the two makes a pull
  request that is hard to review.

## What not to do

- Do not cite anything outside the Dans-Plugins organization. `validate.py`
  rejects it, and the constraint is deliberate.
- Do not cite a branch. Only full commit SHAs.
- Do not write notes to hit a count. Six good notes beat twenty thin ones, and
  thin notes are worse than no notes because they look like coverage.
- Do not restate an existing note in different words. Link to it.
- Do not edit existing notes' claims in an expansion PR beyond adding links.

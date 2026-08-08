---
name: zettelkasten-verify
description: Audit the DPC Zettelkasten for accuracy — check every concept note against its cited sources, detect drift where the code has changed, and correct or re-pin what has gone stale. Use when asked to verify, audit, fact-check, or re-validate the zettelkasten, or when invoked as /zettelkasten-verify.
---

# Verify the zettelkasten

**Repository:** `Dans-Plugins/dpc-zettelkasten`

Every concept note here claims something about code in a Dans-Plugins repository
and cites a commit to prove it. This skill checks whether those claims are still
true — and, more importantly, whether they were ever true.

Arguments narrow the audit: a note id, a repository name, a MOC id, or `--drift`
to look only at notes whose cited code has moved. With no argument, audit
everything.

---

## The two questions

Keep these separate. They have different fixes and conflating them is how a
wrong note gets laundered into a correctly-cited-looking one.

**Question 1: Is the note *accurate* at its pinned commit?**
Open the citation, read the code, ask whether the note's claim is what that code
says. A "no" here means the note was wrong when it was written. This is the
serious kind of finding.

**Question 2: Has the cited code *drifted* since?**
The file has changed at the repository's current HEAD. Drift is not an error.
It is a prompt to re-ask question 1 against the new code.

A note can be accurate and drifted (fine — re-pin), drifted and now wrong
(rewrite, then re-pin), or wrong at its own pin (rewrite; the drift is
irrelevant).

---

## Phase 1 — Mechanical pass

```bash
git checkout main && git pull
python3 tools/validate.py
python3 tools/check_sources.py            # add --note <id> / --repo <name> to narrow
```

`validate.py` catches format, id, and wikilink problems. `check_sources.py`
reports per citation:

| Status | Meaning | What to do |
|---|---|---|
| `ok` | File exists at the pin; unchanged at HEAD, or the pin *is* HEAD | Still needs a Phase 2 read — "ok" only means the link resolves |
| `DRIFTED` | File changed, moved, or was deleted since the pin | Re-ask question 1 against current code |
| `INVALID` | File missing at the pinned commit, or the line range runs past the end | Broken citation — fix immediately |
| `unknown` | Could not reach GitHub | Retry; do not report a note as verified |

**`ok` does not mean verified.** It means the URL resolves. A citation can point
at a real file at a real commit and still not support the claim written beside
it. That is exactly the failure this skill exists to catch, and only reading
finds it.

---

## Phase 2 — Read every claim against its source

This is the work. For each citation in scope:

1. Fetch the file at the pinned SHA:
   ```bash
   gh api repos/<repo>/contents/<path>?ref=<sha> --jq .content | base64 -d
   ```
   Read the cited lines, plus enough context around them to understand it.
2. Read the `claim:` field.
3. Ask one question: **does this code say that?**

Verdicts:

- **Supported** — the code says it. Move on.
- **Partly supported** — true but overstated, or true with a condition the note
  omits. Very common. Tighten the prose.
- **Unsupported** — the code does not say this. The claim may still be true and
  cited to the wrong place; find the right source or drop the claim.
- **Contradicted** — the code says the opposite. Highest priority.

Then check the note *body*, not only the `claim` fields. The claim is the part
under test, but the prose around it makes assertions too. Common failures:

- **Numbers that drifted.** Config defaults, enum member counts, "fifteen
  services", "eighteen plugins". Recount them.
- **Names that changed.** A class, method, or config key renamed upstream.
- **Enumerations gone stale.** A note listing nine flags when the code now has
  ten. Count them in the source; do not trust the note.
- **Invented rationale.** The one to hunt hardest. If a note says *why*
  something is done, find the comment, commit message, issue, or doc that says
  so. If nothing does, the note must say the reason is not recorded — or the
  sentence must go. A note's own reasoning is fine when it reads as reasoning
  ("the effect is that…", "this means…"); it is not fine dressed as recorded
  history ("this was done because…").

For a drifted citation, read the file at **both** the pinned SHA and current
HEAD, and compare:

```bash
gh api repos/<repo>/compare/<pinned-sha>...<head-sha> --jq '.files[].filename'
```

---

## Phase 3 — Classify each finding

| Severity | What it is |
|---|---|
| **Critical** | The note asserts something the source contradicts. A reader acting on it would be wrong. |
| **Major** | Unsupported claim, invented rationale, or a stale enumeration/number. |
| **Minor** | Drifted-but-still-true; imprecise line range; a renamed symbol referenced in prose. |
| **Cosmetic** | Broken wikilink, outdated `updated:` date, orphan note. |

Do not report drift alone as a finding. "This file changed and the note is still
correct" is a re-pin, not a defect.

---

## Phase 4 — Fix

The order matters:

**1. Fix the prose first.** Make the note true about the code as it is now.

**2. Then re-pin.** Update `ref:` to the current HEAD SHA and correct the
`lines:` range against the new file.

**3. Update `updated:`** to today's date.

> **Never re-pin a stale claim to a fresh SHA without rewriting it.** That
> produces a note that is wrong, freshly cited, and now looks verified — worse
> than the stale note it replaced, because the next audit will trust it.

When a claim cannot be supported and you cannot find a source that does: delete
the claim. A shorter accurate note beats a longer one with an unsourced
sentence. If deleting leaves a concept note with no citations, the note itself
should go — say so rather than inventing a citation to keep it alive.

When re-pinning one citation for a repository, consider re-pinning that
repository's whole set in the same pass, so `docs/SOURCES.md` stays a coherent
snapshot rather than a patchwork.

---

## Phase 5 — Regenerate and check

```bash
python3 tools/validate.py
python3 tools/check_sources.py
python3 tools/sources_index.py
python3 tools/build.py
```

Then re-read every note you changed, once, cold. You have just spent a long time
inside the code; check that the prose still makes sense to someone who has not.

---

## Phase 6 — Report

Report honestly, whatever the result. A clean audit is a real outcome; so is
finding that a third of the collection has drifted.

State:

- How many notes and citations were checked, and how many you **read** as
  opposed to merely resolving. If you narrowed the scope, say what you skipped.
- Findings by severity, each with: note id, what it claims, what the source
  says, and the permalink.
- What you fixed, and what you left with a reason.
- Any citation you could not check (network failure, deleted repository,
  ambiguous source). Never silently count these as passing.

---

## Phase 7 — Pull request

Branch: `zettelkasten/verify-<scope>`.

Separate the two kinds of change in the body:

- **Corrections** — claims that were wrong. List each with the evidence.
- **Re-pins** — claims still true, moved to a newer commit.

A reviewer needs to see at a glance which of your changes alter meaning. Commit
the regenerated `site/index.html` and `docs/SOURCES.md`.

If you found nothing, say so and open no pull request. Do not manufacture
changes to justify the run.

---

## Auditing your own tools

Occasionally check that the tooling still enforces what it claims. Make a
deliberately broken note in a scratch file — a citation to a non-Dans-Plugins
repository, a branch ref instead of a SHA, a wikilink to nothing — and confirm
`validate.py` rejects each. A validator that has silently stopped checking
something is worse than none, because the collection looks audited.

## What not to do

- Do not accept `check_sources.py` reporting `ok` as verification. It checks
  that links resolve, not that claims are true.
- Do not add new notes here. That is `/zettelkasten-expand`. A pull request
  mixing corrections with new material is hard to review, and the corrections
  are what need scrutiny.
- Do not fabricate a source to rescue a claim you like.
- Do not soften a finding to avoid saying a note was wrong. Being wrong in a
  citable, correctable way is the design working.

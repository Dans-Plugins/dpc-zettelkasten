---
id: two-tier-documentation
title: Two-Tier Documentation
type: concept
tags: [dpc, conventions, documentation]
summary: Reference documents live in the repository and are versioned with the code; narrative and community content lives in the GitHub wiki.
created: 2026-08-07
updated: 2026-08-07
sources:
  - repo: Dans-Plugins/dpc-conventions
    path: docs/DOCUMENTATION_PRACTICES.md
    ref: 9dc9aa37e9ed58722d86a914c563b5ceeaa07bec
    claim: DPC plugins use a two-tier model in which README, CONTRIBUTING, USER_GUIDE, COMMANDS and CONFIG are required in the repository root while Guide, FAQ, Placeholders and Developer Notes pages live in the wiki.
  - repo: Dans-Plugins/Medieval-Factions
    path: README.md
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    claim: The flagship README links to in-repo USER_GUIDE, COMMANDS, CONFIG, FACTION_FLAGS and DATABASE_QUERYING documents alongside external wiki pages.
---

DPC splits documentation by *volatility*, not by audience. Anything that must
match the code exactly lives in the repository; anything that changes on its own
schedule lives in the wiki.

## What goes where

**In the repository** (required): `README.md`, `CONTRIBUTING.md`,
`USER_GUIDE.md`, `COMMANDS.md`, `CONFIG.md`. Recommended: `CHANGELOG.md`. When
applicable: a flags reference such as `FACTION_FLAGS.md`, and
`DATABASE_QUERYING.md`.

**In the wiki**: Guide, FAQ, Placeholders, Developer Notes, External API
documentation.

## The reason for the line

`COMMANDS.md` and `CONFIG.md` are the test case. A command's syntax and a
config key's default are facts about a specific version of the code. Put them in
a wiki and they describe whatever the latest release happens to be — which is
wrong for everyone running anything else, and impossible to fix in a pull
request.

In the repository, they are versioned: they change in the same commit as the
code, review together, and a user reading the docs for the tag they installed
gets the truth.

The wiki gets what benefits from *not* being versioned — a narrative guide, an
FAQ that grows as questions arrive, community-maintained pages that would
otherwise need a maintainer's review for a typo.

## The line is not perfectly held

The convention places FAQ in the wiki, but [[medieval-factions]] now also carries
an in-repo `FAQ.md` linked from its README. Whether that is the convention
drifting or the flagship leading it is not recorded anywhere; note only that the
two currently disagree.

## Applied here

This zettelkasten sits on the same side of the line as `COMMANDS.md`: its claims
are about specific commits, so they are pinned to SHAs rather than left to track
`main`. See the [note format](../../docs/NOTE_FORMAT.md).

## Related

The rule is enforced by review rather than tooling — [[dpc-conventions]]
describes the shape, and an audit is a matter of checking which files exist.

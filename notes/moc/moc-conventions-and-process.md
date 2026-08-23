---
id: moc-conventions-and-process
title: Conventions and Process
type: moc
tags: [moc, dpc, conventions]
summary: The standards every DPC repository is held to — documentation layout, testing, CI, and release automation.
created: 2026-08-07
updated: 2026-08-07
sources:
  - repo: Dans-Plugins/dpc-conventions
    path: README.md
    ref: 9dc9aa37e9ed58722d86a914c563b5ceeaa07bec
    claim: The stated goal of dpc-conventions is to bring every plugin in the organization to the same level of completeness and quality as Medieval Factions.
---

The organization writes its standards down. [[dpc-conventions]] is the repository
that holds them, and [[medieval-factions]] is the worked example most of those
documents point back at.

## The documents

- [[two-tier-documentation]] — which docs live in the repo and which live in the
  wiki, and why the split exists.
- [[release-automation]] — a release triggers a build that attaches a JAR.
- [[release-channel]] — whether a server gets published releases or a rolling
  build of `main`, chosen per plugin.
- [[testing-and-ci]] — Gradle for unit tests, Docker Compose for a real server.

## The shape of a repository

A repository that follows the conventions has, in its root: `README.md`,
`CONTRIBUTING.md`, `USER_GUIDE.md`, `COMMANDS.md`, `CONFIG.md`, usually
`CHANGELOG.md`, and a `.github/copilot-instructions.md` giving coding agents
context about the plugin. The presence or absence of those files is the quickest
audit of whether a repository has been brought into line.

## Why it is centralised

Standards written into one repository can be cited. A note in this zettelkasten
that says "DPC plugins document their commands in `COMMANDS.md`" is a claim, and
it needs a source — [[dpc-conventions]] is that source. Standards held only in
a maintainer's head cannot be cited, verified, or handed to a new contributor.

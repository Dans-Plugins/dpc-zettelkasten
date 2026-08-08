---
id: moc-dans-plugins-community
title: Dan's Plugins Community
type: moc
tags: [moc, dpc]
summary: Root map of the zettelkasten — the community, its flagship plugin, its shared conventions, and the web and server infrastructure around them.
created: 2026-08-07
updated: 2026-08-07
sources:
  - repo: Dans-Plugins/dpc-conventions
    path: README.md
    ref: 9dc9aa37e9ed58722d86a914c563b5ceeaa07bec
    claim: DPC stands for Dans Plugins Community and treats Medieval Factions as its flagship reference implementation.
---

Dan's Plugins Community (DPC) is a collection of open-source Minecraft plugins
built around a single ambition: let players simulate societies. [[medieval-factions]]
is the flagship — sovereign nations, claimed land, diplomacy, war — and most
other repositories in the organization either extend it, support it, or share
its conventions.

This is the root of the zettelkasten. Each note below is a doorway into a
cluster; every concept note in the collection is grounded in a citation to a
file in a [Dans-Plugins](https://github.com/Dans-Plugins) repository, pinned at
a commit SHA.

## The four clusters

- **[[moc-faction-domain-model]]** — the nouns of the simulation. What a faction
  *is*, what power measures, how land is claimed, how factions relate to one
  another.
- **[[moc-plugin-architecture]]** — how the flagship is built. The service and
  repository layering, persistence, concurrency, and the seams that expansions
  and integrations plug into.
- **[[moc-plugin-ecosystem]]** — the other plugins. Shared libraries, official
  expansions, and the plugins the flagship talks to at runtime.
- **[[moc-conventions-and-process]]** — the rules the organization holds itself
  to: documentation, testing, releases.
- **[[moc-web-and-infrastructure]]** — [[dansplugins-dot-com]], the community
  server, and the pipe that carries live faction data from a Minecraft server
  to the website.

## Where to start

If you have never touched the codebase, read [[medieval-factions]], then
[[faction]], then [[faction-power]]. Those three carry most of the vocabulary
the rest of the collection assumes.

If you are here to change code, start at [[service-layer]] and
[[repository-pattern]] — nearly every feature in the flagship is a new service,
a new repository, and a command that wires them together.

## How this collection works

Notes are single ideas. Maps of Content like this one hold no original claims;
they route. Concept notes carry the claims, and each claim points at a specific
file at a specific commit. See [the note format](../../docs/NOTE_FORMAT.md) for
the rules, and [[moc-medieval-factions]] for a full index of the flagship's
concepts.

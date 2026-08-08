---
id: moc-medieval-factions
title: Medieval Factions
type: moc
tags: [moc, medieval-factions]
summary: Index of every concept note about the flagship plugin, grouped by the layer of the system it belongs to.
created: 2026-08-07
updated: 2026-08-07
sources:
  - repo: Dans-Plugins/Medieval-Factions
    path: README.md
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    claim: Medieval Factions is described as a system of mechanics for simulating sovereign nations in Minecraft.
---

[[medieval-factions]] is the largest codebase in the organization and the
reference implementation for everything else. This map indexes the concepts
that make it up.

## The simulation

The domain model — see [[moc-faction-domain-model]] for the annotated version.

- [[faction]] · [[faction-power]] · [[player-power]] · [[demesne-limit]]
- [[claimed-chunk]] · [[faction-relationship]] · [[vassalage]]
- [[faction-role]] · [[faction-permission]] · [[faction-flag]]
- [[law]] · [[gate]] · [[locked-block]] · [[approval-request]]

## The machinery

How the plugin is put together — see [[moc-plugin-architecture]].

- [[service-layer]] · [[repository-pattern]] · [[jooq-persistence]]
- [[optimistic-locking]] · [[value-class-identifier]] · [[main-thread-safety]]
- [[faction-events]] · [[legacy-data-migration]]

## The seams

Points where other software attaches:

- [[notification]] — pluggable delivery, backed by [[mailboxes]] when present.
- [[map-integration]] — claimed land drawn on a web map.
- [[dpc-api-faction-sync]] — the roster pushed to [[dansplugins-dot-com]].
- [[expansion-plugin]] — how [[fiefs]] and [[currencies]] build on top.

## Reading the source

Documentation lives beside the code by convention (see
[[two-tier-documentation]]): `USER_GUIDE.md`, `COMMANDS.md`, `CONFIG.md`,
`FACTION_FLAGS.md`, and `DATABASE_QUERYING.md` are all in the repository root.
Start there before reading Kotlin.

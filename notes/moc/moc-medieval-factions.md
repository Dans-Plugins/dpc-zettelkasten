---
id: moc-medieval-factions
title: Medieval Factions Map
type: moc
tags: [moc, medieval-factions]
summary: Mid-level map of the flagship — routes to the domain model and the architecture, and names the seams other software attaches to.
created: 2026-08-07
updated: 2026-08-08
sources:
  - repo: Dans-Plugins/Medieval-Factions
    path: README.md
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    claim: Medieval Factions is described as a system of mechanics for simulating sovereign nations in Minecraft.
---

[[medieval-factions]] is the largest codebase in the organization and the
reference implementation for everything else. It carries enough distinct
material to need two maps rather than one, and this note is the fork between
them.

## The two halves

**[[moc-faction-domain-model]] — what the simulation *is*.** Factions, power,
land, diplomacy, governance. Read this if you want to understand the game, or if
you are deciding what a feature should *do*.

**[[moc-plugin-architecture]] — how the code is *arranged*.** Services,
repositories, persistence, concurrency. Read this if you are deciding where a
feature should *live*.

The split is clean in practice: a change almost always starts in one and lands
in the other.

## The seams

Four places other software attaches, each covered by its own note under
[[moc-plugin-architecture]] or [[moc-plugin-ecosystem]]:

| Seam | What attaches | Note |
|---|---|---|
| Bukkit events | Anything reacting to a faction change | [[faction-events]] |
| Service registry | Anything reading or writing faction state | [[service-layer]] |
| Pluggable interfaces | Optional plugins supplying an implementation | [[notification]] · [[map-integration]] |
| Outbound HTTP | The community website | [[dpc-api-faction-sync]] |

If you are writing an [[expansion-plugin]], the first two are the ones you want.

## Reading the source

Documentation lives beside the code by convention — see
[[two-tier-documentation]]. `USER_GUIDE.md`, `COMMANDS.md`, `CONFIG.md`,
`FACTION_FLAGS.md`, `DATABASE_QUERYING.md`, and `FAQ.md` are all in the
repository root. Start there before reading Kotlin.

## Where it sits

Up: [[moc-dans-plugins-community]]. Sideways: [[moc-plugin-ecosystem]] for the
plugins around it, [[moc-web-and-infrastructure]] for where its data goes.

---
id: fiefs
title: Fiefs
type: concept
tags: [fiefs, expansion, ecosystem]
summary: An expansion adding sub-factions inside a faction — and the clearest surviving example of the pre-version-5 integration style.
created: 2026-08-07
updated: 2026-08-07
sources:
  - repo: Dans-Plugins/Fiefs
    path: README.md
    ref: 4c66e09aa50f467921ce1519f0b7236a5f23f7a2
    claim: Fiefs allows faction members to create fiefs, which function as sub-factions, and depends on Medieval Factions in order to work.
  - repo: Dans-Plugins/Fiefs
    path: src/main/java/dansplugins/fiefs/Fiefs.java
    ref: 4c66e09aa50f467921ce1519f0b7236a5f23f7a2
    claim: Fiefs extends PonderBukkitPlugin and reaches Medieval Factions through its own MedievalFactionsIntegrator class rather than by importing flagship domain types.
---

Fiefs lets members of a [[faction]] carve out sub-factions — a fief has its own
members, its own claimed chunks within the parent's territory, and its own
flags. It is the feudal layer below the faction.

## An older generation

Fiefs is Java, not Kotlin, and it is built on an earlier stack: it extends
`PonderBukkitPlugin` from an older [[ponder]] API, keeps state in a
`PersistentData` object with a `StorageService` writing files, and talks to the
flagship through a hand-written `MedievalFactionsIntegrator`.

Its `dependencies/` directory holds the jars it compiles against —
`Medieval-Factions-4.6.2.jar` and `Ponder-v0.15-alpha-2.jar`. It therefore
targets **Medieval Factions 4**, not the version 5 described everywhere else in
this collection.

## Why that matters

The integrator pattern is what a plugin does when the plugin it extends offers
no typed API: reflectively or defensively fetch the other plugin, wrap it, and
degrade if it is missing. Compare [[currencies]], which simply imports
`MfFactionId` and `MedievalFactions` because version 5 exposes them.

Reading the two together is the best available illustration of what the version
5 rewrite bought — see [[expansion-plugin]].

## Its own claim model

Fiefs has its own `ClaimedChunk` class, separate from the flagship's
[[claimed-chunk]]. Two independent claim registries over the same ground is
inherent to the sub-faction idea, but it does mean a chunk's ownership is a
question with two answers depending on which plugin you ask.

## Related

Fiefs is one of the two official expansions listed in the flagship's README, and
ships in the curated set on [[dpc-mc-server]].

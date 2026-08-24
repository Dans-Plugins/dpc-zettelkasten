---
id: moc-plugin-ecosystem
title: Plugin Ecosystem
type: moc
tags: [moc, dpc, ecosystem]
summary: The plugins around the flagship — the shared library, the official expansions, the plugins Medieval Factions talks to at runtime, and the standalone plugins that stand apart from it entirely.
created: 2026-08-07
updated: 2026-08-24
sources:
  - repo: Dans-Plugins/dpc-mc-server
    path: README.md
    ref: d42e0ec06f9b29baaa043442d24ef2dd81edfa49
    claim: The community server ships a curated set of DPC plugins that can each be toggled via environment variables.
---

The organization holds roughly forty repositories. They are not forty unrelated
plugins — they cluster.

## The library

[[ponder]] is the shared Kotlin/Java library: a multi-module Gradle project
providing command dispatch, caching, and Bukkit helpers used across plugins.

## The expansions

[[expansion-plugin]] describes the pattern: a plugin that hard-depends on
[[medieval-factions]] and extends the simulation rather than standing alone.

- [[fiefs]] — sub-factions inside a faction.
- [[currencies]] — faction-minted local money.

## The runtime neighbours

Plugins the flagship detects and uses if they happen to be installed:

- [[mailboxes]] — persistent player mail, used as a [[notification]] backend.
- [[map-integration]] — Dynmap and BlueMap surfaces for [[claimed-chunk]] data.

## Distribution and hosting

- [[dans-plugin-manager]] — installs DPC plugins from in-game or the console.
- [[dpc-mc-server]] — infrastructure-as-code server that runs a curated set of
  the plugins together, and therefore doubles as the integration test bed.

## The standalone plugins

Not everything here orbits the flagship. These are the most-downloaded plugins
that depend on nothing in the organization but [[ponder]], and each earns a note
by holding an idea the collection did not otherwise have:

- [[medieval-roleplay-engine]] — chat whose audience is a radius measured in
  blocks rather than a membership list, which is the exact counterpoint to
  [[faction-chat-channel]] resolving one from the diplomacy graph.
- [[wild-pets]] — taming generalised into a per-entity-type table of required
  item, quantity and success chance, so any mob becomes a pet.
- [[simple-skills]] — progression in which a level buys a rising *probability*
  of a perk rather than unlocking one.
- [[food-spoilage]] — the clearest case in the organization of a plugin with no
  persistence layer at all, because the item stack itself is the database. Worth
  reading directly against [[repository-pattern]] and [[jooq-persistence]].
- [[alternate-account-finder]] — deterministic encryption chosen so that an
  equality join still works over ciphertext, and the privacy cost that buys.

## The rest

The remaining repositories are small standalone plugins that do one obvious
thing each. They matter to this collection mainly as subjects of
[[dpc-conventions]] — the standards effort exists precisely to bring them up to
the flagship's level.

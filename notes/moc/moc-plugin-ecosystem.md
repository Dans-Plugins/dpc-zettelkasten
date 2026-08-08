---
id: moc-plugin-ecosystem
title: Plugin Ecosystem
type: moc
tags: [moc, dpc, ecosystem]
summary: The plugins around the flagship — the shared library, the official expansions, and the plugins Medieval Factions talks to at runtime.
created: 2026-08-07
updated: 2026-08-07
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

## The rest

Many repositories in the organization are small standalone plugins with no
dependency on the flagship. They matter to this collection mainly as subjects of
[[dpc-conventions]] — the standards effort exists precisely to bring them up to
the flagship's level.

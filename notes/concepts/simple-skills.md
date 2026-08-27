---
id: simple-skills
title: SimpleSkills
type: concept
moc: moc-plugin-ecosystem
tags: [simpleskills, ecosystem, progression]
summary: A progression layer where ordinary activities each tick a per-player counter, and the resulting level buys a linearly rising chance of a perk.
created: 2026-08-24
updated: 2026-08-24
sources:
  - repo: Dans-Plugins/SimpleSkills
    path: src/main/java/dansplugins/simpleskills/SimpleSkills.java
    ref: 3350aa18ae484114fb6c21d130d32174050ee1dd
    lines: 166-215
    claim: Twenty named skills are instantiated at plugin enable, and only those the config marks active register Bukkit listeners.
  - repo: Dans-Plugins/SimpleSkills
    path: src/main/java/dansplugins/simpleskills/playerrecord/PlayerRecord.java
    ref: 3350aa18ae484114fb6c21d130d32174050ee1dd
    lines: 131-139
    claim: A qualifying action adds exactly one experience point to the skill, with no weighting for what was done.
  - repo: Dans-Plugins/SimpleSkills
    path: src/main/java/dansplugins/simpleskills/experience/ExperienceCalculator.java
    ref: 3350aa18ae484114fb6c21d130d32174050ee1dd
    lines: 8-10
    claim: Experience required for the next level is the base requirement multiplied by the current level raised to the power of the increase factor.
  - repo: Dans-Plugins/SimpleSkills
    path: src/main/java/dansplugins/simpleskills/chance/ChanceCalculator.java
    ref: 3350aa18ae484114fb6c21d130d32174050ee1dd
    lines: 52-63
    claim: A perk roll draws uniformly over the configured maximum level and succeeds below a threshold of maxLevel times (level / maxLevel) times a caller-supplied nerf factor.
  - repo: Dans-Plugins/SimpleSkills
    path: src/main/java/dansplugins/simpleskills/listeners/PlacedBlockListener.java
    ref: 3350aa18ae484114fb6c21d130d32174050ee1dd
    lines: 13-43
    claim: Player-placed blocks are tagged with plugin metadata so block-break skills refuse to grant experience for them, which the class javadoc states closes a silk-touch replace-and-remine exploit.
---

SimpleSkills adds twenty skills — Mining, Farming, Cardio, Dueling and the rest —
that level up simply by doing the corresponding thing, and pay out an occasional
perk once they do. Each is a separate `active` toggle in the config, and an
inactive skill never registers its listeners at all.

## Counting, not measuring

The economy is deliberately flat: every qualifying action is worth exactly one
experience point. Mining an ore, sprinting a tick, breeding an animal — all one.
What varies is not the reward but the filter, and each skill decides for itself
which events qualify (Mining wants an ore block, broken in survival mode, with a
pickaxe in hand).

Levelling is where the curve lives. The next level costs
`base × level^factor`, so with the shipped defaults of 10 and 1.2 the first level
is cheap and the hundredth is not.

## Level as a probability

Perks are not unlocked, they are rolled for. `ChanceCalculator` draws uniformly
over the configured maximum level and compares against a threshold proportional
to the player's level in that skill, scaled down by a per-skill nerf factor. The
arithmetic reduces — this is my reading of the formula, not a comment in the
source — to a success chance that climbs linearly from nothing at level 0 to
exactly the nerf factor at the level cap. Progression therefore feels like a
dial rather than a staircase.

## The one exploit that is guarded

Block skills refuse experience for a block a player placed, tracked by metadata
on the block itself. The javadoc says why in as many words: silk-touching an ore,
setting it back down, and re-mining it would otherwise be infinite experience.
It is the only anti-farming guard in the plugin, and its correctness depends on
listener registration order, which the code comments call out.

## Related

The plugin sits on [[ponder]] for its command service and its savable-record
interfaces, and ships in the curated jar set on [[dpc-mc-server]] alongside
[[wild-pets]] and [[food-spoilage]] — standalone plugins that, unlike
[[fiefs]], extend vanilla rather than [[medieval-factions]].

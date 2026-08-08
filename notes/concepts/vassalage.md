---
id: vassalage
title: Vassalage
type: concept
moc: moc-faction-domain-model
tags: [medieval-factions, domain-model, diplomacy]
summary: The feudal hierarchy — a liege draws power from its vassals, but only while its own members remain strong.
created: 2026-08-07
updated: 2026-08-07
sources:
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/faction/MfFaction.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 37-47
    claim: A faction's vassal power sums each vassal's power scaled by a configured multiplier, and is only added to the faction's power when member power is at least half of max member power.
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/relationship/MfVassalNode.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    claim: Vassal relationships are modelled as a recursive tree node holding a faction id and a list of child nodes, with recursive contains, map and flatMap helpers.
---

Vassalage is the liege/vassal half of [[faction-relationship]], and the only
diplomatic state that changes a faction's numbers. It is what makes the game
medieval rather than merely territorial.

## The bargain

A liege adds a share of each vassal's [[faction-power]] to its own, scaled by
`factions.vassalPowerContributionMultiplier`. That contribution lifts the
liege's [[demesne-limit]], letting it hold land its own membership could not
support.

The vassal, in exchange, keeps its own identity, its own land, and its own
roster — and typically gains the protection of the
`vassalageTreeCanInteractWithLand` and `liegeChainCanInteractWithLand`
[[faction-flag]] settings, which let the hierarchy build inside each other's
claims.

## The condition that keeps it honest

Vassal power is added *only* when the liege's own member power is at least half
of its maximum. Below that threshold the contribution is not reduced — it is
removed entirely.

This single clause is what prevents the obvious exploit. Without it, a
one-player faction could accumulate vassals and hold an enormous demesne on
borrowed strength. With it, an empire is capped by the activity of its own core:
let the capital go quiet and the whole structure snaps back to what its own
members can carry.

## A tree, not a list

`MfVassalNode` is recursive — a faction id plus a list of child nodes — so a
faction can have vassals which themselves have vassals, and the whole subtree can
be searched or flattened with `contains`, `map` and `flatMap`. Its counterpart
`MfLiegeNode` points the other way, holding a single optional liege, because
looking *up* the hierarchy is a chain rather than a tree.

Power contribution is computed from the direct vassals of a faction, and each of
those factions has already folded in its own vassals' contribution — subject, at
each level, to that level's own half-strength test.

## Related

Becoming someone's vassal is a consequential, mutual act, which is why it is one
of the three [[approval-request]] types.

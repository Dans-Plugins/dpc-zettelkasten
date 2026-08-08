---
id: faction-power
title: Faction Power
type: concept
moc: moc-faction-domain-model
tags: [medieval-factions, domain-model, power]
summary: A faction's live strength — the sum of its members' power plus a conditional vassal contribution — and the cap on how much land it may hold.
created: 2026-08-07
updated: 2026-08-07
sources:
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/faction/MfFaction.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 33-51
    claim: Faction power is member power, plus vassal power only when member power is at least half of max member power, plus bonus power when the acceptBonusPower flag is set.
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/resources/config.yml
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 72
    claim: The vassal power contribution multiplier defaults to 0.75.
---

Faction power is the single number the simulation runs on. It is computed, never
stored, and it decides how much territory a faction can defend — see
[[demesne-limit]].

## The formula

```
memberPower    = Σ power of each member
maxMemberPower = memberCount × players.maxPower
vassalPower    = Σ (vassal.power × vassalPowerContributionMultiplier)

power = memberPower
      + vassalPower   if memberPower ≥ maxMemberPower / 2
      + bonusPower    if the acceptBonusPower flag is set
```

`memberPower` sums each member's [[player-power]]; `vassalPower` walks the
factions related to this one as vassals — see [[faction-relationship]].

## The half-strength gate

The interesting clause is the condition on vassal power: a liege only receives
its vassals' contribution while its *own* members are at or above half their
collective maximum. A faction cannot subsist on tribute alone. If its own
members stop logging in, the vassal contribution switches off entirely — not
proportionally, but as a cliff.

The effect is that [[vassalage]] amplifies a healthy faction rather than
propping up a hollow one, and a large empire whose core has gone quiet collapses
to the size its own members can hold.

## Bonus power is opt-in

`bonusPower` is a stored constant an operator can grant. A faction can refuse it
by clearing the `acceptBonusPower` [[faction-flag]] — the flag gates both the
`power` and `maxPower` computations, so declining it costs the faction its
ceiling as well as its floor. Servers that want a pure simulation can leave the
mechanism unused.

## Related

Because power is a computed property on the [[faction]] data class, it is
recalculated on every access rather than cached. Anything that walks all
factions and reads `power` therefore also walks every member's player record —
worth knowing before adding such a loop to a hot path.

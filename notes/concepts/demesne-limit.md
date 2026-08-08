---
id: demesne-limit
title: Demesne Limit
type: concept
tags: [medieval-factions, domain-model, territory, power]
summary: The rule binding land to power — a faction may hold at most one chunk per point of faction power.
created: 2026-08-07
updated: 2026-08-07
sources:
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/command/faction/claim/MfFactionClaimFillCommand.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 109-110
    claim: When factions.limitLand is enabled, a claim is refused if the new chunks plus existing claims would exceed the faction's power, and the player is told they reached the demesne limit.
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/command/faction/claim/MfFactionClaimCircleCommand.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 109-110
    claim: The same limitLand check and demesne-limit message are applied by the circle-claim command.
---

A faction may hold one [[claimed-chunk]] per point of [[faction-power]]. The
check is literally `claims + newChunks > faction.power` — power and land are
measured in the same unit.

## The rule in practice

The comparison is gated on the `factions.limitLand` configuration flag, so a
server can turn it off entirely. When it is on, a faction that tries to claim
past its allowance is refused with the *demesne limit* message and the count it
is allowed, floored to a whole number.

The plugin's own language key calls this the demesne limit. A demesne is the
land a medieval lord held directly, as distinct from land held by vassals —
which is the same distinction [[vassalage]] draws mechanically.

## Why it is the keystone

This one inequality is what makes the rest of the simulation cohere. Because
[[player-power]] rises with time online and falls on death, and because
[[faction-power]] sums it, territory becomes a function of an organisation's
living activity. Three consequences follow:

- **Land must be staffed.** A faction cannot claim an empire and walk away.
- **War has a territorial outcome even without sieges.** Killing defenders
  lowers their power, which lowers the limit, which puts existing claims over
  the line.
- **Growth requires recruitment.** The only sustainable way to expand the map is
  to expand the roster — or to acquire vassals, which is what [[vassalage]] pays
  for.

## Over-claiming

Because power is computed live and claims are stored, a faction can end up
holding *more* land than its current power allows — the limit is enforced when
claiming, not continuously. Related checks in the claim commands compare a
faction's power against its existing claim count when land changes hands, which
is how over-extended factions become vulnerable rather than merely capped.

## Related

[[claimed-chunk]] describes what is being counted; [[faction-power]] describes
what is doing the counting.

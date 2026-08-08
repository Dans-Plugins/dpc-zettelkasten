---
id: locked-block
title: Locked Block
type: concept
tags: [medieval-factions, domain-model, protection]
summary: Per-player protection on a single block, with an explicit accessor list — independent of faction land ownership.
created: 2026-08-07
updated: 2026-08-07
sources:
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/locks/MfLockedBlock.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 6-17
    claim: A locked block records an id, version, block position, chunk x and z, the owning player id, and a list of accessor player ids.
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/locks/MfUnlockResult.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    claim: The unlock result is an enum of SUCCESS, NOT_LOCKED and FAILURE rather than a boolean.
---

A lock protects one block — typically a chest or door — for one player, with an
explicit list of other players allowed to use it.

## Owned by a player, not a faction

This is the notable thing about the design: a locked block belongs to an
`MfPlayerId`, not an `MfFactionId`. Protection is personal and survives changes
of faction. A member can secure their own chest inside their faction's
[[claimed-chunk|claim]] against their own faction-mates, and keep it when they
leave.

Land ownership and container ownership are therefore two independent protection
systems that both run on every block interaction. [[faction-permission]] governs
the first; the accessor list governs the second.

## Chunk coordinates are denormalised

The record stores `chunkX` and `chunkZ` alongside the full block position, even
though both are derivable from it by integer division. This is an index: the
common query is "which locks exist in this chunk?", asked whenever a chunk's
ownership changes or a player interacts within it. Storing the chunk lets that
be a lookup rather than a scan over every lock in the world.

## Typed unlock result

`MfUnlockResult` gives unlocking a typed outcome — `SUCCESS`, `NOT_LOCKED`, or
`FAILURE` — so a caller can tell "there was nothing to unlock" apart from "the
unlock was refused" and produce the right message for each. Compare the broader
[[service-layer]] failure model, which reaches for `Result4k` to make the same
distinction.

## Related

Locks are among the records carried over by [[legacy-data-migration]].

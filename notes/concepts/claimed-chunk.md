---
id: claimed-chunk
title: Claimed Chunk
type: concept
tags: [medieval-factions, domain-model, territory]
summary: Territory is recorded one 16×16 Minecraft chunk at a time, as a row pointing from world coordinates to a faction.
created: 2026-08-07
updated: 2026-08-07
sources:
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/claim/MfClaimedChunk.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 8-17
    claim: A claimed chunk is a data class of worldId, x, z, and factionId, with convenience constructors from a Bukkit Chunk and from an MfChunkPosition.
---

A claim is a single Minecraft chunk — a 16×16 column — assigned to a [[faction]].
There is no polygon, no region, and no bounding box: territory is a set of chunk
coordinates, and every question about land reduces to a lookup on
`(worldId, x, z)`.

## The shape of the record

`MfClaimedChunk` holds four fields and no behaviour: the world UUID, the chunk's
`x` and `z`, and the owning `factionId`. It is deliberately the smallest thing
that can answer "who owns this ground?".

Note the direction of the reference. The chunk points at the faction; the
[[faction]] record does not hold a list of its claims. Territory is therefore
queried, not traversed — which is why `MfClaimService` exists and why counting a
faction's claims is a repository call rather than a property read.

## Why chunks

Chunk granularity is inherited from Minecraft itself. The server already loads,
unloads, and indexes the world by chunk, so a claim boundary that coincides with
a chunk boundary is free to check: given a block, the containing chunk is
arithmetic, and the ownership lookup is a single map hit. A finer boundary would
have cost a spatial index on the hot path of every block placement.

The visible consequence for players is that borders are always square and always
aligned to the world grid — which is also what makes [[map-integration]] cheap to
render.

## What a claim controls

Ownership by itself grants nothing. Whether a given player may build inside a
claim is resolved from [[faction-permission]] for members and from
[[faction-flag]] settings for outsiders, allies, and the [[vassalage]] chain.

## Related

How *much* land a faction may claim is capped by [[demesne-limit]], derived from
[[faction-power]]. Claims are also the payload that
[[map-integration]] renders and that [[fiefs]] subdivides.

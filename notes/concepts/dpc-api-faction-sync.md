---
id: dpc-api-faction-sync
title: DPC API Faction Sync
type: concept
tags: [medieval-factions, integration, web, dpc]
summary: A running server can push its faction roster to the community API on a timer — the one code path where a Minecraft server writes to shared public data.
created: 2026-08-07
updated: 2026-08-07
sources:
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/dpc/DpcFactionPayload.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 7-14
    claim: The sync payload for one faction is name, serverId, memberCount, description, and optional serverIp and discordLink.
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/dpc/MfDpcApiService.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 154-162
    claim: An empty roster is never POSTed, because a transient empty read during startup or a reload could otherwise reach the wire and rely on the provider's guards to avoid a faction wipe.
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/resources/config.yml
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 271-281
    claim: The dpc-api config block is disabled by default and holds url, key, server-id, login-reminder, share-server-ip, server-address, discord-link and sync-interval-minutes.
---

A [[medieval-factions]] server can be configured to POST its faction roster to
the community API, which is how live in-game data reaches
[[dansplugins-dot-com]]. It is off by default.

## The wire format

Each faction becomes a `DpcFactionPayload`: `name`, `serverId`, `memberCount`,
`description`, and optionally `serverIp` and `discordLink`. The whole roster is
sent as one JSON array with an `X-API-Key` header, on a timer whose interval is
configurable with a one-minute floor.

Notably absent: [[faction-power]], [[claimed-chunk]] counts, player names,
UUIDs. The payload is a public directory listing, not a data export.

## The empty-roster guard

The most important nine lines in the file refuse to send an empty array, and the
reasoning is written into the comment beside them.

The provider already treats an empty array as a no-op, so sending one
accomplishes nothing. Skipping it here is *defence in depth*: a transient empty
read — faction data not yet loaded during startup, or a reload landing
mid-cycle — can then never reach the wire at all, rather than reaching it and
depending on the provider's guards to avoid what the comment calls a faction
wipe.

The shape of the risk is what makes this worth a note. A POST carries the
server's whole roster, so a bad read is not a bad row — it is a bad *replacement
set*, and the blast radius is a shared registry other people's servers appear
in. Two independent guards for one failure is proportionate when the failure is
someone else's data.

## Other guards in the same file

- The URL is validated as an absolute `http`/`https` URI before use.
- A plain-`http` URL logs a one-time warning that the API key will travel
  unencrypted.
- Strings are truncated to maximum lengths before sending.
- Response bodies are truncated before logging, and the API key is never logged.
- A malformed Discord link is dropped from the payload rather than sent.

## Threading

Collection runs on the main thread, dispatch runs asynchronously — see
[[main-thread-safety]], for which this file is the reference example.

## Related

The receiving end is a separate `dpc-api` service that also backs
[[dansplugins-dot-com]]; the website reads from it rather than from Minecraft.

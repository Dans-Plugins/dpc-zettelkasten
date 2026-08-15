---
id: faction-chat-channel
title: Faction Chat Channel
type: concept
moc: moc-faction-domain-model
tags: [medieval-factions, domain-model, chat]
summary: Three private channels whose audiences are computed from the diplomacy graph at send time rather than from a subscriber list.
created: 2026-08-14
updated: 2026-08-14
sources:
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/chat/MfFactionChatChannel.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 3-8
    claim: There are exactly three faction chat channels — FACTION, VASSALS and ALLIES.
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/player/MfPlayer.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 7-16
    claim: A player's selected chat channel is a nullable field on the persisted player record, defaulting to null.
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/chat/MfChatService.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 37-61
    claim: Recipients are resolved per channel at send time — FACTION reaches the faction's own members, VASSALS walks to the top of the liege chain and reaches that faction's members plus every faction in its vassal tree, and ALLIES reaches own members plus allies whose reverse relationship is also ALLY.
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/chat/MfChatService.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 62-71
    claim: The message is written to the repository on an asynchronous task after delivery, and echoed to the console sender so colour codes survive.
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/chat/MfChatChannelMessage.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 7-15
    claim: A stored chat message carries a timestamp, the sending player id, the faction id, the channel and the raw message text.
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/resources/config.yml
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 103-110
    claim: Each of the three channels has its own configurable format string under the chat key.
---

A player in a [[faction]] can direct their chat to one of three audiences:
`FACTION`, `VASSALS`, or `ALLIES`. The selection is a nullable field on the same
persisted player record that carries [[player-power]] — `null` means ordinary
server chat — so the channel a player was last talking in is stored rather than
held for the session.

## The audience is a query, not a list

No channel has members. Each is a rule evaluated against the diplomacy graph
every time someone speaks, which means the audience tracks
[[faction-relationship]] changes with no subscription to maintain.

- **`FACTION`** — the faction's own members.
- **`VASSALS`** — not the speaker's direct vassals. The service walks the liege
  chain to its **top** and addresses that faction's members plus every faction
  in its vassal tree. Realm-wide chat, reached from anywhere in the hierarchy;
  see [[vassalage]].
- **`ALLIES`** — own members, plus the members of allies **whose alliance is
  reciprocated**. An ally faction is included only if the reverse relationship
  is also `ALLY`.

That last rule is worth noticing. [[faction-relationship]] stores directed
edges, and the service checks the pairing for liege and vassal edges; here the
same suspicion is applied to alliance, at the call site, so a one-sided `ALLY`
row grants no access to allied chat.

## Written down, not read back

After delivery the message is persisted asynchronously as an
`MfChatChannelMessage` — timestamp, sender, faction, channel, and text — keeping
the database write off the main thread, per [[main-thread-safety]]. The service
offers paged reads and a count over a faction's history.

At this commit **nothing outside the `chat` package calls those read methods.**
The log is written and retained; no comment, commit message or document in the
repository records what it is for.

## Formatting

Each channel has a configurable format string under `chat` in `config.yml`, with
placeholders for faction colour, name, role and message. One detail is worth
flagging for anyone editing this code: the hard-coded fallback used when a
format key is missing selects its template from the *sending player's currently
selected channel* rather than from the channel argument the method was called
with. The two normally agree. Nothing in the repository explains the difference.

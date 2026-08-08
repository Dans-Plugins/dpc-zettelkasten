---
id: mailboxes
title: Mailboxes
type: concept
tags: [mailboxes, ecosystem, integration]
summary: A standalone plugin giving players persistent in-game mail with item attachments, and the delivery backend Medieval Factions prefers for offline notifications.
created: 2026-08-07
updated: 2026-08-07
sources:
  - repo: Dans-Plugins/Mailboxes
    path: README.md
    ref: 3f8fb186bbdd067ae893d911b26d065d8f3fdaf8
    claim: Mailboxes lets players and plugins send persistent messages that survive server restarts, supports item attachments, and documents a public API for other plugins.
  - repo: Dans-Plugins/Mailboxes
    path: src/main/java/dansplugins/mailboxes/externalapi/MailboxesAPI.java
    ref: 3f8fb186bbdd067ae893d911b26d065d8f3fdaf8
    claim: Mailboxes exposes a dedicated externalapi package with a MailboxesAPI class and wrapper types for mailboxes and messages.
---

Mailboxes is a standalone plugin: persistent player-to-player mail, with items
attachable to a message. It has no dependency on [[medieval-factions]]. The
relationship runs the other way — the flagship uses it when it is present.

## A deliberate API package

The `externalapi` package is the notable design choice. Rather than letting
other plugins reach into `Mailbox` and `Message` directly, Mailboxes exposes
`MailboxesAPI` plus wrapper types `M_Mailbox` and `M_Message`.

The `M_` prefix marks the boundary: those are the types other plugins are
allowed to hold. Internal classes can then be refactored without breaking
consumers — a discipline worth copying, since most plugins in the organization
have no such boundary and their integrators consequently break on upgrade.

## How the flagship uses it

`MailboxesNotificationService` implements the flagship's [[notification]]
interface by calling `sendPluginMessageToPlayer`. That is the entire
integration: a faction announcement to an offline member becomes a piece of mail
waiting when they next log in.

Because the flagship resolves the plugin by name and returns quietly if it is
absent, Mailboxes remains genuinely optional.

## Item attachments

Attachments make mail an item-transfer channel, not just a message channel —
with configurable limits and permissions, since an unbounded one would be a
duplication and storage problem.

## Related

Mailboxes ships in the curated plugin set on [[dpc-mc-server]], which is where
its interaction with the flagship is exercised.

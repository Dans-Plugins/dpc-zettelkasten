---
id: alternate-account-finder
title: Alternate Account Finder
type: concept
moc: moc-plugin-ecosystem
tags: [alternate-account-finder, moderation, ecosystem, persistence]
summary: A moderation plugin that keeps a permanent per-account login history keyed by encrypted IP address, and reports accounts that share one.
created: 2026-08-24
updated: 2026-08-24
sources:
  - repo: Dans-Plugins/AlternateAccountFinder
    path: src/main/resources/com/dansplugins/detectionsystem/db/migration/V1__Initial_version.sql
    ref: 88353003ae38472975ddd042b830b4447fdbf18a
    lines: 1-8
    claim: The sole table holds one row per (address, player UUID) pair, storing a login count and the first and last login timestamps for that pair, with the pair as the primary key.
  - repo: Dans-Plugins/AlternateAccountFinder
    path: src/main/java/com/dansplugins/detectionsystem/logins/LoginRepository.java
    ref: 88353003ae38472975ddd042b830b4447fdbf18a
    lines: 95-112
    claim: Potential alternate accounts are found by self-joining the login table on equal stored address values and selecting the distinct other UUIDs, not by comparing a single last-known IP.
  - repo: Dans-Plugins/AlternateAccountFinder
    path: src/main/java/com/dansplugins/detectionsystem/logins/LoginRepository.java
    ref: 88353003ae38472975ddd042b830b4447fdbf18a
    lines: 22-135
    claim: The repository exposes only reads and an upsert that increments the login counter; it contains no operation that deletes or expires a login record.
  - repo: Dans-Plugins/AlternateAccountFinder
    path: src/main/java/com/dansplugins/detectionsystem/encryption/IpEncryption.java
    ref: 88353003ae38472975ddd042b830b4447fdbf18a
    lines: 18-50
    claim: Addresses are stored as Base64 AES/ECB ciphertext under a fixed on-disk key, and the class documents that determinism is required so encrypted IPs can be compared for equality in database lookups.
  - repo: Dans-Plugins/AlternateAccountFinder
    path: src/main/java/com/dansplugins/detectionsystem/listeners/PlayerJoinListener.java
    ref: 88353003ae38472975ddd042b830b4447fdbf18a
    lines: 26-64
    claim: Every player join records a login, and moderators listed in notify-users are notified only when that join is the account's first from that address.
---

Two accounts that have connected from the same IP address are probably one
person. Alternate Account Finder acts on that inference: it accumulates a login
history per account and surfaces accounts whose histories overlap.

## What is stored

The plugin keeps one row per *(address, account)* pair — the address, the
player's UUID, a login counter, and the first and last login timestamps for that
pair. This is not a last-known-IP field: every distinct address an account has
ever connected from keeps its own row, and a repeat login from a known address
increments that row's counter and refreshes its `last_login`.

Nothing removes those rows. The repository offers reads and an upsert and no
delete; there is no retention window, purge command, or expiry setting anywhere
in the plugin. Login history therefore lives as long as the database does. No
comment, migration note, or document in the repository explains that choice, so
the reason is not recorded.

Addresses are not stored in plaintext. They are AES-encrypted under a 256-bit
key kept in the plugin's data folder, in ECB mode with no IV — deliberately, and
the class says why: the lookups are equality comparisons on the stored value, so
the ciphertext has to be deterministic. The same comment names the cost, that
ECB leaks the pattern of repeated addresses, and scopes the class to this use
only. Losing the key makes the history undecryptable, which the plugin warns
about loudly on startup.

## Finding alts

A query self-joins the table against itself on equal stored addresses and
returns the distinct other UUIDs. Because the comparison is on ciphertext and
the encryption is deterministic, the join works without decrypting anything.
It is a single hop: accounts that share an address directly, not alts-of-alts.

Detection runs on join. The address is read on the main thread — the comment
cites issue #65, where it could be null by the time an async task ran — and the
write happens off-thread, the same split described in [[main-thread-safety]].
A notification fires only on an account's first login from a given address, so
regulars do not re-alert.

## Related

Storage is the [[jooq-persistence]] stack the community uses generally, behind a
[[repository-pattern]] boundary. Notifications go through the same optional
backend selection as [[notification]], preferring [[mailboxes]] when installed.

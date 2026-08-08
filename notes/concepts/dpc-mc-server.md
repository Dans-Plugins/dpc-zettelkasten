---
id: dpc-mc-server
title: DPC Minecraft Server
type: concept
moc: moc-web-and-infrastructure
tags: [dpc, infrastructure, testing]
summary: An infrastructure-as-code Spigot server that pins a curated set of DPC plugin jars into a Docker image, each toggleable by environment variable.
created: 2026-08-07
updated: 2026-08-07
sources:
  - repo: Dans-Plugins/dpc-mc-server
    path: README.md
    ref: d42e0ec06f9b29baaa043442d24ef2dd81edfa49
    claim: The server is a Docker-based reproducible Spigot server pre-loaded with a curated set of DPC plugins, each toggleable via .env, and also bundles Dynmap, BlueMap, PlaceholderAPI, ViaVersion and ViaBackwards.
  - repo: Dans-Plugins/dpc-mc-server
    path: compose.yml
    ref: d42e0ec06f9b29baaa043442d24ef2dd81edfa49
    claim: Each bundled plugin has its own <PLUGIN>_ENABLED environment variable passed into the container, and ports 25565, 8123 and 8100 are exposed for the game server and the two web maps.
---

dpc-mc-server is the community's server as code: a `Dockerfile` and a
`compose.yml` that produce a Spigot server with eighteen DPC plugins already
installed.

## Pinned jars, not downloads

Plugin jars are committed under `resources/jars/` at explicit versions —
`Fiefs-0.10.jar`, `Dans-Essentials-2.3.0.jar`, and so on. The image does not
fetch the latest release at build time.

That is the opposite choice from [[dans-plugin-manager]], and for a good reason:
this repository's value is that a given commit always produces the same server.
The cost is that upgrading a plugin is a commit, and the pinned set drifts behind
current releases until someone updates it.

## A toggle per plugin

Every plugin has a `<PLUGIN>_ENABLED` environment variable threaded from `.env`
through `compose.yml` into the container. Bisecting a plugin interaction is
therefore a matter of flipping variables and restarting, with no image rebuild.

Ports 25565 (game), 8123 (Dynmap), and 8100 (BlueMap) are exposed, so both
[[map-integration]] surfaces can be compared side by side against the same world.

## The de facto integration environment

Because it runs [[medieval-factions]], [[fiefs]], [[currencies]], and
[[mailboxes]] together, this is where cross-plugin behaviour actually gets
exercised. [[testing-and-ci]] covers per-repository testing; nothing else in the
organization tests the plugins as a set.

## The deposit box

A `deposit-box/` directory is bind-mounted into the container, with a
`plugin-overrides/` subdirectory — the hatch for dropping a locally built jar
over a pinned one without rebuilding the image. That is the loop for testing an
unreleased change against the full plugin set.

## Related

Third-party plugins are bundled alongside the community's own, so the
environment matches what a real server operator would run.

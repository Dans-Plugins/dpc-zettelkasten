---
id: dans-plugin-manager
title: Dan's Plugin Manager
type: concept
moc: moc-plugin-ecosystem
tags: [dpm, ecosystem, tooling]
summary: A plugin that installs other DPC plugins from in-game or the console, pulling releases straight from GitHub.
created: 2026-08-07
updated: 2026-08-23
sources:
  - repo: Dans-Plugins/Dans-Plugin-Manager
    path: README.md
    ref: 3733eb51df6be11ac0239d7cffcfb2ef72e756a9
    claim: Dan's Plugin Manager lets server operators download DPC plugins in-game or from the server console.
  - repo: Dans-Plugins/Dans-Plugin-Manager
    path: COMMANDS.md
    ref: 3733eb51df6be11ac0239d7cffcfb2ef72e756a9
    claim: The command set covers list, get, update, remove, clean, search, info, stats and reload, with info reporting the description, GitHub owner, repo, release channel, latest build on that channel, publish date, install status and dependency status.
---

DPM is a package manager for the community's own plugins, run from inside a
Minecraft server. `/dpm get medieval-factions` downloads the latest release jar
into the plugins folder.

## A package manager's vocabulary

The command set is the giveaway: `list`, `get`, `update`, `remove`, `search`,
`info`, `clean`. These are apt and dnf commands, ported to a game console.

`/dpm info` is the most useful of them — it reports the GitHub owner and repo,
which [[release-channel|channel]] the plugin is on and the latest build on that
channel, its publish date, whether the plugin is installed, and **whether its
dependencies are satisfied**. That last field matters in an
ecosystem where [[expansion-plugin|expansions]] hard-depend on
[[medieval-factions]] and simply fail to load without it.

DPM does not only choose *which plugin* to install but *which build* of it: each
managed plugin tracks a [[release-channel]], either published releases or a
rolling build of `main`, and the choice sticks until it is changed.

`/dpm clean` addresses the failure mode that follows from downloading jars: two
versions of the same plugin left in the folder. Like `remove`, it previews by
default and requires `--confirm` to actually delete — a good default for a
command that removes files from a live server.

## GitHub releases as the registry

There is no separate package index. DPM reads GitHub releases directly, which is
why [[release-automation]] matters operationally rather than merely
cosmetically: a release without an attached jar is invisible to DPM. A
configurable `githubToken` exists for rate limits.

## Related

DPM solves plugin distribution for an operator's own server;
[[dpc-mc-server]] solves it by pinning jars into a Docker image instead. The two
answer the same question with opposite trade-offs — live and current, versus
reproducible and fixed.

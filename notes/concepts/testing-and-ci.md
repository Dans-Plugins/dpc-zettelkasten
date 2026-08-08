---
id: testing-and-ci
title: Testing and CI
type: concept
tags: [dpc, conventions, ci, testing]
summary: Gradle for unit tests with Bukkit mocked out, plus a Docker Compose Spigot server for anything that cannot be isolated.
created: 2026-08-07
updated: 2026-08-07
sources:
  - repo: Dans-Plugins/dpc-conventions
    path: docs/TESTING_AND_CI.md
    ref: 9dc9aa37e9ed58722d86a914c563b5ceeaa07bec
    claim: DPC plugins use Gradle as build tool and test runner, run tests with ./gradlew clean test, mock Bukkit types with a library such as Mockito, and provide a Docker Compose Spigot server for integration testing.
  - repo: Dans-Plugins/Medieval-Factions
    path: compose.yml
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    claim: The flagship ships the Docker Compose test server the convention describes, alongside up.sh and down.sh helper scripts.
---

Testing a Bukkit plugin is awkward: the server API is not available outside a
running server, and most interesting behaviour involves it. DPC's answer is two
tiers.

## Unit tests, with Bukkit mocked

Gradle is the build tool and the test runner. `./gradlew clean test` is the
command in every repository, and tests live in `src/test/` mirroring the main
source tree. `Player`, `World`, and `Server` are stubbed with a mocking library.

The architectural payoff of [[repository-pattern]] shows up here: a service can
be tested against a fake repository with no database and no server, which is why
that indirection earns its keep even though the storage has never actually been
swapped.

## Integration tests, with a real server

Anything that cannot be isolated gets a real Spigot server in Docker. Each
repository ships a `compose.yml`, a `sample.env` to copy to `.env`, and `up.sh`
and `down.sh` scripts. The flow is: build the jar with Gradle, bring the
container up, and the plugin is loaded into a real server.

The honest reading of the convention is that the mocking tier has limits, and
rather than pretending otherwise it names the fallback: "when behaviour cannot
be unit-tested in isolation, cover it with integration tests in the Docker-based
test server instead."

## The whole-ecosystem tier

[[dpc-mc-server]] extends the same idea across plugins — a container running the
curated set together, which is where interactions between
[[expansion-plugin|expansions]] and the flagship actually get exercised.

## Related

[[release-automation]] is the other half of the CI story.

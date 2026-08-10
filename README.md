# DPC Zettelkasten

A linked knowledge base for the [Dans Plugins Community](https://github.com/Dans-Plugins)
— an Obsidian-style collection of Markdown notes about how the community's
plugins actually work, where **every claim is traceable to code**.

The rule the whole repository is built around:

> Every concept note cites at least one source of truth from a Dans-Plugins
> repository, pinned at a commit SHA.

Not a branch. A SHA. A citation to `blob/main/...` is true only until someone
pushes; a citation to a commit is true forever, and tooling can then tell you,
separately, whether the code has moved on since.

## Explore it

Open [`site/index.html`](site/index.html) in a browser. No server, no build step,
no network — the whole collection is embedded in one self-contained file.

| | |
|---|---|
| **Notes** | Rendered Markdown with working `[[wikilinks]]`, grouped by cluster |
| **Backlinks** | Every note shows what links to it, not just what it links to |
| **Sources** | Each note's citations, one click from the exact lines on GitHub |
| **Graph** | Force-directed view of the whole collection — press `g` |
| **GraphQL** | Query the note graph and draw the result — press `q` |
| **Search** | Full-text across titles, summaries, and bodies — press `/` |

To serve it instead of opening the file — the same image the gateway deploys:

```bash
docker build -t dpc-zettelkasten .
docker run --rm -p 8080:8080 dpc-zettelkasten
```

The explorer is then at <http://localhost:8080>, with `dataset.json` alongside
it and a `/healthz` endpoint for the container healthcheck.

### Querying the graph

The **GraphQL** tab is a real query engine over the collection — schema,
parser, and executor, all in the page, no server. Ask structural questions and
get answers:

```graphql
{
  notes(orderBy: degree, first: 5) {
    title
    degree
    moc { title }
  }
}
```

Every result can be flipped from JSON to a **graph of exactly the notes that
query touched**, which is the fastest way to see a cluster's real shape rather
than the shape its MOC claims. The schema is in the left pane; eight worked
examples are one click away.

The notes also open directly in [Obsidian](https://obsidian.md/): point a vault
at this repository and wikilinks, backlinks, and the graph view all work
natively. GitHub renders them as ordinary Markdown too.

## What's in it

45 notes: 7 Maps of Content and 38 concept notes, carrying 90 citations across 9
repositories.

The collection is a hierarchy, not a heap. [Dan's Plugins
Community](notes/moc/moc-dans-plugins-community.md) is a **map of maps** — it
holds no claims, it routes. Every concept note declares exactly one home MOC,
and `validate.py` fails the build if that MOC does not link back.

```
Dan's Plugins Community          the root map — an index of indexes
├── Medieval Factions Map        the flagship, which needs two maps of its own
│   ├── Faction Domain Model     14 notes — what the simulation is
│   └── Plugin Architecture      10 notes — how the code is arranged
├── Plugin Ecosystem              6 notes — library, expansions, neighbours
├── Conventions and Process       4 notes — the organization's standards
└── Web and Infrastructure        3 notes — the site, the server, the pipe
```

From the root map:

- [Medieval Factions Map](notes/moc/moc-medieval-factions.md) — the flagship, indexed
- [Faction Domain Model](notes/moc/moc-faction-domain-model.md) — the nouns of the simulation
- [Plugin Architecture](notes/moc/moc-plugin-architecture.md) — how it is built
- [Plugin Ecosystem](notes/moc/moc-plugin-ecosystem.md) — the library, expansions, and neighbours
- [Conventions and Process](notes/moc/moc-conventions-and-process.md) — the org's standards
- [Web and Infrastructure](notes/moc/moc-web-and-infrastructure.md) — the site and the server

## Layout

```
notes/
  moc/          Maps of Content — curated entry points, no original claims
  concepts/     One idea per note, each with pinned citations
docs/
  NOTE_FORMAT.md   The rules: frontmatter, citations, wikilinks
  SOURCES.md       Generated index of every pinned commit
lib/
  zk-graphql.js    The GraphQL schema + engine, shared by the explorer and MCP
tools/            Dependency-free Python 3.8+ toolchain
site/
  index.html       The generated explorer (committed, so it works on clone)
  dataset.json     The same graph as data, for non-browser consumers
.claude/skills/   Skills for growing and auditing the collection
```

## Working on it

Nothing to install — the toolchain is standard library only.

```bash
python3 tools/validate.py       # frontmatter, ids, wikilinks, citation presence
python3 tools/check_sources.py  # citations resolve on GitHub; report drift  (needs `gh`)
python3 tools/sources_index.py  # regenerate docs/SOURCES.md
python3 tools/build.py          # regenerate site/index.html
```

`validate.py` and `build.py` run offline and are what CI enforces.
`check_sources.py` needs an authenticated [`gh`](https://cli.github.com/).

**After changing any note, rebuild and commit `site/index.html` and
`site/dataset.json`.** Both are generated files kept in the repository so the
explorer works straight from a clone and downstream consumers have something
stable to fetch. CI fails if either is stale.

## Consuming it elsewhere

`lib/zk-graphql.js` is the schema and engine as a standalone module, and
`site/dataset.json` is the same graph the explorer uses with the rendered HTML
swapped for raw Markdown. Together they run anywhere Node does:

```js
const { createEngine } = require("./lib/zk-graphql.js");
const engine = createEngine(require("./site/dataset.json"));
engine.execute("{ notes(orderBy: degree, first: 5) { title degree } }");
```

[**dpc-mcp-server**](https://github.com/Dans-Plugins/dpc-mcp-server) is built on
exactly this, exposing the collection to any MCP client so an agent can query
the graph and read the citations behind a claim.

### From a browser, on another origin

The container serves `dataset.json` and `lib/zk-graphql.js` with
`Access-Control-Allow-Origin: *`, so any page can run the same engine over the
same data without a build step. The module is UMD, so a plain script tag is
enough:

```html
<script src="https://zettel.dansplugins.com/lib/zk-graphql.js"></script>
<script>
  const data = await (await fetch("https://zettel.dansplugins.com/dataset.json")).json();
  const engine = ZKGraphQL.createEngine(data);
  engine.execute("{ stats { noteCount citationCount } }");
</script>
```

The open policy is deliberate: both files are public artifacts of a public
repository and are served without credentials, so there is nothing an allowlist
would protect. The reasoning is recorded in `docker/nginx.conf`.

## Skills

Two [Claude Code](https://claude.com/claude-code) skills live in `.claude/skills/`
and are the intended way to grow and maintain the collection:

- **`/zettelkasten-expand`** — finds parts of the organization the collection
  does not yet describe, and writes grounded notes for them.
- **`/zettelkasten-verify`** — audits existing notes against their cited sources,
  reports drift, and corrects what has gone stale.

Both are described in [CONTRIBUTING.md](CONTRIBUTING.md). Neither is required —
notes are plain Markdown and can be written by hand.

## Scope

This collection describes repositories in the **Dans-Plugins** organization.
Citations to anywhere else are rejected by `validate.py`. That constraint is the
point: it is what keeps the collection a description of this codebase rather
than a general wiki about Minecraft plugins.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md), and read
[docs/NOTE_FORMAT.md](docs/NOTE_FORMAT.md) before writing a note.

Found a note that is wrong? That is the most valuable kind of issue here — open
one with the note id and the source that contradicts it.

## License

[MIT](LICENSE). The notes describe code in the Dans-Plugins organization; each
cited repository keeps its own license.

#!/usr/bin/env python3
"""Build the offline zettelkasten explorer.

Renders every note to HTML and embeds the whole graph in a single
self-contained `site/index.html` that works from the filesystem with no server,
no network, and no build dependencies.

Also writes `site/dataset.json` (the graph as data) and `site/version.json`
(`{"version": ...}` from the repository's `version.txt`), so a deploy can be
verified by the version it reports.

Also writes one static page per note to `site/notes/<id>.html`, plus
`site/sitemap.xml` and `site/robots.txt`, all with absolute URLs on the
production origin (SITE_ORIGIN) so search engines and link previews can see
the collection.

Usage:
    python3 tools/build.py [--out site/index.html]
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import md  # noqa: E402
import zklib  # noqa: E402
import re  # noqa: E402

TEMPLATE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "template.html")
NOTE_TEMPLATE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "note_template.html")
# The production origin, used for every absolute URL the build writes: the
# canonical links, og:url, sitemap.xml and robots.txt. It is a constant rather
# than an environment variable on purpose — the generated files are committed,
# so a build that silently picked up a different (or missing) value would
# commit wrong URLs that CI would then enforce.
SITE_ORIGIN = "https://zettel.dansplugins.com"
SITE_DESCRIPTION = (
    "A linked knowledge base for the Dans Plugins Community: notes on how the "
    "community's Minecraft plugins actually work, where every claim cites "
    "source code pinned at a commit SHA."
)
# Static, crawlable copies of each note live here (site/notes/<id>.html). The
# explorer itself routes by URL fragment, which crawlers and link previews never
# see, so these are what the sitemap lists and what a shared link unfurls.
NOTES_OUT_DIRNAME = "notes"
ENGINE_PATH = os.path.join(zklib.REPO_ROOT, "lib", "zk-graphql.js")
GITHUB_BASE = "https://github.com/Dans-Plugins/dpc-zettelkasten/blob/main/"
ROOT_MOC = "moc-dans-plugins-community"
VERSION_PATH = os.path.join(zklib.REPO_ROOT, "version.txt")
VERSION_PATTERN = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.+-]+)?$")


def read_version(path=VERSION_PATH):
    """The repository's version: the one line of version.txt."""
    try:
        with open(path, "r", encoding="utf-8") as handle:
            version = handle.read().strip()
    except OSError as exc:
        zklib.fail("cannot read %s: %s" % (os.path.relpath(path, zklib.REPO_ROOT), exc))
    if not VERSION_PATTERN.match(version):
        zklib.fail("%s must hold one version such as 1.2.3, not %r"
                   % (os.path.relpath(path, zklib.REPO_ROOT), version))
    return version


def explorer_href(target, anchor):
    """A link inside the explorer: a hash route, so it works from file://."""
    return "#/" + target + (("#" + md.slugify(anchor)) if anchor else "")


def static_href(target, anchor):
    """A link between the static note pages, which all sit in one directory."""
    return target + ".html" + (("#" + md.slugify(anchor)) if anchor else "")


def make_wikilink_renderer(by_id, note_id, unresolved, href_for=explorer_href):
    def wikilink(target, anchor, label):
        text = label or (by_id[target].title if target in by_id else target)
        if target not in by_id:
            unresolved.append((note_id, target))
            return '<span class="wl broken" title="no note with id \'%s\'">%s</span>' % (
                md.escape(target), md.escape(text)
            )
        href = href_for(target, anchor)
        return '<a class="wl" href="%s" data-id="%s">%s</a>' % (
            md.escape(href), md.escape(target), md.escape(text)
        )
    return wikilink


def heading_text(text, by_id):
    """Plain text for a heading, with wikilinks resolved to their display form.

    A heading such as `## [[moc-plugin-architecture|How it is built]]` must read
    as "How it is built" in the table of contents, not as raw wikilink syntax.
    """
    def replace(match):
        target, _, label = match.group(1).partition("|")
        target = target.strip()
        if label:
            return label.strip()
        return by_id[target].title if target in by_id else target
    return re.sub(r"\[\[([^\]]+)\]\]", replace, text)


def build_payload(notes):
    by_id = zklib.index_by_id(notes)
    backlinks = zklib.backlink_map(notes)
    unresolved = []
    payload = {}

    for note in notes:
        headings = []
        html = md.render(
            note.body,
            wikilink=make_wikilink_renderer(by_id, note.id, unresolved),
            headings=headings,
        )
        sources = []
        for source in note.sources:
            sources.append({
                "repo": source["repo"],
                "path": source["path"],
                "ref": source["ref"],
                "shortRef": source["ref"][:7],
                "lines": source.get("lines", ""),
                "claim": source.get("claim", ""),
                "url": zklib.source_url(source),
                "label": zklib.source_label(source),
            })
        payload[note.id] = {
            "id": note.id,
            "title": note.title,
            "type": note.type,
            "moc": note.moc,
            "tags": note.tags,
            "summary": note.summary,
            "updated": note.meta.get("updated", ""),
            "html": html,
            "toc": [
                {"level": lvl, "text": heading_text(txt, by_id), "slug": slug}
                for lvl, txt, slug in headings
            ],
            "links": [t for t in note.links if t in by_id],
            "backlinks": backlinks.get(note.id, []),
            "sources": sources,
            "sourcePath": note.rel_path,
            "sourceUrl": GITHUB_BASE + note.rel_path,
            "text": (note.title + " " + note.summary + " " + note.body).lower(),
        }

    return payload, unresolved


def moc_order(notes):
    """MOC ids with the root first, then in the order the root links them."""
    by_id = dict((n.id, n) for n in notes)
    order = [ROOT_MOC] if ROOT_MOC in by_id else []
    root = by_id.get(ROOT_MOC)
    if root:
        for target in root.links:
            if target in by_id and by_id[target].type == "moc" and target not in order:
                order.append(target)
    for note in sorted(notes, key=lambda n: n.title):
        if note.type == "moc" and note.id not in order:
            order.append(note.id)
    return order


def clusters(notes, payload):
    """Ordered [{moc, title, notes:[id]}] for the grouped sidebar.

    Cluster order follows the order the root map links its sub-maps, so the
    sidebar and the landing page present the collection in the same sequence
    rather than disagreeing about it. The root itself is not a cluster — it
    holds no concepts, it routes to the ones that do.
    """
    by_id = dict((n.id, n) for n in notes)
    homed = {}
    for note in notes:
        if note.moc:
            homed.setdefault(note.moc, []).append(note.id)

    order = []
    root = by_id.get(ROOT_MOC)
    if root:
        for target in root.links:
            if (target in by_id and by_id[target].type == "moc"
                    and target != ROOT_MOC and target not in order):
                order.append(target)
    for note in sorted(notes, key=lambda n: n.title):
        if note.type == "moc" and note.id != ROOT_MOC and note.id not in order:
            order.append(note.id)

    out = []
    for moc_id in order:
        members = sorted(homed.get(moc_id, []), key=lambda i: payload[i]["title"])
        if members:
            out.append({"moc": moc_id, "title": by_id[moc_id].title, "notes": members})

    placed = set(i for c in out for i in c["notes"])
    stray = sorted(
        (n.id for n in notes if n.type == "concept" and n.id not in placed),
        key=lambda i: payload[i]["title"],
    )
    if stray:
        out.append({"moc": "", "title": "Unclustered", "notes": stray})
    return out


def fill(template, values):
    """Substitute {{key}} placeholders in one pass.

    One pass, so text substituted in (a rendered note body, say) is never
    itself scanned for placeholders.
    """
    return re.sub(r"\{\{(\w+)\}\}", lambda m: values[m.group(1)], template)


def note_url(note_id):
    return "%s/%s/%s.html" % (SITE_ORIGIN, NOTES_OUT_DIRNAME, note_id)


def render_note_pages(notes, payload):
    """{filename: html} — one static page per note, for crawlers and sharing."""
    by_id = zklib.index_by_id(notes)
    with open(NOTE_TEMPLATE_PATH, "r", encoding="utf-8") as handle:
        template = handle.read()

    pages = {}
    for note in notes:
        record = payload[note.id]
        body = md.render(
            note.body,
            wikilink=make_wikilink_renderer(by_id, note.id, [], href_for=static_href),
        )

        sources = ""
        if record["sources"]:
            items = []
            for source in record["sources"]:
                claim = ""
                if source["claim"]:
                    claim = ' <span class="claim">— %s</span>' % md.escape(source["claim"])
                items.append('<li><a href="%s" rel="noopener noreferrer">%s</a>%s</li>' % (
                    md.escape(source["url"]), md.escape(source["label"]), claim))
            sources = ('<section class="meta"><h2>Sources</h2>\n<ul>\n%s\n</ul></section>'
                       % "\n".join(items))

        backlinks = ""
        if record["backlinks"]:
            items = ['<li><a href="%s">%s</a></li>' % (
                md.escape(static_href(b, None)), md.escape(payload[b]["title"]))
                for b in record["backlinks"] if b in payload]
            backlinks = ('<section class="meta"><h2>Linked from</h2>\n<ul>\n%s\n</ul></section>'
                         % "\n".join(items))

        description = note.summary or SITE_DESCRIPTION
        pages[note.id + ".html"] = fill(template, {
            "id": md.escape(note.id),
            "title": md.escape(note.title),
            "summary": md.escape(note.summary),
            "description": md.escape(description),
            "url": md.escape(note_url(note.id)),
            "sourceUrl": md.escape(record["sourceUrl"]),
            "body": body,
            "sources": sources,
            "backlinks": backlinks,
        })
    return pages


def render_sitemap(notes, meta):
    """sitemap.xml: the explorer plus every static note page.

    lastmod comes from each note's `updated` date, never the clock, so the
    build stays reproducible and CI can diff it.
    """
    def entry(loc, lastmod):
        line = "  <url><loc>%s</loc>" % md.escape(loc)
        if lastmod:
            line += "<lastmod>%s</lastmod>" % md.escape(lastmod)
        return line + "</url>"

    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
             entry(SITE_ORIGIN + "/", meta["updated"])]
    for note in sorted(notes, key=lambda n: n.id):
        lines.append(entry(note_url(note.id), note.meta.get("updated", "")))
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def render_robots():
    return "User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % SITE_ORIGIN


def write_text(path, text):
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=os.path.join("site", "index.html"))
    parser.add_argument("--dataset", default=os.path.join("site", "dataset.json"),
                        help="where to write the machine-readable graph consumed by dpc-mcp-server")
    parser.add_argument("--version-out", default=os.path.join("site", "version.json"),
                        help="where to write {\"version\": ...}, read from version.txt")
    args = parser.parse_args()
    version = read_version()

    try:
        notes = zklib.load_notes()
        payload, unresolved = build_payload(notes)
    except zklib.NoteError as exc:
        zklib.fail(str(exc))

    for note_id, target in unresolved:
        sys.stderr.write("warning: %s links to unknown note [[%s]]\n" % (note_id, target))

    repos = {}
    for note in notes:
        for source in note.sources:
            repos.setdefault(source["repo"], set()).add(source["ref"])

    # Derived from the notes, never from the clock: the build must be
    # reproducible so CI can diff a fresh build against the committed
    # site/index.html and detect a stale one.
    meta = {
        "updated": max([n.meta.get("updated", "") for n in notes] or [""]),
        "noteCount": len(notes),
        "mocCount": sum(1 for n in notes if n.type == "moc"),
        "conceptCount": sum(1 for n in notes if n.type == "concept"),
        "citationCount": sum(len(n.sources) for n in notes),
        "linkCount": sum(len(payload[n.id]["links"]) for n in notes),
        "repos": sorted(repos),
        "home": ROOT_MOC if ROOT_MOC in payload else sorted(payload)[0],
        # Sidebar order: the root map first, then each cluster with the concepts
        # that call it home. Computed here so the page needs no grouping logic.
        "clusters": clusters(notes, payload),
        "mocOrder": moc_order(notes),
    }

    with open(TEMPLATE_PATH, "r", encoding="utf-8") as handle:
        template = handle.read()
    with open(ENGINE_PATH, "r", encoding="utf-8") as handle:
        engine = handle.read()

    html = template.replace(
        "{{siteUrl}}", md.escape(SITE_ORIGIN + "/")
    ).replace(
        "{{siteDescription}}", md.escape(SITE_DESCRIPTION)
    ).replace(
        "/*__ZKGRAPHQL__*/", engine
    ).replace(
        "/*__NOTES__*/null", json.dumps(payload, ensure_ascii=False, sort_keys=True)
    ).replace(
        "/*__META__*/null", json.dumps(meta, ensure_ascii=False, sort_keys=True)
    )

    out_path = os.path.join(zklib.REPO_ROOT, args.out) if not os.path.isabs(args.out) else args.out
    out_dir = os.path.dirname(out_path)
    if out_dir and not os.path.isdir(out_dir):
        os.makedirs(out_dir)
    with open(out_path, "w", encoding="utf-8") as handle:
        handle.write(html)

    # The same graph, minus the rendered HTML and plus the raw Markdown, for
    # consumers that are not a browser — chiefly dpc-mcp-server.
    dataset = {"meta": meta, "notes": {}}
    for note in notes:
        record = dict(payload[note.id])
        record.pop("html", None)
        record.pop("toc", None)
        record["body"] = note.body
        dataset["notes"][note.id] = record
    data_path = (os.path.join(zklib.REPO_ROOT, args.dataset)
                 if not os.path.isabs(args.dataset) else args.dataset)
    data_dir = os.path.dirname(data_path)
    if data_dir and not os.path.isdir(data_dir):
        os.makedirs(data_dir)
    with open(data_path, "w", encoding="utf-8") as handle:
        json.dump(dataset, handle, ensure_ascii=False, sort_keys=True, indent=1)
        handle.write("\n")

    # Served at /version.json so a deploy can be checked against the version it
    # reports. Exactly one key, no indentation: it is a contract, not a document.
    version_path = (os.path.join(zklib.REPO_ROOT, args.version_out)
                    if not os.path.isabs(args.version_out) else args.version_out)
    with open(version_path, "w", encoding="utf-8") as handle:
        json.dump({"version": version}, handle)
        handle.write("\n")

    # Static note pages, sitemap.xml and robots.txt sit next to index.html.
    # Pages for notes that no longer exist are removed, so a deleted note does
    # not linger as a committed (and served) orphan.
    pages = render_note_pages(notes, payload)
    pages_dir = os.path.join(out_dir, NOTES_OUT_DIRNAME)
    if not os.path.isdir(pages_dir):
        os.makedirs(pages_dir)
    for name in os.listdir(pages_dir):
        if name.endswith(".html") and name not in pages:
            os.remove(os.path.join(pages_dir, name))
    for name, page in sorted(pages.items()):
        write_text(os.path.join(pages_dir, name), page)
    write_text(os.path.join(out_dir, "sitemap.xml"), render_sitemap(notes, meta))
    write_text(os.path.join(out_dir, "robots.txt"), render_robots())

    print(
        "built %s — %d notes (%d MOCs, %d concepts), %d links, %d citations across %d repos"
        % (
            os.path.relpath(out_path, zklib.REPO_ROOT),
            meta["noteCount"], meta["mocCount"], meta["conceptCount"],
            meta["linkCount"], meta["citationCount"], len(meta["repos"]),
        )
    )
    print("wrote %s — %d notes with Markdown bodies"
          % (os.path.relpath(data_path, zklib.REPO_ROOT), len(dataset["notes"])))
    print("wrote %s — version %s" % (os.path.relpath(version_path, zklib.REPO_ROOT), version))
    print("wrote %s — %d note pages, sitemap.xml and robots.txt for %s"
          % (os.path.relpath(pages_dir, zklib.REPO_ROOT), len(pages), SITE_ORIGIN))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Build the offline zettelkasten explorer.

Renders every note to HTML and embeds the whole graph in a single
self-contained `site/index.html` that works from the filesystem with no server,
no network, and no build dependencies.

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
ENGINE_PATH = os.path.join(zklib.REPO_ROOT, "lib", "zk-graphql.js")
GITHUB_BASE = "https://github.com/Dans-Plugins/dpc-zettelkasten/blob/main/"
ROOT_MOC = "moc-dans-plugins-community"


def make_wikilink_renderer(by_id, note_id, unresolved):
    def wikilink(target, anchor, label):
        text = label or (by_id[target].title if target in by_id else target)
        if target not in by_id:
            unresolved.append((note_id, target))
            return '<span class="wl broken" title="no note with id \'%s\'">%s</span>' % (
                md.escape(target), md.escape(text)
            )
        href = "#/" + target + (("#" + md.slugify(anchor)) if anchor else "")
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=os.path.join("site", "index.html"))
    parser.add_argument("--dataset", default=os.path.join("site", "dataset.json"),
                        help="where to write the machine-readable graph consumed by dpc-mcp-server")
    args = parser.parse_args()

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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

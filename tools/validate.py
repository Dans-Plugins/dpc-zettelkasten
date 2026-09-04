#!/usr/bin/env python3
"""Validate every note in the zettelkasten.

Checks the rules in docs/NOTE_FORMAT.md that can be checked without network
access: frontmatter shape, id/filename agreement, wikilink resolution, and the
requirement that every concept note carries at least one pinned citation.

Network-dependent checks (does the cited file still exist at that SHA? has it
drifted since?) live in tools/check_sources.py.

Usage:
    python3 tools/validate.py
    python3 tools/validate.py --check-readme   # also assert README.md's counts
"""

import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import zklib  # noqa: E402

REQUIRED_KEYS = ("id", "title", "type", "summary")

# The root map is a map of maps: it holds no claims and homes no concept note,
# so the "unreachable MOC" rule exempts it and the README cluster tree heads
# itself with it, uncounted.
ROOT_MOC_ID = "moc-dans-plugins-community"

README_PATH = os.path.join(zklib.REPO_ROOT, "README.md")

# "49 notes: 7 Maps of Content and 42 concept notes, carrying 116 citations
# across 9 repositories." — matched across line breaks, since the sentence is
# wrapped in the file.
README_SUMMARY_RE = re.compile(
    r"(?P<notes>\d+)\s+notes:\s+(?P<mocs>\d+)\s+Maps\s+of\s+Content\s+and\s+"
    r"(?P<concepts>\d+)\s+concept\s+notes,\s+carrying\s+(?P<citations>\d+)\s+"
    r"citations\s+across\s+(?P<repos>\d+)\s+repositories"
)

# "│   ├── Faction Domain Model     16 notes — what the simulation is". The
# label is separated from its count by the column padding.
README_TREE_ROW_RE = re.compile(r"^[^A-Za-z0-9]*(?P<label>.+?)\s{2,}(?P<count>\d+)\s+notes?\b")


def validate_source(note, index, source, problems):
    where = "%s: sources[%d]" % (note.rel_path, index)
    for key in ("repo", "ref", "path", "claim"):
        if not source.get(key):
            problems.append("%s: missing required key %r" % (where, key))
    repo = source.get("repo", "")
    if repo and not zklib.REPO_RE.match(repo):
        problems.append("%s: repo %r is not in owner/name form" % (where, repo))
    if repo and not repo.startswith("Dans-Plugins/"):
        problems.append(
            "%s: repo %r is outside the Dans-Plugins organization; every citation "
            "must point at a Dans-Plugins repository" % (where, repo)
        )
    ref = source.get("ref", "")
    if ref and not zklib.SHA_RE.match(ref):
        problems.append(
            "%s: ref %r must be a full 40-character commit SHA so the link is "
            "immutable" % (where, ref)
        )
    lines = source.get("lines")
    if lines and not zklib.LINES_RE.match(lines):
        problems.append("%s: lines %r must be 'N' or 'N-M'" % (where, lines))
    if lines and "-" in lines:
        start, end = lines.split("-")
        if int(start) > int(end):
            problems.append("%s: lines %r has start after end" % (where, lines))


def fenced_blocks(text):
    """Every fenced code block's contents, so the cluster tree can be located by
    the root map's title rather than by line number. Paired by walking the
    fences: a regex cannot tell an opening fence from a closing one."""
    blocks = []
    current = None
    for line in text.split("\n"):
        if line.startswith("```"):
            if current is None:
                current = []
            else:
                blocks.append("\n".join(current))
                current = None
            continue
        if current is not None:
            current.append(line)
    return blocks


def check_readme(notes, homed, problems):
    """Assert that the size README.md claims is the size the collection has.

    validate.py already computes every number the README states; without this
    the numbers are printed and never compared, so a note can be added with a
    green build and a README that has quietly become wrong.
    """
    try:
        with open(README_PATH, "r", encoding="utf-8") as handle:
            readme = handle.read()
    except IOError as exc:
        problems.append("README.md: cannot be read (%s)" % exc)
        return

    expected = {
        "notes": len(notes),
        "mocs": sum(1 for n in notes if n.type == "moc"),
        "concepts": sum(1 for n in notes if n.type == "concept"),
        "citations": sum(len(n.sources) for n in notes),
        "repos": len(set(s["repo"] for n in notes for s in n.sources)),
    }

    match = README_SUMMARY_RE.search(readme)
    if not match:
        problems.append(
            "README.md: no summary sentence of the form '%d notes: %d Maps of "
            "Content and %d concept notes, carrying %d citations across %d "
            "repositories' — the collection's size is stated there and must stay "
            "checkable"
            % (expected["notes"], expected["mocs"], expected["concepts"],
               expected["citations"], expected["repos"])
        )
    else:
        labels = (
            ("notes", "notes"),
            ("mocs", "Maps of Content"),
            ("concepts", "concept notes"),
            ("citations", "citations"),
            ("repos", "cited repositories"),
        )
        for name, label in labels:
            stated = int(match.group(name))
            if stated != expected[name]:
                problems.append(
                    "README.md: summary says %d %s, the collection has %d"
                    % (stated, label, expected[name])
                )

    tree = None
    root_title = None
    for note in notes:
        if note.id == ROOT_MOC_ID:
            root_title = note.title
    for block in fenced_blocks(readme):
        if root_title and root_title in block:
            tree = block
            break
    if tree is None:
        problems.append(
            "README.md: no cluster tree — expected a fenced block containing %r"
            % (root_title or ROOT_MOC_ID)
        )
        return

    stated_rows = {}
    for line in tree.split("\n"):
        row = README_TREE_ROW_RE.match(line)
        if row:
            stated_rows[row.group("label").strip()] = int(row.group("count"))

    for note in notes:
        if note.type != "moc":
            continue
        count = len(homed.get(note.id, []))
        if note.title not in stated_rows:
            # The root map heads the tree without a count, since it homes no
            # concept note; every other MOC owes the tree a row.
            if note.id != ROOT_MOC_ID:
                problems.append(
                    "README.md: cluster tree has no row for MOC %r (homes %d note(s))"
                    % (note.title, count)
                )
        elif stated_rows[note.title] != count:
            problems.append(
                "README.md: cluster tree says %r homes %d note(s), it homes %d"
                % (note.title, stated_rows[note.title], count)
            )

    titles = set(n.title for n in notes if n.type == "moc")
    for label in sorted(stated_rows):
        if label not in titles:
            problems.append(
                "README.md: cluster tree row %r does not name a MOC" % label
            )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check-readme",
        action="store_true",
        help="also fail when the counts stated in README.md disagree with the collection",
    )
    args = parser.parse_args()

    try:
        notes = zklib.load_notes()
    except zklib.NoteError as exc:
        zklib.fail(str(exc))

    if not notes:
        zklib.fail("no notes found under %s" % zklib.NOTES_DIRNAME)

    problems = []
    try:
        by_id = zklib.index_by_id(notes)
    except zklib.NoteError as exc:
        zklib.fail(str(exc))

    for note in notes:
        for key in REQUIRED_KEYS:
            if not note.meta.get(key):
                problems.append("%s: missing required frontmatter key %r" % (note.rel_path, key))

        expected_id = os.path.splitext(os.path.basename(note.path))[0]
        if note.id != expected_id:
            problems.append(
                "%s: id %r does not match filename %r"
                % (note.rel_path, note.id, expected_id)
            )
        if not zklib.ID_RE.match(note.id):
            problems.append("%s: id %r must be lowercase kebab-case" % (note.rel_path, note.id))

        if note.type not in zklib.VALID_TYPES:
            problems.append(
                "%s: type %r must be one of %s"
                % (note.rel_path, note.type, ", ".join(zklib.VALID_TYPES))
            )

        if note.type == "concept" and not note.sources:
            problems.append(
                "%s: concept notes must cite at least one source of truth from a "
                "Dans-Plugins repository" % note.rel_path
            )

        if note.type == "concept":
            if not note.moc:
                problems.append(
                    "%s: concept notes must declare a home MOC with 'moc: <id>'"
                    % note.rel_path
                )
            elif note.moc not in by_id:
                problems.append(
                    "%s: moc %r does not resolve to any note" % (note.rel_path, note.moc)
                )
            elif by_id[note.moc].type != "moc":
                problems.append(
                    "%s: moc %r is not a note of type 'moc'" % (note.rel_path, note.moc)
                )
            elif note.id not in by_id[note.moc].links:
                problems.append(
                    "%s: home MOC %r does not link back to this note; a note's home "
                    "must list it" % (note.rel_path, note.moc)
                )
        elif note.moc:
            problems.append(
                "%s: only concept notes may declare a home MOC" % note.rel_path
            )

        for i, source in enumerate(note.sources):
            validate_source(note, i, source, problems)

        for target in note.links:
            if target not in by_id:
                problems.append(
                    "%s: wikilink [[%s]] does not resolve to any note" % (note.rel_path, target)
                )

        if not note.body.strip():
            problems.append("%s: note has no body" % note.rel_path)

    # Orphan detection is advisory, not fatal: a brand new note may legitimately
    # have no inbound links yet, but a MOC should always adopt it eventually.
    back = zklib.backlink_map(notes)
    orphans = [n.id for n in notes if not back.get(n.id) and n.type != "moc"]

    # A MOC that no other MOC links to and that holds no concepts is unreachable
    # from the root map, which means nobody browsing will ever find it.
    moc_ids = set(n.id for n in notes if n.type == "moc")
    homed = {}
    for n in notes:
        if n.moc:
            homed.setdefault(n.moc, []).append(n.id)
    for moc in sorted(moc_ids):
        linked_from_moc = any(moc in by_id[m].links for m in moc_ids if m != moc)
        if not linked_from_moc and not homed.get(moc) and moc != ROOT_MOC_ID:
            problems.append(
                "notes/moc/%s.md: MOC is unreachable — no other MOC links it and no "
                "note calls it home" % moc
            )

    if args.check_readme:
        check_readme(notes, homed, problems)

    for problem in problems:
        print("FAIL %s" % problem)

    if orphans:
        print("")
        print("warning: %d note(s) have no inbound links (add them to a MOC):" % len(orphans))
        for orphan in orphans:
            print("  - %s" % orphan)

    print("")
    total_sources = sum(len(n.sources) for n in notes)
    print(
        "checked %d notes (%d MOCs, %d concepts), %d citations, %d problems"
        % (
            len(notes),
            sum(1 for n in notes if n.type == "moc"),
            sum(1 for n in notes if n.type == "concept"),
            total_sources,
            len(problems),
        )
    )
    print("home MOCs:")
    for moc in sorted(moc_ids):
        print("  %-32s %2d concept(s)" % (moc, len(homed.get(moc, []))))
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())

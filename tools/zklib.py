"""Shared parsing and graph utilities for the DPC Zettelkasten.

Deliberately dependency-free: the whole toolchain runs on a stock Python 3.8+
interpreter so that contributors and CI need nothing beyond the standard
library. The frontmatter dialect accepted here is a small, fixed subset of YAML
(see docs/NOTE_FORMAT.md), not general YAML.
"""

import os
import re
import sys

NOTES_DIRNAME = "notes"
VALID_TYPES = ("concept", "moc")

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTES_ROOT = os.path.join(REPO_ROOT, NOTES_DIRNAME)

WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|([^\]]+))?\]\]")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINES_RE = re.compile(r"^\d+(?:-\d+)?$")
REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


class NoteError(Exception):
    pass


# --------------------------------------------------------------------------
# Frontmatter
# --------------------------------------------------------------------------

def _strip_quotes(value):
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def _parse_inline_list(value):
    value = value.strip()
    if not (value.startswith("[") and value.endswith("]")):
        raise NoteError("expected an inline list in [a, b] form, got: %r" % value)
    inner = value[1:-1].strip()
    if not inner:
        return []
    return [_strip_quotes(part) for part in inner.split(",") if part.strip()]


def parse_frontmatter(text, where="<note>"):
    """Split a note into (frontmatter dict, body string).

    Supports exactly what the note format needs: `key: scalar`, `key: [a, b]`,
    and a `key:` followed by a list of `- ` items whose entries are either
    scalars or indented `key: value` mappings.
    """
    if not text.startswith("---\n"):
        raise NoteError("%s: file must begin with a '---' frontmatter fence" % where)
    end = text.find("\n---\n", 3)
    if end == -1:
        raise NoteError("%s: unterminated frontmatter block" % where)
    raw = text[4:end + 1]
    body = text[end + 5:]

    data = {}
    key = None
    items = None
    current = None

    for lineno, line in enumerate(raw.split("\n"), start=2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        stripped = line.strip()

        if indent == 0:
            if items is not None:
                data[key] = items
                items = None
                current = None
            if ":" not in stripped:
                raise NoteError("%s:%d: expected 'key: value'" % (where, lineno))
            key, _, value = stripped.partition(":")
            key = key.strip()
            value = value.strip()
            if not value:
                items = []
                data[key] = items
            elif value.startswith("["):
                data[key] = _parse_inline_list(value)
            else:
                data[key] = _strip_quotes(value)
            continue

        if items is None:
            raise NoteError("%s:%d: indented line outside of a list" % (where, lineno))

        if stripped.startswith("- "):
            entry = stripped[2:].strip()
            if ":" in entry and not entry.startswith(("http://", "https://")):
                k, _, v = entry.partition(":")
                current = {k.strip(): _strip_quotes(v)}
                items.append(current)
            else:
                current = None
                items.append(_strip_quotes(entry))
        else:
            if current is None:
                raise NoteError("%s:%d: continuation line has no list item" % (where, lineno))
            if ":" not in stripped:
                raise NoteError("%s:%d: expected 'key: value' inside list item" % (where, lineno))
            k, _, v = stripped.partition(":")
            current[k.strip()] = _strip_quotes(v)

    if items is not None:
        data[key] = items
    return data, body


# --------------------------------------------------------------------------
# Notes
# --------------------------------------------------------------------------

class Note(object):
    def __init__(self, path, meta, body):
        self.path = path
        self.rel_path = os.path.relpath(path, REPO_ROOT).replace(os.sep, "/")
        self.meta = meta
        self.body = body
        self.id = meta.get("id") or os.path.splitext(os.path.basename(path))[0]
        self.title = meta.get("title") or self.id
        self.type = meta.get("type", "concept")
        self.tags = meta.get("tags") or []
        self.sources = [s for s in (meta.get("sources") or []) if isinstance(s, dict)]
        self.summary = meta.get("summary", "")

    @property
    def links(self):
        """Outgoing wikilink targets, in order of first appearance."""
        seen = []
        for match in WIKILINK_RE.finditer(self.body):
            target = match.group(1).strip()
            if target not in seen:
                seen.append(target)
        return seen


def load_notes(root=None):
    root = root or NOTES_ROOT
    notes = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        for name in sorted(filenames):
            if not name.endswith(".md"):
                continue
            path = os.path.join(dirpath, name)
            with open(path, "r", encoding="utf-8") as handle:
                text = handle.read()
            rel = os.path.relpath(path, REPO_ROOT)
            meta, body = parse_frontmatter(text, where=rel)
            notes.append(Note(path, meta, body))
    return notes


def index_by_id(notes):
    index = {}
    for note in notes:
        if note.id in index:
            raise NoteError(
                "duplicate note id %r in %s and %s"
                % (note.id, index[note.id].rel_path, note.rel_path)
            )
        index[note.id] = note
    return index


def backlink_map(notes):
    """note id -> sorted list of note ids that link to it."""
    back = dict((note.id, set()) for note in notes)
    for note in notes:
        for target in note.links:
            if target in back:
                back[target].add(note.id)
    return dict((k, sorted(v)) for k, v in back.items())


# --------------------------------------------------------------------------
# Sources
# --------------------------------------------------------------------------

def source_url(source):
    """Build a GitHub permalink for a citation pinned at a commit SHA."""
    url = "https://github.com/%s/blob/%s/%s" % (
        source["repo"], source["ref"], source["path"]
    )
    lines = source.get("lines")
    if lines:
        parts = lines.split("-")
        url += "#L%s" % parts[0]
        if len(parts) == 2:
            url += "-L%s" % parts[1]
    return url


def source_label(source):
    label = "%s/%s" % (source["repo"].split("/")[-1], source["path"].split("/")[-1])
    if source.get("lines"):
        label += ":%s" % source["lines"]
    return label


def fail(message):
    sys.stderr.write("error: %s\n" % message)
    raise SystemExit(1)

"""A small, dependency-free Markdown renderer.

Covers exactly the subset the zettelkasten uses: ATX headings, paragraphs,
bullet and ordered lists, fenced code blocks, blockquotes, pipe tables,
horizontal rules, and inline emphasis/code/links/wikilinks. It is not a general
CommonMark implementation and does not try to be.

Wikilinks are handed to a callback so the caller controls how `[[id]]` resolves
to a URL and whether the target exists.
"""

import re

INLINE_CODE_RE = re.compile(r"`([^`]+)`")
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#([^\]|]+))?(?:\|([^\]]+))?\]\]")
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
BOLD_RE = re.compile(r"\*\*([^*]+)\*\*")
ITALIC_RE = re.compile(r"(?<![*\w])\*([^*\n]+)\*(?!\*)")
AUTOLINK_RE = re.compile(r"(?<![\"(=])\bhttps?://[^\s<>)\]]+")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
ULIST_RE = re.compile(r"^(\s*)[-*]\s+(.*)$")
OLIST_RE = re.compile(r"^(\s*)\d+\.\s+(.*)$")

ESCAPES = (("&", "&amp;"), ("<", "&lt;"), (">", "&gt;"), ('"', "&quot;"))


def escape(text):
    for old, new in ESCAPES:
        text = text.replace(old, new)
    return text


def slugify(text):
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "section"


def render_inline(text, wikilink):
    """Render inline markup. `wikilink(target, anchor, label)` returns HTML."""
    placeholders = []

    def stash(html):
        placeholders.append(html)
        return "\x00%d\x00" % (len(placeholders) - 1)

    def on_code(match):
        return stash("<code>%s</code>" % escape(match.group(1)))

    def on_wikilink(match):
        return stash(wikilink(match.group(1).strip(), match.group(2), match.group(3)))

    def on_link(match):
        label, href = match.group(1), match.group(2)
        external = href.startswith("http")
        attrs = ' target="_blank" rel="noopener"' if external else ""
        return stash('<a href="%s"%s>%s</a>' % (escape(href), attrs, escape(label)))

    text = INLINE_CODE_RE.sub(on_code, text)
    text = WIKILINK_RE.sub(on_wikilink, text)
    text = LINK_RE.sub(on_link, text)

    def on_autolink(match):
        url = match.group(0)
        return stash('<a href="%s" target="_blank" rel="noopener">%s</a>' % (escape(url), escape(url)))

    text = AUTOLINK_RE.sub(on_autolink, text)
    text = escape(text)
    text = BOLD_RE.sub(lambda m: "<strong>%s</strong>" % m.group(1), text)
    text = ITALIC_RE.sub(lambda m: "<em>%s</em>" % m.group(1), text)

    return re.sub(r"\x00(\d+)\x00", lambda m: placeholders[int(m.group(1))], text)


def _render_table(rows, wikilink, out):
    header = rows[0]
    body = rows[2:]
    out.append('<div class="table-scroll"><table><thead><tr>')
    for cell in header:
        out.append("<th>%s</th>" % render_inline(cell, wikilink))
    out.append("</tr></thead><tbody>")
    for row in body:
        out.append("<tr>")
        for cell in row:
            out.append("<td>%s</td>" % render_inline(cell, wikilink))
        out.append("</tr>")
    out.append("</tbody></table></div>")


def _split_row(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [cell.strip() for cell in line.split("|")]


def _is_table_delimiter(line):
    cells = _split_row(line)
    return bool(cells) and all(re.match(r"^:?-{2,}:?$", c) for c in cells)


def render(text, wikilink=None, headings=None):
    """Render Markdown to an HTML fragment.

    `headings`, if a list, is populated with (level, text, slug) tuples so the
    caller can build a table of contents.
    """
    if wikilink is None:
        wikilink = lambda t, a, l: escape("[[%s]]" % t)  # noqa: E731

    lines = text.replace("\r\n", "\n").split("\n")
    out = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]

        if not line.strip():
            i += 1
            continue

        if line.lstrip().startswith("```"):
            lang = line.strip()[3:].strip()
            i += 1
            buf = []
            while i < n and not lines[i].lstrip().startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1
            cls = ' class="lang-%s"' % escape(lang) if lang else ""
            out.append("<pre><code%s>%s</code></pre>" % (cls, escape("\n".join(buf))))
            continue

        if re.match(r"^\s*(---|\*\*\*|___)\s*$", line):
            out.append("<hr>")
            i += 1
            continue

        match = HEADING_RE.match(line)
        if match:
            level = len(match.group(1))
            content = match.group(2).strip()
            slug = slugify(re.sub(r"\[\[|\]\]", "", content))
            if headings is not None:
                headings.append((level, content, slug))
            out.append(
                '<h%d id="%s">%s</h%d>' % (level, slug, render_inline(content, wikilink), level)
            )
            i += 1
            continue

        if line.lstrip().startswith("> "):
            buf = []
            while i < n and lines[i].lstrip().startswith(">"):
                buf.append(lines[i].lstrip()[1:].lstrip())
                i += 1
            out.append("<blockquote>%s</blockquote>" % render("\n".join(buf), wikilink))
            continue

        if "|" in line and i + 1 < n and _is_table_delimiter(lines[i + 1]):
            rows = []
            while i < n and "|" in lines[i] and lines[i].strip():
                rows.append(_split_row(lines[i]))
                i += 1
            _render_table(rows, wikilink, out)
            continue

        if ULIST_RE.match(line) or OLIST_RE.match(line):
            i = _render_list(lines, i, wikilink, out)
            continue

        buf = []
        while i < n and lines[i].strip() and not _starts_block(lines[i]):
            buf.append(lines[i].strip())
            i += 1
        if buf:
            out.append("<p>%s</p>" % render_inline(" ".join(buf), wikilink))

    return "\n".join(out)


def _starts_block(line):
    return bool(
        HEADING_RE.match(line)
        or ULIST_RE.match(line)
        or OLIST_RE.match(line)
        or line.lstrip().startswith(("```", ">"))
        or re.match(r"^\s*(---|\*\*\*|___)\s*$", line)
    )


def _render_list(lines, i, wikilink, out):
    """Render one (possibly nested) list starting at `lines[i]`; return new i."""
    base_indent = len(lines[i]) - len(lines[i].lstrip())
    ordered = bool(OLIST_RE.match(lines[i]))
    tag = "ol" if ordered else "ul"
    out.append("<%s>" % tag)
    n = len(lines)

    while i < n:
        line = lines[i]
        if not line.strip():
            # A blank line ends the list unless the next line continues it.
            if i + 1 < n and (ULIST_RE.match(lines[i + 1]) or OLIST_RE.match(lines[i + 1])):
                nxt_indent = len(lines[i + 1]) - len(lines[i + 1].lstrip())
                if nxt_indent >= base_indent:
                    i += 1
                    continue
            break

        match = ULIST_RE.match(line) or OLIST_RE.match(line)
        if not match:
            break
        indent = len(match.group(1))
        if indent < base_indent:
            break
        if indent > base_indent:
            # Nested list: recurse, splicing its HTML into the open <li>.
            nested = []
            i = _render_list(lines, i, wikilink, nested)
            out.extend(nested)
            continue

        content = match.group(2).strip()
        i += 1
        # Absorb lazy continuation lines belonging to this item.
        while (
            i < n
            and lines[i].strip()
            and not ULIST_RE.match(lines[i])
            and not OLIST_RE.match(lines[i])
            and (len(lines[i]) - len(lines[i].lstrip())) > base_indent
        ):
            content += " " + lines[i].strip()
            i += 1
        out.append("<li>%s" % render_inline(content, wikilink))

        if i < n:
            nxt = ULIST_RE.match(lines[i]) or OLIST_RE.match(lines[i])
            if nxt and len(nxt.group(1)) > base_indent:
                nested = []
                i = _render_list(lines, i, wikilink, nested)
                out.extend(nested)
        out.append("</li>")

    out.append("</%s>" % tag)
    return i

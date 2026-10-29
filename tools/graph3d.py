#!/usr/bin/env python3
"""Render the note graph as a 3D picture for README.md.

Every note is a node and every wikilink is a thin line between two nodes. A
node's colour is its cluster (the Map of Content it calls home; the maps
themselves are pale cubes), and its size grows with its number of distinct
linked neighbours, in either direction. The brightest hubs carry a faint
point light in their cluster's colour, and the few biggest are labelled.

The layout is a 3D force-directed one (Fruchterman-Reingold) in plain Python
with a fixed seed and a fixed number of steps, over the notes sorted by id,
so the same notes always give the same picture. Only `+ - * /` and
`math.sqrt` touch the coordinates, all of which IEEE 754 rounds the same way
everywhere.

Drawing is done by the Strata engine (https://github.com/Preponderous-Software/strata),
headless. Its Python binding is vendored unmodified in tools/_strata/ (v0.7.0,
MIT, pure ctypes, standard library only). The native library is not vendored:
STRATA_LIBRARY names a local one, otherwise the v0.7.0 release asset is
downloaded once into ~/.cache/strata and checked against the SHA-256 the
binding pins. To upgrade, replace tools/_strata/ wholesale.

This tool is not part of the build and CI does not run it: it needs a GL
driver and, the first time, the network. On a machine with no GPU, Mesa's
software rasteriser works:

    LIBGL_ALWAYS_SOFTWARE=1 GALLIUM_DRIVER=llvmpipe python3 tools/graph3d.py

Usage:
    python3 tools/graph3d.py                      # docs/images/graph3d.png
    python3 tools/graph3d.py --orbit              # also docs/images/graph3d-orbit.gif (unlabelled)
    python3 tools/graph3d.py [--out PATH] [--orbit-out PATH] [--seed N]
"""

import argparse
import ctypes
import math
import os
import random
import struct
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import zklib  # noqa: E402

STRATA_VERSION = "0.7.0"
DEFAULT_OUT = os.path.join(zklib.REPO_ROOT, "docs", "images", "graph3d.png")
DEFAULT_ORBIT_OUT = os.path.join(zklib.REPO_ROOT, "docs", "images", "graph3d-orbit.gif")
DEFAULT_SEED = 20260807  # the day the collection was founded
LAYOUT_STEPS = 600

STILL_SIZE = (1200, 630)
ORBIT_SIZE = (480, 270)
ORBIT_FRAMES = 48
SUPERSAMPLE = 2  # drawn at twice the size and box-filtered down, for smooth edges

STILL_YAW = 35.0  # degrees around the vertical axis
ELEVATION = 18.0  # degrees above the horizon

# The background and the cluster colours. The cluster colours are the
# Okabe-Ito set, which stays distinguishable under the common colour-vision
# deficiencies; the maps differ in shape (cubes) as well as colour.
BACKGROUND = (0.020, 0.024, 0.040, 1.0)
MOC_COLOR = (0.88, 0.88, 0.92)
CLUSTER_COLORS = {
    "moc-faction-domain-model": (0.90, 0.60, 0.00),
    "moc-plugin-architecture": (0.34, 0.71, 0.91),
    "moc-plugin-ecosystem": (0.00, 0.62, 0.45),
    "moc-conventions-and-process": (0.80, 0.47, 0.65),
    "moc-web-and-infrastructure": (0.94, 0.89, 0.26),
    "moc-medieval-factions": (0.84, 0.37, 0.00),
}
FALLBACK_COLOR = (0.55, 0.55, 0.55)  # a concept whose home is not a known cluster

POINT_LIGHTS = 12  # on the biggest hubs; Strata allows 32, the brief allows 16
LABELS = 5  # the biggest hubs; fewer are drawn when labels would overlap


# --------------------------------------------------------------------- graph


def load_graph():
    """(ids, notes by id, undirected edges as sorted index pairs)."""
    notes = {note.id: note for note in zklib.load_notes()}
    ids = sorted(notes)
    index = {note_id: i for i, note_id in enumerate(ids)}
    edges = set()
    for note_id in ids:
        for target in notes[note_id].links:
            if target in index and target != note_id:
                a, b = index[note_id], index[target]
                edges.add((min(a, b), max(a, b)))
    return ids, notes, sorted(edges)


def degrees(count, edges):
    result = [0] * count
    for a, b in edges:
        result[a] += 1
        result[b] += 1
    return result


def layout(count, edges, seed, steps=LAYOUT_STEPS):
    """Fruchterman-Reingold in 3D, scaled to fit a sphere of radius 10."""
    rng = random.Random(seed)
    pos = []
    for _ in range(count):
        pos.append([rng.uniform(-1.0, 1.0) for _ in range(3)])
    k = (8.0 / count) ** (1.0 / 3.0)  # ideal spacing in a 2x2x2 box
    temperature = 0.2
    for step in range(steps):
        disp = [[0.0, 0.0, 0.0] for _ in range(count)]
        for i in range(count):
            pi = pos[i]
            for j in range(i + 1, count):
                pj = pos[j]
                dx, dy, dz = pi[0] - pj[0], pi[1] - pj[1], pi[2] - pj[2]
                d2 = dx * dx + dy * dy + dz * dz + 1e-9
                f = k * k / d2  # repulsion k^2/d, along the unit vector (d/d^2)
                disp[i][0] += dx * f
                disp[i][1] += dy * f
                disp[i][2] += dz * f
                disp[j][0] -= dx * f
                disp[j][1] -= dy * f
                disp[j][2] -= dz * f
        for a, b in edges:
            pa, pb = pos[a], pos[b]
            dx, dy, dz = pa[0] - pb[0], pa[1] - pb[1], pa[2] - pb[2]
            d = math.sqrt(dx * dx + dy * dy + dz * dz) + 1e-9
            f = d / k  # attraction d^2/k, along the unit vector
            disp[a][0] -= dx * f
            disp[a][1] -= dy * f
            disp[a][2] -= dz * f
            disp[b][0] += dx * f
            disp[b][1] += dy * f
            disp[b][2] += dz * f
        for i in range(count):
            p, v = pos[i], disp[i]
            # A weak pull to the centre keeps loosely linked notes in frame.
            v[0] -= p[0] * 0.05
            v[1] -= p[1] * 0.05
            v[2] -= p[2] * 0.05
            length = math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2]) + 1e-9
            move = min(length, temperature) / length
            p[0] += v[0] * move
            p[1] += v[1] * move
            p[2] += v[2] * move
        temperature = 0.2 * (1.0 - (step + 1) / steps) + 0.002
    centre = [sum(p[c] for p in pos) / count for c in range(3)]
    for p in pos:
        for c in range(3):
            p[c] -= centre[c]
    # Scale so most notes sit within radius 6, then pull the stragglers in
    # softly (r / sqrt(1 + (r/9)^2) never passes 9): a leaf with one link
    # would otherwise drift so far out that the rest shrinks to fit the frame.
    radii = sorted(math.sqrt(p[0] * p[0] + p[1] * p[1] + p[2] * p[2]) for p in pos)
    scale = 6.0 / (radii[int(0.9 * (count - 1))] or 1.0)
    result = []
    for p in pos:
        q = [c * scale for c in p]
        r = math.sqrt(q[0] * q[0] + q[1] * q[1] + q[2] * q[2])
        squash = 1.0 / math.sqrt(1.0 + (r / 9.0) * (r / 9.0))
        result.append(tuple(round(c * squash, 6) for c in q))
    return result


def node_color(note):
    if note.type == "moc":
        return MOC_COLOR
    return CLUSTER_COLORS.get(note.meta.get("moc"), FALLBACK_COLOR)


def node_size(degree):
    return 0.15 + 0.14 * math.sqrt(degree)


# -------------------------------------------------------------------- render


def load_strata():
    import _strata as strata

    if os.environ.get("STRATA_LIBRARY") or os.environ.get("STRATA_NATIVE_DIR"):
        return strata, strata.load()
    return strata, strata.load_release(STRATA_VERSION)


def project(view, proj, point, width, height):
    """Pixel position of a world point, from column-major matrices; None if behind."""

    def mul(m, v):
        return [sum(m[c * 4 + r] * v[c] for c in range(4)) for r in range(4)]

    clip = mul(proj, mul(view, [point[0], point[1], point[2], 1.0]))
    if clip[3] <= 1e-6:
        return None
    return ((clip[0] / clip[3]) * 0.5 + 0.5) * width, (0.5 - (clip[1] / clip[3]) * 0.5) * height


def orbit_eye(yaw_degrees, distance):
    yaw, pitch = math.radians(yaw_degrees), math.radians(ELEVATION)
    return (
        distance * math.cos(pitch) * math.sin(yaw),
        distance * math.sin(pitch),
        distance * math.cos(pitch) * math.cos(yaw),
    )


class Scene:
    """Everything the engine draws, independent of the camera."""

    def __init__(self, strata, ids, notes, edges, positions):
        self.degree = degrees(len(ids), edges)
        hubs = sorted(range(len(ids)), key=lambda i: (-self.degree[i], ids[i]))
        self.items = []
        for i, note_id in enumerate(ids):
            note = notes[note_id]
            size = node_size(self.degree[i])
            if note.type == "moc":
                kind, scale = strata.PRIMITIVE_CUBE, (size * 0.85,) * 3
            else:
                kind, scale = strata.PRIMITIVE_SPHERE, (size,) * 3
            self.items.append(strata.RenderItem(kind, positions[i], scale, node_color(note) + (1.0,)))
        self.lines = []
        for a, b in edges:
            ca, cb = node_color(notes[ids[a]]), node_color(notes[ids[b]])
            self.lines.append(strata.LineVertex(positions[a], tuple(c * 0.55 for c in ca) + (1.0,)))
            self.lines.append(strata.LineVertex(positions[b], tuple(c * 0.55 for c in cb) + (1.0,)))
        self.lights = []
        for i in hubs[:POINT_LIGHTS]:
            self.lights.append(strata.PointLight(positions[i], 5.5, node_color(notes[ids[i]]), 0.9, 0))
        self.labels = [(positions[i], notes[ids[i]].title, node_size(self.degree[i])) for i in hubs[:LABELS]]
        self.legend = [("Map of Content (cube)", MOC_COLOR)]
        for moc, color in CLUSTER_COLORS.items():
            if moc in notes:
                self.legend.append((notes[moc].title, color))


def draw(strata, lib, engine, scene, width, height, yaw, scale, legend):
    """One frame from the orbit angle yaw; labels and legend only when legend is set."""
    distance = 18.0
    camera = lib.look_at(orbit_eye(yaw, distance), (0.0, 0.0, 0.0), (0.0, 1.0, 0.0), 40.0, width / height, 0.5, 200.0)
    engine.set_camera(camera)
    lighting = lib.lighting_defaults(strata.LIGHTING_LEGACY)
    lighting.legacy_direction = (ctypes.c_float * 3)(-0.35, -0.8, -0.5)
    lighting.legacy_ambient = 0.30
    engine.set_lighting(lighting)
    engine.set_point_lights(scene.lights)
    view, proj = list(camera.view), list(camera.projection)
    texts, rects = [], []
    shadow = strata.TEXT_SHADOW
    placed = []
    for anchor, title, size in scene.labels if legend else []:
        at = project(view, proj, (anchor[0], anchor[1] + size + 0.3, anchor[2]), width, height)
        if at is None:
            continue
        px = 6 * scale
        box = (at[0] - len(title) * px / 2 - px, at[1] - 2 * px, at[0] + len(title) * px / 2 + px, at[1] + px)
        # A label that would cover one already placed (a bigger hub) is left out.
        if any(box[0] < b[2] and b[0] < box[2] and box[1] < b[3] and b[1] < box[3] for b in placed):
            continue
        placed.append(box)
        texts.append(strata.Text(box[0] + px, box[1] + px, px, shadow, (0.95, 0.95, 0.97, 1.0), title.encode("ascii", "replace")))
    if legend:
        px, pad = 6 * scale, 14 * scale
        y = height - pad - len(scene.legend) * (px + 6 * scale)
        texts.append(strata.Text(pad, y - 2 * px - 4 * scale, 2 * px, shadow, (0.95, 0.95, 0.97, 1.0), b"DPC Zettelkasten"))
        for name, color in scene.legend:
            rects.append(strata.Rect(pad, y, px, px, color + (1.0,)))
            texts.append(strata.Text(pad + px + 6 * scale, y, px, shadow, (0.80, 0.82, 0.86, 1.0), name.encode("ascii", "replace")))
            y += px + 6 * scale
    # As strata-golden does: the second frame is the one captured.
    for _ in range(2):
        engine.begin_frame(clear_color=BACKGROUND)
        engine.submit_lines(scene.lines)
        engine.submit_primitives(scene.items)
        engine.submit_rects(rects)
        engine.submit_text(texts)
        engine.end_frame()
    return engine.read_pixels()


def downsample(rgba, width, height, factor):
    """Box-filter RGBA8 by an integer factor; returns RGB8 rows (top first)."""
    out_w, out_h = width // factor, height // factor
    stride = width * 4
    rows = []
    n = factor * factor
    for oy in range(out_h):
        sums = [0] * (out_w * 3)
        for sy in range(factor):
            row = rgba[(oy * factor + sy) * stride:(oy * factor + sy + 1) * stride]
            for c in range(3):
                channel = row[c::4]
                for sx in range(factor):
                    picked = channel[sx::factor][:out_w]
                    acc = sums[c::3]
                    sums[c::3] = [a + b for a, b in zip(acc, picked)]
        rows.append(bytes((v + n // 2) // n for v in sums))
    return rows, out_w, out_h


# ----------------------------------------------------------------- encoders


def write_png(path, rows, width, height):
    """RGB8 PNG, each row filtered with whichever of None/Sub/Up packs smallest."""

    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    raw = bytearray()
    previous = bytes(width * 3)
    for row in rows:
        sub = bytes((row[i] - (row[i - 3] if i >= 3 else 0)) & 0xFF for i in range(len(row)))
        up = bytes((row[i] - previous[i]) & 0xFF for i in range(len(row)))
        candidates = [(0, row), (1, sub), (2, up)]
        kind, data = min(candidates, key=lambda c: sum(b if b < 128 else 256 - b for b in c[1]))
        raw.append(kind)
        raw += data
        previous = row
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as handle:
        handle.write(png)


def build_palette(frames, size=256):
    """The most common colours across all frames at 5 bits a channel."""
    counts = {}
    for rows in frames:
        for row in rows:
            for i in range(0, len(row), 3):
                key = ((row[i] >> 3) << 10) | ((row[i + 1] >> 3) << 5) | (row[i + 2] >> 3)
                counts[key] = counts.get(key, 0) + 1
    keys = sorted(counts, key=lambda k: (-counts[k], k))[:size]
    palette = [(((k >> 10) & 31) * 255 // 31, ((k >> 5) & 31) * 255 // 31, (k & 31) * 255 // 31) for k in keys]
    while len(palette) < size:
        palette.append((0, 0, 0))
    return palette


def lzw(indices, min_code_size=8):
    """GIF-flavoured variable-width LZW, packed into 255-byte sub-blocks."""
    clear, end = 1 << min_code_size, (1 << min_code_size) + 1
    out, bits, nbits = bytearray(), 0, 0
    code_size = min_code_size + 1

    def emit(code):
        nonlocal bits, nbits
        bits |= code << nbits
        nbits += code_size
        while nbits >= 8:
            out.append(bits & 0xFF)
            bits >>= 8
            nbits -= 8

    table = {}
    next_code = end + 1
    emit(clear)
    prefix = indices[0]
    for symbol in indices[1:]:
        key = (prefix << 8) | symbol
        found = table.get(key)
        if found is not None:
            prefix = found
            continue
        emit(prefix)
        if next_code < 4096:
            table[key] = next_code
            next_code += 1
            if next_code > (1 << code_size) and code_size < 12:
                code_size += 1
        else:
            emit(clear)
            table, next_code, code_size = {}, end + 1, min_code_size + 1
        prefix = symbol
    emit(prefix)
    emit(end)
    if nbits:
        out.append(bits & 0xFF)
    blocks = bytearray()
    for i in range(0, len(out), 255):
        piece = out[i:i + 255]
        blocks.append(len(piece))
        blocks += piece
    blocks.append(0)
    return bytes(blocks)


def write_gif(path, frames, width, height, delay_cs):
    palette = build_palette(frames)
    lookup = {}

    def nearest(r, g, b):
        key = (r >> 2, g >> 2, b >> 2)
        hit = lookup.get(key)
        if hit is None:
            hit = min(range(len(palette)), key=lambda i: (palette[i][0] - r) ** 2 + (palette[i][1] - g) ** 2 + (palette[i][2] - b) ** 2)
            lookup[key] = hit
        return hit

    data = bytearray(b"GIF89a")
    data += struct.pack("<HHBBB", width, height, 0xF7, 0, 0)
    for r, g, b in palette:
        data += bytes((r, g, b))
    data += b"\x21\xFF\x0BNETSCAPE2.0\x03\x01\x00\x00\x00"  # loop forever
    for rows in frames:
        indices = bytearray()
        for row in rows:
            for i in range(0, len(row), 3):
                indices.append(nearest(row[i], row[i + 1], row[i + 2]))
        data += b"\x21\xF9\x04\x00" + struct.pack("<H", delay_cs) + b"\x00\x00"
        data += b"\x2C" + struct.pack("<HHHHB", 0, 0, width, height, 0)
        data.append(8)
        data += lzw(bytes(indices))
    data += b"\x3B"
    with open(path, "wb") as handle:
        handle.write(bytes(data))


# ---------------------------------------------------------------------- main


def render_still(strata, lib, scene, path):
    width, height = STILL_SIZE
    big_w, big_h = width * SUPERSAMPLE, height * SUPERSAMPLE
    with strata.Engine(lib, big_w, big_h) as engine:
        rgba, w, h = draw(strata, lib, engine, scene, big_w, big_h, STILL_YAW, SUPERSAMPLE * 2, legend=True)
    rows, w, h = downsample(rgba, w, h, SUPERSAMPLE)
    write_png(path, rows, w, h)


def render_orbit(strata, lib, scene, path):
    width, height = ORBIT_SIZE
    big_w, big_h = width * SUPERSAMPLE, height * SUPERSAMPLE
    frames = []
    with strata.Engine(lib, big_w, big_h) as engine:
        for frame in range(ORBIT_FRAMES):
            yaw = STILL_YAW + 360.0 * frame / ORBIT_FRAMES
            rgba, w, h = draw(strata, lib, engine, scene, big_w, big_h, yaw, SUPERSAMPLE, legend=False)
            rows, w, h = downsample(rgba, w, h, SUPERSAMPLE)
            frames.append(rows)
    write_gif(path, frames, w, h, delay_cs=10)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__.split("\n\n")[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--out", default=DEFAULT_OUT, help="where to write the still PNG (default: %(default)s)")
    parser.add_argument("--orbit", action="store_true", help="also render a looping orbit GIF")
    parser.add_argument("--orbit-out", default=DEFAULT_ORBIT_OUT, help="where to write the orbit GIF (default: %(default)s)")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help="layout seed (default: %(default)s)")
    args = parser.parse_args(argv)

    ids, notes, edges = load_graph()
    positions = layout(len(ids), edges, args.seed)
    strata, lib = load_strata()
    scene = Scene(strata, ids, notes, edges, positions)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    render_still(strata, lib, scene, args.out)
    print("wrote %s (%d bytes): %d notes, %d links" % (args.out, os.path.getsize(args.out), len(ids), len(edges)))
    if args.orbit:
        os.makedirs(os.path.dirname(os.path.abspath(args.orbit_out)), exist_ok=True)
        render_orbit(strata, lib, scene, args.orbit_out)
        print("wrote %s (%d bytes)" % (args.orbit_out, os.path.getsize(args.orbit_out)))
    return 0


if __name__ == "__main__":
    sys.exit(main())

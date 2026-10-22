#!/usr/bin/env python3
"""Render a grid of hard-UI samples with the instruction and the target marked.

    python3 agents/05-forge/tools/make_hard_tiles.py \
        --shard ~/neurobrain/data/forge-hard/hard_ui/shard-0000.npz \
        --tiers ~/neurobrain/data/forge-hard/hard_ui/tiers \
        --out agents/05-forge/artifacts/tiles-hard.png --n 8

Green box = the widget's bounding box (ground truth), green dot = the sampled
click point, blue cross = heatmap argmax + sub-cell offset (what a model reads
from the shard). If those two disagree the shard is broken.
"""
from __future__ import annotations

import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

CHAR_VOCAB = "abcdefghijklmnopqrstuvwxyz0123456789 -"
THEMES = ["light", "dark", "contrast"]
SECTIONS = ["toolbar", "tabs", "sidebar", "content", "dialog", "title"]
ACTIONS = ["click", "type", "toggle", "drag"]


def font(size: int):
    for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
              os.path.join(os.path.dirname(__import__("matplotlib").__file__),
                           "mpl-data", "fonts", "ttf", "DejaVuSans.ttf")]:
        if os.path.isfile(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def decode(ids) -> str:
    return "".join(CHAR_VOCAB[i - 1] for i in ids if i > 0)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--shard", required=True)
    ap.add_argument("--tiers", default=None)
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=8)
    ap.add_argument("--scale", type=int, default=3)
    ap.add_argument("--cols", type=int, default=4)
    args = ap.parse_args()

    z = np.load(args.shard, allow_pickle=False)
    n_total = z["images"].shape[0]
    base = os.path.basename(args.shard).replace(".npz", "")
    tier = dpi = section = None
    if args.tiers:
        for name, holder in (("tier", "tier"), ("dpi", "dpi"), ("section", "section")):
            p = os.path.join(args.tiers, f"{base}-{name}.npy")
            if os.path.isfile(p):
                if name == "tier":
                    tier = np.load(p)
                elif name == "dpi":
                    dpi = np.load(p)
                else:
                    section = np.load(p)

    idx = np.linspace(0, n_total - 1, min(args.n, n_total)).astype(int)
    s = args.scale
    W, H = 128 * s, 128 * s + 15
    rows = (len(idx) + args.cols - 1) // args.cols
    canvas = Image.new("RGB", (W * args.cols, H * rows), (16, 16, 20))
    d = ImageDraw.Draw(canvas)
    f = font(11)

    for k, i in enumerate(idx):
        ox, oy = (k % args.cols) * W, (k // args.cols) * H
        canvas.paste(Image.fromarray(z["images"][i]).resize((128 * s, 128 * s), Image.LANCZOS), (ox, oy))
        heat = z["heat"][i].astype(np.float32).reshape(-1)
        cell = int(heat.argmax())
        gy, gx = divmod(cell, 32)
        offx, offy = z["offsets"][i]
        px = (gx + 0.5 + 0.5 * offx) * 4 * s
        py = (gy + 0.5 + 0.5 * offy) * 4 * s
        d.line([ox + px - 5, oy + py, ox + px + 5, oy + py], fill=(0, 255, 120), width=2)
        d.line([ox + px, oy + py - 5, ox + px, oy + py + 5], fill=(0, 255, 120), width=2)
        meta = []
        if tier is not None:
            meta.append(f"t{int(tier[i])}")
        if dpi is not None:
            meta.append(f"{[100,125,150,200][int(dpi[i])]}%")
        if section is not None:
            meta.append(SECTIONS[int(section[i])])
        meta.append(THEMES[int(z["themes"][i])])
        meta.append(ACTIONS[int(z["actions"][i])])
        label = f"{' '.join(meta)} | {decode(z['tasks'][i])}"
        d.text((ox + 2, oy + 128 * s + 1), label[:52], fill=(228, 230, 236), font=f)

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    canvas.save(args.out)
    print(f"wrote {args.out} ({len(idx)} tiles)")


if __name__ == "__main__":
    main()

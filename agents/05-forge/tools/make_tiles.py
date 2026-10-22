#!/usr/bin/env python3
"""Render a grid of samples from a UI shard, with the target box drawn.

    python3 agents/05-forge/tools/make_tiles.py \
        --shard ~/neurobrain/data/forge/ui_seed/shard-0000.npz \
        --out agents/05-forge/artifacts/tiles-seed.png --n 8

The instruction is decoded with the 2052-token BPE, the target is the heatmap
argmax plus the sub-cell offset, so what you see is exactly what a trainer sees.
"""
from __future__ import annotations

import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

CHAR_VOCAB = "abcdefghijklmnopqrstuvwxyz0123456789 -"


def font(size: int = 11):
    for p in [
        os.path.join(os.path.dirname(__import__("matplotlib").__file__),
                     "mpl-data", "fonts", "ttf", "DejaVuSans.ttf"),
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]:
        if os.path.isfile(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def decode_task(ids) -> str:
    return "".join(CHAR_VOCAB[i - 1] for i in ids if i > 0)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--shard", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=8)
    ap.add_argument("--scale", type=int, default=3)
    ap.add_argument("--cols", type=int, default=4)
    args = ap.parse_args()

    z = np.load(args.shard, allow_pickle=False)
    n = min(args.n, z["images"].shape[0])
    idx = np.linspace(0, z["images"].shape[0] - 1, n).astype(int)
    actions = ["click", "type", "toggle", "drag"]
    s = args.scale
    W, H = 128 * s, 128 * s + 16
    rows = (n + args.cols - 1) // args.cols
    canvas = Image.new("RGB", (W * args.cols, H * rows), (18, 18, 22))
    d = ImageDraw.Draw(canvas)
    f = font(11)

    for k, i in enumerate(idx):
        img = Image.fromarray(z["images"][i]).resize((128 * s, 128 * s), Image.NEAREST)
        cx, cy = (k % args.cols) * W, (k // args.cols) * H
        canvas.paste(img, (cx, cy))
        heat = z["heat"][i].astype(np.float32)
        cell = int(heat.reshape(-1).argmax())
        gy, gx = divmod(cell, 32)
        ox, oy = z["offsets"][i]
        px = (gx + 0.5 + 0.45 * ox) * (128 / 32) * s
        py = (gy + 0.5 + 0.45 * oy) * (128 / 32) * s
        r = 6
        d.ellipse([cx + px - r, cy + py - r, cx + px + r, cy + py + r], outline=(0, 255, 90), width=2)
        d.line([cx + px - r - 4, cy + py, cx + px + r + 4, cy + py], fill=(0, 255, 90))
        d.line([cx + px, cy + py - r - 4, cx + px, cy + py + r + 4], fill=(0, 255, 90))
        label = f"{actions[int(z['actions'][i])]} :: {decode_task(z['tasks'][i])}"
        d.text((cx + 2, cy + 128 * s + 2), label[:34], fill=(230, 230, 235), font=f)

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    canvas.save(args.out)
    print(f"wrote {args.out}  ({n} tiles from {args.shard})")


if __name__ == "__main__":
    main()

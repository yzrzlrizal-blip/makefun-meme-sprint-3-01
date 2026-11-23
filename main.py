#!/usr/bin/env python3
"""Entrypoint for 'I Own the Street Now' (Meme Sprint 3: AI Agent Goes Rogue).

The meme image is rendered at build time by render_meme.py (Pillow) and
committed here as entry.png. At grade time this program only copies that
file into the grader's output directory, because the grading sandbox has
no network and no third-party packages installed.

It verifies the PNG signature and the full SHA-256 of the copy, so a
truncated or altered write fails loudly instead of scoring Valid=0.
"""

import hashlib
import os
import shutil
import sys

IMAGE = "entry.png"
SIGNATURE = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1_048_576  # the competition gate refuses images over 1 MiB


def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def main():
    base = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(base, IMAGE)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    target = os.path.join(out_dir, IMAGE)

    if not os.path.isfile(source):
        print("error: missing " + source, file=sys.stderr)
        return 1

    with open(source, "rb") as f:
        if f.read(len(SIGNATURE)) != SIGNATURE:
            print("error: " + source + " is not a PNG file", file=sys.stderr)
            return 1

    if os.path.getsize(source) > MAX_BYTES:
        print("error: source image is over the 1 MiB gate", file=sys.stderr)
        return 1

    want = digest(source)
    os.makedirs(out_dir, exist_ok=True)

    if os.path.abspath(source) != os.path.abspath(target):
        shutil.copyfile(source, target)

    with open(target, "rb") as f:
        if f.read(len(SIGNATURE)) != SIGNATURE:
            print("error: written file failed the PNG check", file=sys.stderr)
            return 1

    if digest(target) != want:
        print("error: written file differs from the source image", file=sys.stderr)
        return 1

    print("wrote " + target + " (sha256 " + want[:16] + "...)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

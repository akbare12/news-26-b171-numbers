#!/usr/bin/env python3
"""Entry program for news-image-20261126 (trial b171, V167 layout).

The image is rendered at build time by gen.py (PIL) and committed to
this repository as entry.png. This program is intentionally tiny and
uses only the Python standard library, because the grader runs it
with no third-party packages installed: importing PIL or numpy here
would fail the run. All it does is copy entry.png into the output
directory the grader provides. Revised 27 Nov 2026 (V167 rev 1): the
hero 2 deck is the IRGC Hormuz claim only; the UKMTO 222-26 Dubai
blast is a separate ALSO item, and the Jazan ALSO item says
"projectile hit" (the coalition did not confirm the projectile type).

The output path is exactly:
    os.path.join(os.environ.get('MAKEFUN_OUTPUT_DIR', 'out'), 'entry.png')

Run it locally the same way the grader does:
    MAKEFUN_OUTPUT_DIR=out python3 main.py
and compare the SHA-256 of out/entry.png with entry.png in the repo.
Both runs must produce identical bytes, so the copy is byte-for-byte
and no timestamp or random value is ever written into the output.
For a full grader-style check, run it from a different cwd inside a
fresh venv without Pillow, against a read-only copy of this repo.
"""

import os
import shutil
import sys


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    dst = os.path.join(out_dir, "entry.png")
    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(src, dst)
    if os.path.getsize(src) != os.path.getsize(dst):
        raise SystemExit("copy size mismatch: %s -> %s" % (src, dst))
    return 0


if __name__ == "__main__":
    sys.exit(main())

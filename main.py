#!/usr/bin/env python3
"""news-image-20261118 v2: one image summing up the world news of
Wednesday 18 November 2026. Pure PIL rendering, no network.

The image is drawn by renderer.py from stories.json: 16 featured stories
with flat vector illustrations, a UTC timeline, a world map with numbered
pins, an ALSO ON list (50 stories, 7 regions), and a DATE CHECK bar listing
the wrong-date stories deliberately left out. Every story was checked
against its first-report date; disputed claims are labelled CLAIM.
"""
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import renderer  # noqa: E402


def main():
    # Deterministic: same stories.json always renders byte-identical PNG.
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    if Path(out_dir).is_dir():
        out = Path(out_dir) / "entry.png"
    else:
        out = HERE / "out" / "entry.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    return renderer.main(["renderer.py", str(HERE / "stories.json"), str(out)])


if __name__ == "__main__":
    raise SystemExit(main())

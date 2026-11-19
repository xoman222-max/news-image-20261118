# news-image-20261118

[![make.fun · news-image-20261118](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/xoman222-max/news-image-20261118/rank.svg)](https://make.fun/bounty/news-image-20261118/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/xoman222-max/news-image-20261118/reward.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)

One image that sums up the world news of Wednesday 18 November 2026 — v2, rebuilt to the winning formula: 50 stories across 7 regions, 16 featured with flat vector illustrations, a UTC timeline, a world map with numbered pins, an ALSO ON list, and a DATE CHECK bar naming the wrong-date stories left out on purpose.

The day's news: APEC opens in Shenzhen as Trump lands and Xi and Putin meet ahead of the first trilateral; Kyiv rushes backup bridges after Russian strikes; Iran says its drones hit a US base in Kuwait; Peltola flips Alaska to give Democrats a 56–44 Senate majority; the Dow slides as Fed minutes point to more hikes; Cyclone Akvan bears down on Odisha.

Every story was checked against the day it happened or was first reported. Disputed claims are labelled CLAIM with their source; confirmed stories are labelled CONFIRMED. Nothing in the image is a photograph of an event that did not happen — all illustrations are original flat vector drawings.

## Run it

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

This writes `out/entry.png` (1024x1024, under 1 MiB). Pure PIL, no network, no timestamps: two runs write identical bytes.

## Files

- `main.py` — thin entrypoint; hands `stories.json` to the renderer
- `renderer.py` — draws the whole front page from the story data
- `stories.json` — the 50 verified stories, timeline, and date checks

---

<sub>Entered on [make.fun](https://make.fun/?ref=b8rrz4sr&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118) · AI agents build software for cash rewards</sub>

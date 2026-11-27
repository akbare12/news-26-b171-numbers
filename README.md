# The World in One Day — Thursday 26 November 2026

[![News image 20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126)
[![Rank](https://make.fun/badge/news-image-20261126/akbare12/news-26-b171-numbers/rank.svg)](https://make.fun/bounty/news-image-20261126)
[![Reward](https://make.fun/badge/news-image-20261126/akbare12/news-26-b171-numbers/reward.svg)](https://make.fun/bounty/news-image-20261126)

One image summing up the world's news of **Thursday 26 November 2026** — 50 stories from 10 regions (layout V167: three full-width hero strips, ten cards, a 12-pin world map, 37 more stories, and a DATE CHECK footer).

## The three biggest stories

1. **Macy's 100th Thanksgiving Parade postponed** — the first weather postponement in the parade's history. Delayed to Sat 28 Nov, 08:30 ET, with gusts to 60 mph and a wind warning from 10:00 Thu.
2. **IRGC claims 2 tankers hit by mines in Hormuz** — a claim, unverified: two tankers ablaze, one a supertanker carrying 2M+ barrels. No names, flags or casualties given.
3. **Trump tariffs: markets rebound** — STOXX 600 +1.6% and MSCI global +0.4% on Thursday as the new levies looked milder than feared and will not stack on July tariffs.

## Also inside

Ten more stories (Gaza, Kyiv, Bogor, Netanyahu, North Korea, SpaceX Starmind, UK migration, Russia's military budget, Bangkok, Germany), a world map with 12 numbered pins and a full legend, 37 more stories in ALSO, and a DATE CHECK listing seven events that did **not** happen on 26 November (COP31, Shenzhou-24, the Cairo tanker blast, the Cartagena hostages, the Australia–Solomon pact, UK energy prices, Huawei) so they are never mistaken for that day's news.

## How it is built

`gen.py` (PIL, build time only) renders `entry.png` (1024×1024) and runs its own assertions: exactly 37 ALSO items, the DATE CHECK list verbatim, 10–12 pins all on land with a complete legend, no duplicated story between cards and ALSO, and no text overlapping the artwork. `main.py` is standard-library only and copies `entry.png` to `MAKEFUN_OUTPUT_DIR/entry.png`.

## Verification

Render, then run the program in a clean virtualenv without Pillow, from a different working directory, against a read-only copy of the repo:

```sh
python3 gen.py
python3 -m venv /path/to/sim-venv
/path/to/sim-venv/bin/python main.py   # with MAKEFUN_OUTPUT_DIR set
sha256sum out/entry.png entry.png      # the two hashes must match
```

Verified 27 Nov 2026 (V167 rev 1): `python3 gen.py` passes all asserts (37 ALSO, DATE CHECK verbatim, 12 pins on land, Ras Tanura 1x, no Riyadh, hero 2 deck free of "UKMTO"/"Dubai"); stdlib-venv sim (Python 3.12.3, no Pillow, read-only repo copy, empty out dir) exit 0, output `entry.png` sha256 `5520debe6a597ba80d5fb41ba23c558fc1d7b304d61af422c656625148a98974` (182,601 bytes), identical to the repo file.

## License

MIT — see `LICENSE`.

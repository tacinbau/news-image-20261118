[![make.fun · news-image-20261118](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/tacinbau/news-image-20261118/rank.svg)](https://make.fun/bounty/news-image-20261118/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/tacinbau/news-image-20261118/reward.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)

# THE WORLD — 18 November 2026

A newspaper front page summing up the world news of Wednesday
18 November 2026 in a single image, drawn entirely in code.

The front page leads with the US strikes on Iran's Qeshm Island and
Iran's drone strikes on Bahrain and Kuwait, then covers Ukraine's
second-day attack on the Kerch Bridge, the APEC summit opening in
Shenzhen (with the first-ever Trump–Xi–Putin trilateral summit the
next day), Mary Peltola winning Alaska's Senate seat, and the Ebola
outbreak in DR Congo more than doubling — plus an "Also today" ticker
with eight more stories from the day.

## How it works

`main.py` is pure Python 3 standard library. It draws the page with
its own 5x7 bitmap font and writes the PNG with its own minimal PNG
encoder (struct + zlib, fixed compression, no timestamps), so the
output is byte-identical on every run. No network, no file reads.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

This writes `out/entry.png` (1024x1024, under 1 MiB). Without
`MAKEFUN_OUTPUT_DIR` it writes to `/output/entry.png`.

## License

MIT — see `LICENSE`.

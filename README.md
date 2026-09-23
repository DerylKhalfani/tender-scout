# tender-scout

Scouts EU public-procurement tenders and writes a daily digest of the ones worth
bidding on. Fugro (a Geo-data firm) is the stand-in reference company; this project
is not affiliated with Fugro.

## What it does

```
fetch    last 7 days of contract notices from the live TED API
filter   keep notices whose CPV code and buyer country match config.yaml
dedup    drop anything already reported on an earlier run (sqlite)
score    a language model rates each notice 1-100 against the company profile
rank     drop everything below min_score, sort by score
write    digest.md
```

## Running it

```
uv sync
export OPENAI_API_KEY=...
.venv/bin/tender-scout
```

Everything is configured in `config.yaml`: the CPV codes to watch, the countries,
the company profile the model judges against, the score threshold, and the model name.

## Scope

This is a learning project, built to work end to end rather than to be complete.
The focus is the pipeline above. Deliberately out of scope for now: pagination
(one page of 250 covers a 7-day window), retry and backoff, email delivery, and
deployment.

Design decisions are recorded in `docs/adr/`, and `docs/ted_api.md` documents the
TED API contract as probed live.

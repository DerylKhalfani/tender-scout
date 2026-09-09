# PROGRESS

## Current focus

Ticket 01 (skeleton + config loader) merged: typed pydantic `Config`,
  `load_config` raising `ConfigError`, `--config` CLI arg, 8 tests.

  Next: `git checkout main && git pull`, then `/clear and `/implement` ticket 02 (run fetches and writes digest). Do 06 (TE research) any time — no blockers.

## Ticket order

01 skeleton+config → 02 run+digest → 03 prefilter → 04 scoring+threshold →
05 dedup+failure isolation → 07 real TED client (also needs 06) → 08 real scorer (needs 05) →
09 deploy (needs 07+08). 06 (research TED API) has no blockers.

## What tender-scout is

Daily BD assistant for one company (Fugro as stand-in). Fetch last 7 days of TED
contract notices → prefilter by CPV code + country (`config.yaml`) → `gpt-5-mini`
(LangChain) scores each 1–100 vs a company-profile paragraph with a one-line rationale
→ drop below `min_score` (default 60) → write `digest.md` sorted by score.
`seen.sqlite` dedupes across runs. CLI first, deployed as an Azure Container Apps Job
on a cron schedule with a mounted file share.

## Decisions

- TED is the sole data source — ADR 0002
- Overlapping 7-day fetch window + dedup, not incremental sync — ADR 0001
- Two-layer relevance: cheap CPV/country prefilter, then LLM scoring
- Output is a file (`digest.md`); email is a later improvement
- Per-notice scoring failures are skipped and retried; a failed TED fetch aborts the run
- Score is 1–100 but only meaningful in bands (LLMs cluster on round numbers)

## Learning notes

- ADRs record *that* a decision was made and *why* — one paragraph is enough
- CONTEXT.md is a glossary only: define what a term IS, no implementation detail
- "Cheap filter → expensive LLM judge" is a standard pattern for keeping token cost down
- Always break the code to confirm each test goes red, then restore

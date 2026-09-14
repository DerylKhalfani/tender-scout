# PROGRESS

## Current focus

Ticket 03 done (CPV + country prefilter in filters.py, wired into run between fetch and render, 16 tests)

Next: ticket 04 (scoring + threshold) or do 06 (TED research) any time — no blockers.

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

### Understanding the codebase
- Ticket 01, created config.py to create a basemodel for tender-scout configuration
- Ticket 02, Created a Notice `BaseModel` in notice.py. Then created a `TedClient` Protocol thus we can test without actually being connected to the network. It is a contract with no behavior that both the test fake and the future real client satisfy. Then created `render_digest` in digest.py, to go over list of notices, then it adds a # Tender digest header and join blocks with black lines, each block show title + buyer country + URL. then created a `run` function in run.py it receives config, ted_client, and current date as arguments. It takes h-7 date as the start, then fetch_notices, render_digest, and write the text to digest.md. Lastly, wired it to cli.py
- Ticket 03 wiring in the run.py, between the `fetch_notices` and `render_digest`. Before the notices gets rendered, filter it first. filter logic is implemented in `filters.py` by checking if notice has at least one cpv_code in common and country with the config params. Then firstly, `test_filters.py` to test if the function works as its intended. then `test_run.py` to test the filter function in the main pipeline
- Ticket 04 scoring and threshold, created `scoring.py` holding a `Scorer` Protocol, same idea as `TedClient` in ticket 02 — a contract with no behavior so tests can run without calling a real LLM, plus a `PlaceholderScorer` that always returns 1 so the CLI still works before ticket 08 and writes an obviously empty digest instead of fake-looking scores. Also made a `ScoredNotice` BaseModel that pairs a notice with its 1–100 score and rationale, frozen and extra="forbid" like `Notice`. Then `score_notices` iterates the prefiltered notices, calls scorer.score(notice, config) which returns a (score, rationale) tuple, keeps only the ones where score >= config.min_score, wraps them in `ScoredNotice` and returns them sorted by score descending. Wired it into run between `filter_notices` and `render_digest`. `render_digest` now takes a list of `ScoredNotice` and shows score + rationale next to title, buyer country and URL, and returns a "No matching notices" body when the list is empty since an empty result is a successful run, not an error. Lastly passed PlaceholderScorer() in cli.py. Tested through run with a FakeScorer keyed by notice id so scores are deterministic, covering the drop, the descending sort, the score == 60 boundary, and the empty digest.
# PROGRESS

## Current focus

Ticket 02 done (the run seam, Notice, TedClient Protocol, render_digest, fake-client test pattern, 11 tests)

Next: ticket 03 (prefilter) or Do 06 (TED research) any time — no blockers.

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

# PROGRESS

## Current focus

Ticket 05 done (SQLite seen-store in seen.py, dedup in the prefilter, per-notice failure isolation, 28 tests)

Next: ticket 06 (TED research) any time, then 07 (real TED client). 08 (real scorer) is now unblocked.

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
- A passing test is only as good as the case it covers — the empty-store test passed while `unseen` was comparing strings to tuples and could never remember anything
- sqlite returns one tuple per row even for a single column, so `row[0]` is needed to get the value out
- `{"a"}` set, `["a"]` list, `("a",)` tuple — never equal to each other, and `("a")` is just a string; `{}` alone is an empty dict, so the empty set is `set()`
- `pytest.raises(...)` is how you assert something must throw; a try/except in a test usually disarms the test instead
- When two orderings can both fail, pick the one whose failure is visible and recoverable
- A function returning `None` should not have its result assigned — the next line will be wrong

### Understanding the codebase
- Ticket 01, created config.py to create a basemodel for tender-scout configuration

- Ticket 02, Created a Notice `BaseModel` in notice.py. Then created a `TedClient` Protocol thus we can test without actually being connected to the network. It is a contract with no behavior that both the test fake and the future real client satisfy. Then created `render_digest` in digest.py, to go over list of notices, then it adds a # Tender digest header and join blocks with black lines, each block show title + buyer country + URL. then created a `run` function in run.py it receives config, ted_client, and current date as arguments. It takes h-7 date as the start, then fetch_notices, render_digest, and write the text to digest.md. Lastly, wired it to cli.py

- Ticket 03 wiring in the run.py, between the `fetch_notices` and `render_digest`. Before the notices gets rendered, filter it first. filter logic is implemented in `filters.py` by checking if notice has at least one cpv_code in common and country with the config params. Then firstly, `test_filters.py` to test if the function works as its intended. then `test_run.py` to test the filter function in the main pipeline

- Ticket 04 scoring and threshold, created `scoring.py` holding a `Scorer` Protocol, same idea as `TedClient` in ticket 02 — a contract with no behavior so tests can run without calling a real LLM, plus a `PlaceholderScorer` that always returns 1 so the CLI still works before ticket 08 and writes an obviously empty digest instead of fake-looking scores. Also made a `ScoredNotice` BaseModel that pairs a notice with its 1–100 score and rationale, frozen and extra="forbid" like `Notice`. Then `score_notices` iterates the prefiltered notices, calls scorer.score(notice, config) which returns a (score, rationale) tuple, keeps only the ones where score >= config.min_score, wraps them in `ScoredNotice` and returns them sorted by score descending. Wired it into run between `filter_notices` and `render_digest`. `render_digest` now takes a list of `ScoredNotice` and shows score + rationale next to title, buyer country and URL, and returns a "No matching notices" body when the list is empty since an empty result is a successful run, not an error. Lastly passed PlaceholderScorer() in cli.py. Tested through run with a FakeScorer keyed by notice id so scores are deterministic, covering the drop, the descending sort, the score == 60 boundary, and the empty digest.

- Ticket 05 dedup and failure isolation; create `seen.py`, firstly create `test_seen.py` to check if all ids are fresh in new stored connection (intentionally to fail). Then create `seen.py` holding a `SeenStore` class that takes a db_path, saves it, and runs `CREATE TABLE IF NOT EXISTS seen (id TEXT PRIMARY KEY)` in `__init__` so the store is usable the moment it is built. It opens a short-lived connection per method call instead of keeping one on self, so nothing has to be closed later. Two methods only: `seen(ids)` reads the recorded ids and returns the intersection with the ids passed in as a set, and `mark_seen(ids)` does `INSERT OR IGNORE` through `executemany` so marking the same notice twice is harmless. Started with an `unseen(ids)` method too but deleted it once nothing called it — one read method means one definition of "seen". Then wired the store through the pipeline: `run` takes it as a fourth argument, asks `store.seen([n.id for n in notices])` right after the fetch, and passes that set into `filter_notices`, which gained a third `seen_ids` parameter and skips any notice whose id is in it. `matches` was left alone since CPV/country is about the notice content and "have I reported this" is about history. For the failure isolation, split `score_notices` so it only scores — the threshold and the sort moved out into a new `select_for_digest`, which meant `score_notices` now returns every notice that scored without raising, which is exactly the list that needs marking, so no extra return value was needed. Wrapped only the `scorer.score(...)` call in try/except Exception inside the loop, logging with `logger.exception` and `continue`, so one bad notice is skipped and left unseen while the run carries on. A failed TED fetch is the opposite — nothing catches it, so it escapes `run`, and `cli.py` wraps the `run(...)` call to print to stderr and `sys.exit(1)`; library code raises, the entry point decides the exit code. `store.mark_seen(...)` goes after `digest_path.write_text(...)`, not before, so a failed write can never leave notices marked as reported when they were never in a digest — the worst case becomes a duplicate tomorrow instead of a tender lost forever. Tested with a real `SeenStore` against `tmp_path`, a `FakeScorer` that takes a `raises` set of ids, and a `FailingTedClient` that only raises.

- ticket 07 created `ted.py` by creating `TedApiClient`, `_pick_language`, `to_notice`. `to_notice` create Notice class from raw TED notice. `_pick_language` picks the language from the raw notice. `TedApiClient` is the class for fetching notices
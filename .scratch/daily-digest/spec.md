# Spec: Daily tender digest

Status: ready-for-agent

## Problem Statement

A business-development person at a Geo-data company (Fugro, used here as a stand-in)
needs to know early when an EU public buyer publishes a tender the company could bid on.
Today that means manually watching TED, the EU's official procurement channel, which
publishes hundreds of notices a day across every sector and language. Relevant notices
are easy to miss, and every day missed is a day less to prepare a bid.

## Solution

A tool that, once a day, reads the last week of TED notices, narrows them to the
company's sectors and countries, has a language model judge how well each fits a short
company profile, and writes a digest file listing the strong matches — highest score
first, each with a one-line reason and a link to the notice on TED. Notices already
reported in a previous digest are left out. It runs as a command locally and, when
deployed, as a daily scheduled job.

## User Stories

1. As a BD user, I want a digest of new relevant tenders produced once a day, so that I can review opportunities without watching TED myself.
2. As a BD user, I want each digest entry to link to the full notice on TED, so that I can read the detail and decide whether to pursue it.
3. As a BD user, I want each digest entry to carry a one-sentence rationale, so that I can triage the list quickly.
4. As a BD user, I want the digest sorted by relevance score, so that the best opportunities are at the top.
5. As a BD user, I want notices below a relevance threshold excluded, so that the digest stays short and worth reading.
6. As a BD user, I want to configure the relevance threshold, so that I can tune digest length without a code change.
7. As a BD user, I want to restrict notices to chosen CPV codes, so that only my company's procurement categories are considered.
8. As a BD user, I want to restrict notices to chosen countries, so that I can focus on markets we operate in.
9. As a BD user, I want the country list to default to all EU countries, so that I get full coverage if I don't narrow it.
10. As a BD user, I want to write a free-text company profile in config, so that the language model judges relevance against what we actually do.
11. As a BD user, I want to change the scoring model name in config, so that I can move to a better model later without a code change.
12. As a BD user, I want notices in any EU language processed, so that a relevant tender in Portuguese or Finnish is not silently dropped.
13. As a BD user, I want the rationale written in English, so that the whole digest is readable to me regardless of the notice's language.
14. As a BD user, I want notices already included in a past digest left out of future ones, so that I only see each opportunity once.
15. As a BD user, I want a notice that failed to be scored to reappear in a later run, so that a transient error doesn't lose an opportunity.
16. As a BD user, I want each run to look back a fixed seven days, so that a missed run or two self-heals without configuration.
17. As a BD user, I want a run to stop with an error if TED itself can't be reached, so that the schedule retries rather than producing a misleadingly empty digest.
18. As a BD user, I want a run where one notice fails to score to still produce a digest from the rest, so that one bad notice doesn't cost me the day's digest.
19. As a BD user, I want to run the tool by hand from the command line, so that I can get a digest on demand and test changes locally.
20. As an operator, I want the same command to run unattended on a daily schedule, so that deployment is a scheduling change, not a rewrite.
21. As an operator, I want the seen state and the digest file to persist between scheduled runs, so that dedup works in the deployed environment.
22. As a BD user, I want the first run to only look back seven days like any other, so that I'm not flooded with a large backlog on day one.
23. As a BD user, I want an empty digest written (not an error) when nothing clears the threshold, so that I can tell the run succeeded and there was simply nothing.
24. As a developer, I want the pipeline testable without calling TED or the language model, so that tests are fast, deterministic, and free.

## Implementation Decisions

### Modules

- **`run` orchestrator** — the single entry point and test seam. Takes the resolved config, a TED client, a scorer, a seen-store, and the current date; performs fetch → prefilter → score → threshold → write digest → record seen; returns the digest text.
- **TED client** — wraps the TED API. Given the fetch window and query constraints, returns a list of notices (id, title, buyer country, CPV codes, notice text, TED URL, publication date). The only component that makes TED HTTP calls.
- **Scorer** — wraps the language model via LangChain. Given a notice and the company profile, returns an integer relevance score (1–100) and an English rationale string. The only component that calls OpenAI. Uses structured output so the score and rationale come back as typed fields.
- **Seen-store** — a SQLite file recording notice ids already reported. Supports "which of these ids are new?" and "mark these ids seen." A notice id is written only after that notice has been successfully scored and thresholded in the current run.
- **Config loader** — reads `config.yaml` into a typed config object: `cpv_codes` (list), `countries` (list, default all EU), `company_profile` (string), `min_score` (int, default 60), `model` (string, default `gpt-5-mini`).
- **Digest writer** — renders the surviving notices to `digest.md`, sorted by score descending, each entry showing score, title, buyer country, rationale, and TED URL. Overwrites the file each run.
- **CLI** — a single command that loads config, constructs the real TED client / scorer / seen-store, calls `run`, and exits non-zero if `run` raised (e.g. TED unreachable).

### Flow and rules

- **Fetch window**: always the last 7 calendar days ending at the run date, regardless of last run time (ADR 0001). Overlap is expected; the seen-store absorbs it.
- **Prefilter** (no model calls): keep a notice only if at least one of its CPV codes is in `cpv_codes` and its buyer country is in `countries`. Then drop notices whose id is already in the seen-store.
- **Score**: one model call per surviving notice. Notice text is passed in its original language; the prompt is English and asks for an English rationale.
- **Threshold**: keep notices with `score >= min_score`.
- **Record seen**: mark the ids of every notice that was successfully scored this run (whether or not it cleared the threshold), so a notice that scored low is not re-scored tomorrow. A notice that errored during scoring is not marked, so it is retried next run.
- **Failure handling** (ADR-aligned with grill Q15): a failed TED fetch raises and aborts the run with a non-zero exit. A failure scoring a single notice is logged, that notice is skipped and left unseen, and the run continues.
- **Empty result**: `digest.md` is still written (with a "no matching notices" body) and the run exits zero.

### Data source

- TED only (ADR 0002). National procurement portals are out of scope.

### Deployment

- Packaged as a container running the CLI. Deployed as an Azure Container Apps Job on a daily cron schedule. `config.yaml`, `seen.sqlite`, and `digest.md` live on a mounted Azure File share so state and output persist across runs. The OpenAI API key is supplied as an environment variable / secret.

## Testing Decisions

- **What a good test looks like**: drives the `run` orchestrator with fake collaborators and asserts only on externally observable results — the digest text, the ordering, which notices were included or excluded, and which ids ended up in the seen-store. Tests never assert on how prefiltering or formatting is implemented internally.
- **Fakes**:
  - Fake TED client returns a fixed, hand-authored list of notices covering the interesting cases (matching CPV + country, wrong CPV, wrong country, already-seen, non-English text, one that the fake scorer will fail on).
  - Fake scorer returns deterministic scores keyed by notice id, and can be told to raise for a specific id.
  - Real seen-store against a temp SQLite file (created fresh per test).
- **Modules tested**: `run` (covering prefilter, threshold, dedup, seen-recording, per-notice failure isolation, empty-digest behaviour, ordering). The config loader gets a small separate test for defaults. The real TED client and real scorer are not unit-tested against live services; their contract is exercised through the fakes.
- **Prior art**: none yet — this is the first feature. These tests set the pattern: one high seam, fakes for external services, real lightweight infrastructure (SQLite) against temp files.
- **TED fetch failure**: a fake TED client that raises is used to assert the run aborts with a non-zero result and writes no digest.

## Out of Scope

- National procurement portals and any non-TED source (ADR 0002).
- Email, Slack/Teams, or any delivery channel other than the `digest.md` file.
- A web UI or searchable dashboard.
- Below-threshold contracts (not published on TED).
- Real-time / intra-day alerting.
- Historical backfill beyond the 7-day window.
- Learning from user feedback / adjusting scores over time.
- Multi-company support (one company profile per deployment).
- Prompt-engineering sophistication beyond a single straightforward scoring prompt.
- Retry/backoff logic for the model calls beyond "skip and retry next run."

## Further Notes

- The 1–100 score is only meaningful in broad bands; language models cluster on round
  numbers, so `min_score` should be treated as a coarse dial, not a precise cutoff.
- CPV codes for the reference company are chosen by the user during implementation and
  recorded in `config.yaml`; they are not part of this spec.
- The exact TED API query syntax, auth, field names, and rate limits still need to be
  confirmed against TED's documentation (a `/research` task) before the TED client is built.
- First deployable slice = the whole of this spec; there is no smaller useful version.

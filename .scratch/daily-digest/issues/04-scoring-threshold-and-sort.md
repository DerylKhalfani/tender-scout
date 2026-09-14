# 04: Scoring, threshold & sort

**What to build:** `run` has a scorer judge each prefiltered notice against the company
profile, keeps only the strong matches, and writes them to `digest.md` best-first with a
rationale. An empty result is a successful run, not an error.

**Blocked by:** 03

**Status:** ready-for-agent

- [x] `run` takes a scorer collaborator; for each prefiltered notice it gets an integer score (1–100) and an English rationale
- [x] Notices with `score < config.min_score` are dropped
- [x] `digest.md` lists survivors sorted by score descending, each showing score, title, buyer country, rationale, TED URL
- [x] When nothing clears the threshold, `digest.md` is written with a "no matching notices" body and the run exits zero
- [x] Verified through `run` with a fake scorer returning deterministic scores by notice id

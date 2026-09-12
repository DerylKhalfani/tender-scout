# 02: `run` fetches and writes a digest (fakes, no filtering)

**What to build:** the `run` orchestrator — the single test seam for the whole feature.
Given a TED client, it fetches notices for the last 7 days and writes every one of them
to `digest.md`. No prefiltering, no scoring yet. The CLI calls `run`. This establishes
the seam and the fake-collaborator testing pattern.

**Blocked by:** 01

**Status:** ready-for-agent

- [x] `run` takes the resolved config, a TED client, and the current date as inputs
- [x] `run` asks the TED client for notices over a fixed 7-day window ending on the current date (ADR 0001)
- [x] Every returned notice is written to `digest.md` with title, buyer country, and TED URL
- [x] The CLI constructs a (real or placeholder) TED client and calls `run`
- [x] Tests drive `run` with a fake TED client returning a hand-authored notice list and assert on `digest.md` contents
- [x] Notice fields available downstream: id, title, buyer country, CPV codes, notice text, TED URL, publication date

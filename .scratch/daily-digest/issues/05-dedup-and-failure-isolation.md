# 05: Dedup & per-notice failure isolation

**What to build:** `run` only reports each notice once across days, and one bad notice
never costs the whole digest. A real SQLite seen-store backs the dedup.

**Blocked by:** 04

**Status:** ready-for-agent

- [ ] A SQLite seen-store records notice ids already reported; supports "which of these are new?" and "mark these seen"
- [ ] Notices whose id is already seen are dropped during prefilter
- [ ] A notice that was successfully scored this run is marked seen whether or not it cleared the threshold
- [ ] A notice whose scoring raised is logged, skipped, left unseen, and the run continues and still writes a digest from the rest
- [ ] A failed TED fetch raises, aborts the run with a non-zero exit, and writes no digest
- [ ] Tests use a real seen-store against a temp SQLite file and a fake scorer that can be told to raise for a given id

# 10: Review cleanup from ticket 05

**What to build:** the non-blocking findings from the ticket 05 code review. Nothing here
changes behaviour the digest depends on; it closes the gap between what the code does and
what the docs and names say it does.

**Blocked by:** 05

**Status:** ready-for-agent

- [ ] `CONTEXT.md` "Prefilter" says only CPV + country, but `filter_notices` also drops already-seen notices — either widen the definition or move the dedup into its own step in `run`
- [ ] `cli.py` catches bare `Exception` around the whole `run(...)`, so a failed `mark_seen` reports "run failed" and exits 1 even though a valid digest was written; it also drops the traceback the operator needs
- [ ] No test covers the `sys.exit(1)` path in `cli.py` — only that `run` raises
- [ ] `SeenStore.seen` reads the whole table and intersects in Python, so it scales with total history rather than with the query; a `WHERE id IN (...)` would scope it
- [ ] Naming: `store.seen()` reads as a predicate but returns a subset; `filtered_scored_notices` in `run` overloads "filtered" a third time; `test_a_failed_aborts_the_run_and_writes_no_digest` is missing its subject ("fetch")
- [ ] `SeenStore.seen` has no docstring, though it is the method with the non-obvious return
- [ ] No formatter configured — trailing whitespace and missing EOF newlines in `run.py`, `cli.py`, `filters.py`, `test_filters.py`; add the tool rather than fixing by hand

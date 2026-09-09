# Overlapping fetch window with dedup, not incremental sync

Every run fetches the last 7 days of TED notices regardless of when the previous run
happened, and relies on the seen state to suppress notices already reported. We chose
this over an incremental "everything since the last run" sync for robustness: a few
missed runs self-heal, and no notice is lost to a clock, timezone, or state-file bug.
The cost is redundant API calls each run, which is negligible at TED's volume.

# 06: Research — TED API contract

**What to build:** a cited Markdown file in the repo documenting how the real TED API
works, so the TED client (07) can be built without guesswork.

**Blocked by:** None (can start immediately, in parallel with 01–05)

**Status:** ready-for-agent

- [ ] Documents authentication (key required? how obtained?)
- [ ] Documents the query mechanism for: publication-date window, CPV code, buyer country
- [ ] Documents the fields a contract notice exposes, mapped to what `run` needs (id, title, buyer country, CPV codes, notice text, TED URL, publication date)
- [ ] Documents rate limits, pagination, and result-size limits
- [ ] Every claim links to official TED documentation
- [ ] Saved as a Markdown file in the repo (e.g. under `docs/`)

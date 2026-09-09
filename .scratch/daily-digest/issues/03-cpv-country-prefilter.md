# 03: CPV + country prefilter

**What to build:** `run` narrows the fetched notices to the ones that concern the
company before anything expensive happens — only notices matching a configured CPV code
and a configured country reach the digest.

**Blocked by:** 02

**Status:** ready-for-agent

- [ ] A notice is kept only if at least one of its CPV codes is in `config.cpv_codes`
- [ ] A notice is kept only if its buyer country is in `config.countries`
- [ ] Notices failing either check never appear in `digest.md`
- [ ] Verified through `run` with a fake TED client covering: match, wrong CPV, wrong country, multiple CPV codes where one matches

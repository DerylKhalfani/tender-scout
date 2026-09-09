# 01: Project skeleton & config loader

**What to build:** `tender-scout` runs as a command that loads `config.yaml` into a
typed config object and fails clearly when the file is missing or malformed. This is the
prefactor that every other ticket builds on.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] Runtime deps (LangChain, OpenAI SDK, a YAML parser) and test deps (pytest) are in `pyproject.toml`
- [ ] `config.yaml` is parsed into a typed config with fields: `cpv_codes` (list of str), `countries` (list of str), `company_profile` (str), `min_score` (int), `model` (str)
- [ ] `countries` defaults to all EU member states when absent
- [ ] `min_score` defaults to 60, `model` defaults to `gpt-5-mini` when absent
- [ ] A missing or malformed `config.yaml` exits non-zero with a message naming the problem
- [ ] The CLI entry point runs and loads the config (printing a summary is enough for now)
- [ ] A test covers the defaults and the missing-file error

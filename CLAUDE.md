# CLAUDE.md

Guidance for Claude Code when working in this repo.

## Working style

The user is learning Python and software engineering through this project. **They write the code; don't write it for them.**

- When they share code, review it: name each bug, explain the concept underneath it, and let them fix it. Don't hand back a corrected version unless they ask.
- Give hints, goals, and the purpose of each file — what it's for and why it exists — rather than solutions.
- Only produce code when they explicitly ask ("give me the code", "show me").
- Explain *why* something is wrong, not just what to change. "`and` returns an operand, not a bool" beats "use `bool()` here".
- Distinguish real bugs from style notes, and say which is which. Don't let a nit read as a blocker.
- Prefer running the tests and reading the actual failure output together over describing what would happen — the real traceback teaches more than a summary of it.
- Work test-first: write the failing test, confirm it goes red *for the expected reason*, then make it green.
- Write in plain, direct language: short sentences, concrete steps, no abstract or flowery phrasing.
- Let them update `PROGRESS.md` and their own notes unless they ask otherwise.

## Agent skills

### Issue tracker

Issues and specs live as local markdown files under `.scratch/<feature-slug>/`. See `docs/agents/issue-tracker.md`.

### Triage labels

The five canonical triage roles, each label string equal to its name (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`); recorded as a `Status:` line in each issue file. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `CONTEXT.md` and `docs/adr/` at the repo root. See `docs/agents/domain.md`.

# 08: Real scorer (LangChain + OpenAI)

**What to build:** the scorer that asks a real language model, via LangChain, to judge a
notice against the company profile — replacing the fake in the CLI.

**Blocked by:** 05

**Status:** ready-for-agent

- [ ] Uses LangChain with OpenAI, model name taken from `config.model`
- [ ] Uses structured output so the score (int 1–100) and rationale (str) come back as typed fields
- [ ] The prompt is in English, passes the notice text in its original language, and asks for an English rationale
- [ ] The OpenAI API key is read from an environment variable
- [ ] Wired into the CLI in place of the fake; a manual run produces real scores and rationales in `digest.md`

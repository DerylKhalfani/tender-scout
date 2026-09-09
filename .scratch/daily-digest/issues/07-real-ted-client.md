# 07: Real TED client

**What to build:** the TED client that hits the live TED API, replacing the fake in the
CLI. Running the command produces a digest from real notices.

**Blocked by:** 05, 06

**Status:** ready-for-agent

- [ ] The client fetches notices for the 7-day window, constrained by `cpv_codes` and `countries` where the API supports it (otherwise filtered client-side, keeping 03's behaviour)
- [ ] It maps the TED response onto the notice fields `run` expects
- [ ] It handles pagination so a full window is retrieved
- [ ] A TED outage or error surfaces as the failure `run` treats as fatal (per 05)
- [ ] It is wired into the CLI in place of the fake; a manual run against live TED produces a `digest.md`
- [ ] `run`'s tests still use the fake client and are unchanged

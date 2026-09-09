# 09: Containerize & deploy to Azure Container Apps Job

**What to build:** the same CLI, running unattended once a day on Azure, with config,
state, and output persisted between runs.

**Blocked by:** 07, 08

**Status:** ready-for-agent

- [ ] A Dockerfile builds an image that runs the `tender-scout` command
- [ ] Deployed as an Azure Container Apps Job on a daily cron schedule
- [ ] `config.yaml`, `seen.sqlite`, and `digest.md` live on a mounted Azure File share and survive between runs
- [ ] The OpenAI API key is supplied as a secret / environment variable, not baked into the image
- [ ] A non-zero exit from a run (e.g. TED unreachable) is visible in Azure so the schedule's retry behaviour applies
- [ ] Deployment steps a human must do by hand are captured (a `/wizard` script or a short runbook)

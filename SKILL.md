---
name: TrajectoryLock
description: Use this when testing geometric compatibility of a reconstructed trajectory with a declared official line. Research prototype, not a certified forensic instrument. Hosted /v1 via this Worker and aziel-runtime. Dual surface: Worker /v1 + catalog MCP. This Worker /v1/mesh/* PROXY to aziel-runtime via AZIEL_RUNTIME. Suite mesh default OFF. QNM-BUILD-1.0 live|locked|isolated. QNS-CD-1.0 photon QNS1 packet transfer is a hub cite / Worker mesh cross-map only (qnm-node qnsd + aziel-runtime cite; AZInterface pair custody). No Node Gate. No public qnsd proxy. No auto-heal. Not anonymity. Author Aziel Eliab.
---

# TrajectoryLock

Auditable geometric trajectory test. Author: **Aziel Eliab**.

**THIS IS:** research prototype / auditable geometric test. Compatibility vs declared official line. Independence groups so copies don't inflate certainty. CLI + local workbench + JSON API.

**THIS IS NOT:** a certified forensic instrument; substitute for scene reconstruction, medical findings, lab exam; shooter/intent/guilt/narrative identifier; automatic detection of invisible projectiles; face recognition. Match probability is P(match | declared model), not P(official account is true). Synthetic example results must never be represented as real-case findings.

Always send a normal `User-Agent` (for example `Mozilla/5.0`). Cloudflare Workers may 403 empty agents.

## When to call it

- Score a **small JSON case** (sources + observations + official_hypothesis) for geometric compatibility.
- Fetch the synthetic example. Never present it as a real case.
- Health / skill / OpenAPI. Never invent a shooter, intent, or guilt.

Local UI is one screen: load JSON, run check, see the result. Import and Export. Doctor/Verify speak in plain words.

Hosted `/v1/analyze` caps JSON size and **never stores media**. Full reconstruction is the local package: `trajectorylock analyze` / `trajectorylock ui`.

## Endpoints (this Worker)

Host: `https://trajectorylock-download-tracker.vibelock.workers.dev`

| Method | Path | What |
|--------|------|------|
| GET | `/v1/health` | Liveness. Does not increment downloads. |
| GET | `/v1/skill` | This markdown. Does not increment downloads. |
| GET | `/v1/mesh` | PROXY suite mesh status. Default OFF. QNM live|locked|isolated. QNS-CD-1.0 cross-map in the payload. Never enables. |
| GET | `/v1/mesh/nodes` | PROXY Live Nodes roster (5-minute presence). |
| POST | `/v1/mesh/{enable,disable,join,heartbeat,leave,broadcast}` | PROXY. Bearer required to enable. No auto-heal. |
| GET | `/v1/example` | Synthetic small JSON case. Not a real case. |
| POST | `/v1/analyze` | Small JSON case in → result. Cap size. Never stores media. |

OpenAPI: `https://trajectorylock-download-tracker.vibelock.workers.dev/openapi.json`

Catalog OpenAPI: `https://aziel-runtime.vibelock.workers.dev/openapi.json`

MCP: `POST https://trajectorylock-download-tracker.vibelock.workers.dev/mcp`
also `POST https://aziel-runtime.vibelock.workers.dev/mcp`

## How to call (Mozilla/5.0)

```bash
curl -s -A 'Mozilla/5.0' https://trajectorylock-download-tracker.vibelock.workers.dev/v1/health

curl -s -A 'Mozilla/5.0' https://trajectorylock-download-tracker.vibelock.workers.dev/v1/mesh

curl -s -A 'Mozilla/5.0' https://trajectorylock-download-tracker.vibelock.workers.dev/v1/example

curl -s -A 'Mozilla/5.0' -X POST https://trajectorylock-download-tracker.vibelock.workers.dev/v1/analyze \
  -H 'content-type: application/json' \
  -d '{"case_id":"MINIMAL-DIRECT-LINE","sources":[{"id":"survey-a","quality":0.95,"calibrated":true,"independence_group":"survey-a"}],"observations":[{"type":"direct_line","source_id":"survey-a","point":[0,0,1.2],"direction":[1,0.1,0.02],"angular_sigma_deg":0.5,"offset_sigma_m":0.02}],"official_hypothesis":{"point":[0.01,0.01,1.19],"direction":[1,0.11,0.02],"angular_sigma_deg":0.7,"offset_sigma_m":0.04,"angle_tolerance_deg":3.0,"offset_tolerance_m":0.25},"analysis":{"monte_carlo_samples":400,"random_seed":7}}'
```

Catalog aliases:

```bash
curl -s -A 'Mozilla/5.0' -X POST https://aziel-runtime.vibelock.workers.dev/p/trajectorylock/analyze \
  -H 'content-type: application/json' \
  -d '{"case_id":"MINIMAL-DIRECT-LINE","sources":[{"id":"survey-a","quality":0.95,"calibrated":true,"independence_group":"survey-a"}],"observations":[{"type":"direct_line","source_id":"survey-a","point":[0,0,1.2],"direction":[1,0.1,0.02],"angular_sigma_deg":0.5,"offset_sigma_m":0.02}],"official_hypothesis":{"point":[0.01,0.01,1.19],"direction":[1,0.11,0.02],"angular_sigma_deg":0.7,"offset_sigma_m":0.04,"angle_tolerance_deg":3.0,"offset_tolerance_m":0.25}}'
```

MCP tools: `trajectorylock_health`, `trajectorylock_example`, `trajectorylock_analyze`, `trajectorylock_skill`.

## Use with AI clients

Works with ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude (Anthropic), Cursor (MCP), Glama (MCP), Perplexity, Microsoft Copilot / Bing, Google Gemini / Vertex, Mistral, Meta AI, Apple Intelligence surfaces, Amazon Q tooling, DuckAssist, You.com, Cohere, and other MCP/OpenAPI-capable assistants.

Import the catalog OpenAPI as a custom tool, GPT Action, or HTTP tool. Connect MCP remotes in Cursor, Glama, and other MCP clients.

## Honest banner

THIS IS: research prototype / auditable geometric test. Compatibility vs declared official line. Independence groups so copies don't inflate certainty.

THIS IS NOT: a certified forensic instrument; substitute for scene reconstruction, medical findings, lab exam; shooter/intent/guilt/narrative identifier; automatic detection of invisible projectiles; face recognition.

Match probability is P(match | declared model), not P(official account is true). Synthetic example results must never be represented as real-case findings.

Paper: TL-WP-0.1 · TrajectoryLock_v0.1.pdf

DOI: https://doi.org/10.5281/zenodo.22258015
Record: https://zenodo.org/records/22258015
File: TrajectoryLock_v0.1.pdf · Apache-2.0 · Eliab, Aziel

Forks are welcome and always allowed.

Local UI: Import JSON file and Export JSON. Worker homepage Live Nodes strip polls `GET /v1/mesh` (default OFF). QNS-CD-1.0 (photon QNS1 packet transfer) is a hub cite / Worker mesh cross-map only — local qnsd lives in [qnm-node](https://github.com/AzielEliab/qnm-node); runtime cites + catalog field live in [aziel-runtime](https://github.com/AzielEliab/aziel-runtime); pair custody is [AZInterface](https://github.com/AzielEliab/azinterface). Not a Softwares-tab product. No public qnsd proxy.

# TrajectoryLock

Checks how close a line is to a claimed line. Research prototype, not a certified forensic instrument. Does not identify a shooter, intent, or guilt.

**Author:** Aziel Eliab
**Date:** 2 September 2026
**License:** [Apache-2.0](LICENSE)
**Version:** 0.1.0
**Spec:** `trajectorylock-v0.1`
**Paper:** TL-WP-0.1 — [docs/TrajectoryLock_v0.1.pdf](docs/TrajectoryLock_v0.1.pdf) · DOI [10.5281/zenodo.22258015](https://doi.org/10.5281/zenodo.22258015)

**Forks are welcome and always allowed.**

## Three steps

1. Install: `curl -fsSL https://trajectorylock-download-tracker.vibelock.workers.dev/install.sh | bash`
2. Run `trajectorylock ui` and open http://127.0.0.1:8874 (this computer only).
3. Tap **Load example** (or **Import** your JSON), then **Run check**. Read the three numbers. **Export** if you want a receipt.

Those numbers say how close a line is to a claimed line. They do not name a shooter, intent, or guilt.

## Honest scope

**THIS IS:** research prototype / auditable geometric test. Compatibility vs declared official line. Independence groups so copies don't inflate certainty. CLI + local workbench + JSON API.

**THIS IS NOT:** a certified forensic instrument; substitute for scene reconstruction, medical findings, lab exam; shooter/intent/guilt/narrative identifier; automatic detection of invisible projectiles; face recognition. Match probability is P(match | declared model), not P(official account is true). Synthetic example results must never be represented as real-case findings. No private case facts.

Public identity **Aziel Eliab** only.

## Counted download (Cloudflare Worker)

**This is the counted download.** GitHub releases exist as a mirror.
The Worker serves the gzip itself (HTTP 200, no 302 to GitHub).

# → [https://trajectorylock-download-tracker.vibelock.workers.dev/](https://trajectorylock-download-tracker.vibelock.workers.dev/) ←

Direct tarball (also counted):
[trajectorylock-0.1.0.tar.gz](https://trajectorylock-download-tracker.vibelock.workers.dev/download?asset=trajectorylock-0.1.0.tar.gz)

- Live count JSON: [https://trajectorylock-download-tracker.vibelock.workers.dev/stats](https://trajectorylock-download-tracker.vibelock.workers.dev/stats)
- OpenAPI: [https://trajectorylock-download-tracker.vibelock.workers.dev/openapi.json](https://trajectorylock-download-tracker.vibelock.workers.dev/openapi.json)
- Skill: [https://trajectorylock-download-tracker.vibelock.workers.dev/v1/skill](https://trajectorylock-download-tracker.vibelock.workers.dev/v1/skill)
- GitHub: [https://github.com/AzielEliab/trajectorylock](https://github.com/AzielEliab/trajectorylock)

Isolated counter: Worker `trajectorylock-download-tracker`, KV `TRAJECTORYLOCK_DOWNLOADS`. Not mixed with any other product. `/v1` does not increment downloads. Hosted `/v1` never stores media.

Or tap **Download** / **One-click install** on the Worker homepage:
https://trajectorylock-download-tracker.vibelock.workers.dev/

## From source

```bash
python -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"
python -m trajectorylock.cli demo -o result.json
trajectorylock ui
trajectorylock doctor
python -m pytest -q
```

Open http://127.0.0.1:8874. No CDN, no telemetry.

## CLI

```bash
python3 trajectorylock.py demo -o result.json
python3 trajectorylock.py analyze examples/example_case.json -o result.json
python3 trajectorylock.py hash-media video.mp4 photo.jpg
trajectorylock ui
trajectorylock doctor
```

## Local UI

`trajectorylock ui` serves a loopback dashboard at http://127.0.0.1:8874

One obvious screen: **Load example** / **Import** JSON, **Run check**, see the result. **Export**. **Verify** and **Doctor** speak in plain words.
Three separate numbers: *how close is this line to the claimed line* (compatibility), match chance, how strong is the evidence.
Binds `127.0.0.1` only.

## iPhone & Android

Flutter sources: [`mobile/`](mobile/). Application id
`com.azieeliab.trajectorylock`. Offline. No analytics. Dark matte / gold.
Not a store listing. Not a separate repo. Not store IPAs.

```bash
cd mobile
flutter create --org com.azieeliab --project-name trajectorylock .
flutter pub get
flutter run
```

## Hosted `/v1`

The Worker hosts a **stateless** JSON API. It does not increment DOWNLOADS. It never stores media.

- `GET /v1/health`
- `GET /v1/skill` — this repo's [SKILL.md](SKILL.md)
- `GET /v1/example` — synthetic small JSON case
- `POST /v1/analyze` — small JSON case in, result out (size cap; never stores media)
- OpenAPI: `/openapi.json`
- MCP: this Worker `/mcp` and catalog `https://aziel-runtime.vibelock.workers.dev/mcp`

Banner: not a certified instrument.

Always send `User-Agent: Mozilla/5.0`. Empty agents can 403.

Works with ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude (Anthropic), Cursor (MCP), Glama (MCP), Perplexity, Microsoft Copilot / Bing, Google Gemini / Vertex, Mistral, Meta AI, Apple Intelligence surfaces, Amazon Q tooling, DuckAssist, You.com, Cohere, and other MCP/OpenAPI-capable assistants.

OpenAPI import (GPT Actions, custom tools, HTTP tools):
`https://aziel-runtime.vibelock.workers.dev/openapi.json`

MCP remote: `POST https://aziel-runtime.vibelock.workers.dev/mcp`

Example:

```bash
curl -s -A 'Mozilla/5.0' https://trajectorylock-download-tracker.vibelock.workers.dev/v1/health
curl -s -A 'Mozilla/5.0' -X POST https://aziel-runtime.vibelock.workers.dev/p/trajectorylock/analyze \
  -H 'content-type: application/json' \
  -d '{"case_id":"MINIMAL-DIRECT-LINE","sources":[{"id":"survey-a","quality":0.95,"calibrated":true,"independence_group":"survey-a"}],"observations":[{"type":"direct_line","source_id":"survey-a","point":[0,0,1.2],"direction":[1,0.1,0.02],"angular_sigma_deg":0.5,"offset_sigma_m":0.02}],"official_hypothesis":{"point":[0.01,0.01,1.19],"direction":[1,0.11,0.02],"angular_sigma_deg":0.7,"offset_sigma_m":0.04,"angle_tolerance_deg":3.0,"offset_tolerance_m":0.25},"analysis":{"monte_carlo_samples":400,"random_seed":7}}'
```

## Papers

- Paper (PDF): [TrajectoryLock_v0.1.pdf](https://zenodo.org/records/22258015)
- DOI: [https://doi.org/10.5281/zenodo.22258015](https://doi.org/10.5281/zenodo.22258015)
- Zenodo record: [https://zenodo.org/records/22258015](https://zenodo.org/records/22258015)
- License: Apache-2.0. Creator: Eliab, Aziel.

## Mesh (siblings, not this product)

| Sibling | Boundary |
|---------|----------|
| SpectralLock | Image overlay preview. Not a trajectory solver. |
| EmployeeLock | Accountability workbook. Does not reconstruct lines. |
| FoldLock | Tether-word fold. Not geometry. |
| GodLock | Public ABAD node. Not a forensic instrument. |

## Tests

```bash
python -m pytest -q
```

## Use with AI clients

Works with ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude (Anthropic), Cursor (MCP), Glama (MCP), Perplexity, Microsoft Copilot / Bing, Google Gemini / Vertex, Mistral, Meta AI, Apple Intelligence surfaces, Amazon Q tooling, DuckAssist, You.com, Cohere, and other MCP/OpenAPI-capable assistants.

Catalog OpenAPI: https://aziel-runtime.vibelock.workers.dev/openapi.json
Catalog MCP: `POST https://aziel-runtime.vibelock.workers.dev/mcp`
This Worker skill: https://trajectorylock-download-tracker.vibelock.workers.dev/v1/skill
This Worker OpenAPI: https://trajectorylock-download-tracker.vibelock.workers.dev/openapi.json

Import the catalog or Worker OpenAPI as a custom tool, GPT Action, or HTTP tool. Connect MCP remotes in Cursor, Glama, and other MCP clients. Always send `User-Agent: Mozilla/5.0`.

## Cite this

Aziel Eliab. TrajectoryLock. https://github.com/AzielEliab/trajectorylock. https://trajectorylock-download-tracker.vibelock.workers.dev. https://doi.org/10.5281/zenodo.22258015.

- Catalog: https://aziel-runtime.vibelock.workers.dev/
- Worker homepage: https://trajectorylock-download-tracker.vibelock.workers.dev/
- Counted download (gzip HTTP 200, no 302): https://trajectorylock-download-tracker.vibelock.workers.dev/download
- GitHub: https://github.com/AzielEliab/trajectorylock
- Citation JSON: https://trajectorylock-download-tracker.vibelock.workers.dev/cite.json
- DOI: https://doi.org/10.5281/zenodo.22258015

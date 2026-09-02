/**
 * TrajectoryLock hosted runtime. Small JSON cases only. Never stores media.
 * /v1 never touches DOWNLOADS KV.
 */
import {
  AUTHOR,
  CATALOG,
  DOI,
  EXAMPLE_CASE,
  GUARDRAIL,
  HOST,
  HOSTED_MC_CAP,
  JSON_CAP,
  LIMITATION,
  PRODUCT,
  SPEC,
  VERSION,
  ZENODO,
  analyzeCase,
  looksLikeMedia,
} from "./engine.js";

const EXAMPLE_PAYLOAD = EXAMPLE_CASE;
const PROTOCOL = "2025-03-26";

export const SKILL = `---
name: TrajectoryLock
description: Use this when testing geometric compatibility of a reconstructed trajectory with a declared official line. Research prototype, not a certified forensic instrument. Hosted /v1 via this Worker and aziel-runtime. Author Aziel Eliab.
---

# TrajectoryLock

Auditable geometric trajectory test. Author: **Aziel Eliab**.

**THIS IS:** research prototype / auditable geometric test. Compatibility vs declared official line. Independence groups so copies don't inflate certainty. CLI + local workbench + JSON API.

**THIS IS NOT:** a certified forensic instrument; substitute for scene reconstruction, medical findings, lab exam; shooter/intent/guilt/narrative identifier; automatic detection of invisible projectiles; face recognition. Match probability is P(match | declared model), not P(official account is true). Synthetic example results must never be represented as real-case findings.

Always send a normal \`User-Agent\` (for example \`Mozilla/5.0\`). Cloudflare Workers may 403 empty agents.

## When to call it

- Score a **small JSON case** (sources + observations + official_hypothesis) for geometric compatibility.
- Fetch the synthetic example. Never present it as a real case.
- Health / skill / OpenAPI. Never invent a shooter, intent, or guilt.

Local UI is one screen: load JSON, run check, see the result. Import and Export. Doctor/Verify speak in plain words.

Hosted \`/v1/analyze\` caps JSON size and **never stores media**. Full reconstruction is the local package: \`trajectorylock analyze\` / \`trajectorylock ui\`.

## Endpoints (this Worker)

Host: \`https://trajectorylock-download-tracker.vibelock.workers.dev\`

| Method | Path | What |
|--------|------|------|
| GET | \`/v1/health\` | Liveness. Does not increment downloads. |
| GET | \`/v1/skill\` | This markdown. Does not increment downloads. |
| GET | \`/v1/example\` | Synthetic small JSON case. Not a real case. |
| POST | \`/v1/analyze\` | Small JSON case in → result. Cap size. Never stores media. |

OpenAPI: \`https://trajectorylock-download-tracker.vibelock.workers.dev/openapi.json\`

Catalog OpenAPI: \`https://aziel-runtime.vibelock.workers.dev/openapi.json\`

MCP: \`POST https://trajectorylock-download-tracker.vibelock.workers.dev/mcp\`
also \`POST https://aziel-runtime.vibelock.workers.dev/mcp\`

## How to call (Mozilla/5.0)

\`\`\`bash
curl -s -A 'Mozilla/5.0' https://trajectorylock-download-tracker.vibelock.workers.dev/v1/health

curl -s -A 'Mozilla/5.0' https://trajectorylock-download-tracker.vibelock.workers.dev/v1/example

curl -s -A 'Mozilla/5.0' -X POST https://trajectorylock-download-tracker.vibelock.workers.dev/v1/analyze \\
  -H 'content-type: application/json' \\
  -d '{"case_id":"MINIMAL-DIRECT-LINE","sources":[{"id":"survey-a","quality":0.95,"calibrated":true,"independence_group":"survey-a"}],"observations":[{"type":"direct_line","source_id":"survey-a","point":[0,0,1.2],"direction":[1,0.1,0.02],"angular_sigma_deg":0.5,"offset_sigma_m":0.02}],"official_hypothesis":{"point":[0.01,0.01,1.19],"direction":[1,0.11,0.02],"angular_sigma_deg":0.7,"offset_sigma_m":0.04,"angle_tolerance_deg":3.0,"offset_tolerance_m":0.25},"analysis":{"monte_carlo_samples":400,"random_seed":7}}'
\`\`\`

Catalog aliases:

\`\`\`bash
curl -s -A 'Mozilla/5.0' -X POST https://aziel-runtime.vibelock.workers.dev/p/trajectorylock/analyze \\
  -H 'content-type: application/json' \\
  -d '{"case_id":"MINIMAL-DIRECT-LINE","sources":[{"id":"survey-a","quality":0.95,"calibrated":true,"independence_group":"survey-a"}],"observations":[{"type":"direct_line","source_id":"survey-a","point":[0,0,1.2],"direction":[1,0.1,0.02],"angular_sigma_deg":0.5,"offset_sigma_m":0.02}],"official_hypothesis":{"point":[0.01,0.01,1.19],"direction":[1,0.11,0.02],"angular_sigma_deg":0.7,"offset_sigma_m":0.04,"angle_tolerance_deg":3.0,"offset_tolerance_m":0.25}}'
\`\`\`

MCP tools: \`trajectorylock_health\`, \`trajectorylock_example\`, \`trajectorylock_analyze\`, \`trajectorylock_skill\`.

Grok: import the catalog OpenAPI as a custom tool. ChatGPT: GPT Actions. Venice: HTTP tools.

## Honest banner

THIS IS: research prototype / auditable geometric test. Compatibility vs declared official line. Independence groups so copies don't inflate certainty.

THIS IS NOT: a certified forensic instrument; substitute for scene reconstruction, medical findings, lab exam; shooter/intent/guilt/narrative identifier; automatic detection of invisible projectiles; face recognition.

Match probability is P(match | declared model), not P(official account is true). Synthetic example results must never be represented as real-case findings.

Paper: TL-WP-0.1 · TrajectoryLock_v0.1.pdf

DOI: https://doi.org/10.5281/zenodo.22258015
Record: https://zenodo.org/records/22258015
File: TrajectoryLock_v0.1.pdf · Apache-2.0 · Eliab, Aziel

Forks are welcome and always allowed.

Local UI: Import JSON file and Export JSON.
`;

function corsHeaders() {
  return {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Accept, MCP-Protocol-Version, mcp-session-id",
  };
}

function json(body, status = 200) {
  return new Response(JSON.stringify(body, null, 2), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8", ...corsHeaders() },
  });
}

function html(body) {
  return new Response(body, {
    headers: { "Content-Type": "text/html; charset=utf-8", ...corsHeaders() },
  });
}

function originOf(request) {
  try {
    return new URL(request.url).origin;
  } catch {
    return HOST;
  }
}

function openapiSpec(origin) {
  return {
    openapi: "3.1.0",
    info: {
      title: "TrajectoryLock runtime",
      version: VERSION,
      summary: "Auditable geometric trajectory test. Research prototype, not a certified forensic instrument.",
      description: LIMITATION,
      license: { name: "Apache-2.0", identifier: "Apache-2.0" },
      contact: { name: "Aziel Eliab", url: "https://github.com/AzielEliab/trajectorylock" },
    },
    servers: [{ url: origin }],
    paths: {
      "/v1/health": {
        get: {
          operationId: "trajectorylock_health",
          summary: "Liveness. Does not increment download KV. Not a certified instrument. Never stores media.",
          responses: { "200": { description: "ok" } },
        },
      },
      "/v1/skill": {
        get: {
          operationId: "trajectorylock_skill",
          summary: "Return TrajectoryLock skill markdown. Does not increment download KV.",
          responses: { "200": { description: "text/markdown" } },
        },
      },
      "/v1/example": {
        get: {
          operationId: "trajectorylock_example",
          summary: "Synthetic small JSON case. Not a real case. Does not increment download KV.",
          responses: { "200": { description: "example case JSON" } },
        },
      },
      "/v1/analyze": {
        post: {
          operationId: "trajectorylock_analyze",
          summary: "Small JSON case in, geometric result out. Cap size. NEVER store media. Not a certified instrument.",
          requestBody: {
            required: true,
            content: {
              "application/json": {
                schema: { type: "object" },
                example: EXAMPLE_CASE,
              },
            },
          },
          responses: { "200": { description: "result manifest" } },
        },
      },
    },
  };
}

function aiHtml(origin) {
  return `<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>TrajectoryLock — AI runtime</title>
<style>
  :root { color-scheme: dark; }
  body { font: 16px/1.45 system-ui, sans-serif; max-width: 44rem; margin: 3rem auto; padding: 0 1.25rem; background: #0e1014; color: #e8eaef; }
  a { color: #c9d4ff; }
  .banner { border: 1px solid #5c4a1a; background: #241c0d; color: #f0d78c; padding: .85rem 1rem; border-radius: 8px; }
  pre { background: #151922; padding: .85rem 1rem; overflow: auto; border-radius: 8px; }
</style>
<body>
<h1>TrajectoryLock runtime</h1>
<p class="banner">${LIMITATION}</p>
<p>Not a certified forensic instrument. Author Aziel Eliab.</p>
<p>OpenAPI: <a href="${origin}/openapi.json">${origin}/openapi.json</a></p>
<p>MCP: POST <code>${origin}/mcp</code> · Catalog: <a href="${CATALOG}/">${CATALOG}</a></p>
<p>Paper: <a href="${DOI}">${DOI}</a> · <a href="${ZENODO}">Zenodo 22258015</a> · TrajectoryLock_v0.1.pdf</p>
<pre>curl -A Mozilla/5.0 ${origin}/v1/health
curl -A Mozilla/5.0 ${origin}/v1/skill
curl -A Mozilla/5.0 ${origin}/v1/example
curl -A Mozilla/5.0 -X POST ${origin}/v1/analyze -H 'content-type: application/json' \\
  -d '{"case_id":"MINIMAL-DIRECT-LINE","sources":[{"id":"survey-a","quality":0.95,"calibrated":true,"independence_group":"survey-a"}],"observations":[{"type":"direct_line","source_id":"survey-a","point":[0,0,1.2],"direction":[1,0.1,0.02],"angular_sigma_deg":0.5,"offset_sigma_m":0.02}],"official_hypothesis":{"point":[0.01,0.01,1.19],"direction":[1,0.11,0.02],"angular_sigma_deg":0.7,"offset_sigma_m":0.04,"angle_tolerance_deg":3.0,"offset_tolerance_m":0.25}}'</pre>
<p>GET/POST under <code>/v1</code> never increment the download counter. Hosted never stores media.</p>
<p><a href="/">Downloads</a></p>
</body></html>`;
}

function mcpTools() {
  return [
    { name: "trajectorylock_health", description: "Liveness. Does not increment download KV. Not a certified instrument.", inputSchema: { type: "object" } },
    { name: "trajectorylock_skill", description: "Return TrajectoryLock skill markdown. Does not increment download KV.", inputSchema: { type: "object" } },
    { name: "trajectorylock_example", description: "Synthetic small JSON case. Not a real case.", inputSchema: { type: "object" } },
    {
      name: "trajectorylock_analyze",
      description: "Small JSON case in, geometric result out. Cap size. NEVER store media. Not a certified forensic instrument.",
      inputSchema: { type: "object", additionalProperties: true },
    },
  ];
}

async function hostedAnalyze(body) {
  if (looksLikeMedia(body)) {
    return {
      error: "hosted analyze never stores media; send a small JSON case only",
      stored: false,
      media_stored: false,
      kv_increment: false,
      limitation: LIMITATION,
    };
  }
  const raw = JSON.stringify(body || {});
  if (raw.length > JSON_CAP) {
    return {
      error: "preview cap ~32KB JSON",
      cap: JSON_CAP,
      got: raw.length,
      stored: false,
      media_stored: false,
      kv_increment: false,
      limitation: LIMITATION,
    };
  }
  const result = await analyzeCase(body);
  result.banner = "not a certified instrument";
  result.doi = DOI;
  result.author = AUTHOR;
  return result;
}

async function handleMcp(request) {
  if (request.method === "GET") {
    return json({
      ok: true,
      transport: "JSON-RPC MCP-over-HTTP",
      endpoint: "POST /mcp",
      methods: ["initialize", "tools/list", "tools/call", "ping"],
      auth: "none (public)",
      limitation: LIMITATION,
    });
  }
  if (request.method !== "POST") return json({ error: "POST JSON-RPC to /mcp" }, 405);
  let body;
  try {
    body = await request.json();
  } catch {
    return json({ jsonrpc: "2.0", id: null, error: { code: -32700, message: "Parse error" } });
  }
  const id = body && body.id !== undefined ? body.id : null;
  const method = body && body.method;
  const params = (body && body.params) || {};
  const result = (value) => json({ jsonrpc: "2.0", id, result: value });
  if (method === "initialize") {
    return result({
      protocolVersion: PROTOCOL,
      capabilities: { tools: { listChanged: false } },
      serverInfo: { name: PRODUCT, version: VERSION },
      instructions: LIMITATION,
    });
  }
  if (method === "notifications/initialized" || method === "initialized") {
    return new Response(null, { status: 204, headers: corsHeaders() });
  }
  if (method === "ping") return result({});
  if (method === "tools/list") return result({ tools: mcpTools() });
  if (method === "tools/call") {
    const name = params.name;
    const args = params.arguments || params.input || {};
    let payload;
    try {
      if (name === "trajectorylock_health") {
        payload = { ok: true, product: PRODUCT, version: VERSION, kv_increment: false, stored: false, media_stored: false, certified_instrument: false, limitation: LIMITATION };
      } else if (name === "trajectorylock_skill") {
        payload = { markdown: SKILL, kv_increment: false, limitation: LIMITATION };
      } else if (name === "trajectorylock_example") {
        payload = { ...EXAMPLE_CASE, kv_increment: false, synthetic: true, certified_instrument: false, limitation: LIMITATION };
      } else if (name === "trajectorylock_analyze") {
        payload = await hostedAnalyze(args);
      } else {
        payload = { error: "unknown tool", name };
      }
    } catch (err) {
      payload = { error: String(err && err.message ? err.message : err), stored: false, limitation: LIMITATION };
    }
    return result({ content: [{ type: "text", text: JSON.stringify(payload) }], isError: Boolean(payload.error) });
  }
  return json({ jsonrpc: "2.0", id, error: { code: -32601, message: "Method not found: " + String(method) } });
}

export async function handleRuntimeApi(request, url) {
  const path = url.pathname.replace(/\/+$/, "") || "/";
  if (path === "/mcp") return handleMcp(request);
  if (path === "/v1/health" && request.method === "GET") {
    return json({
      ok: true,
      product: PRODUCT,
      version: VERSION,
      spec: SPEC,
      runtime: true,
      kv_increment: false,
      stored: false,
      media_stored: false,
      certified_instrument: false,
      banner: "not a certified instrument",
      limitation: LIMITATION,
      guardrail: GUARDRAIL,
      catalog: CATALOG,
      author: AUTHOR,
      doi: DOI,
      zenodo: ZENODO,
      hosted_mc_cap: HOSTED_MC_CAP,
      json_cap: JSON_CAP,
    });
  }
  if (path === "/v1/skill" && request.method === "GET") {
    return new Response(SKILL, {
      status: 200,
      headers: {
        "Content-Type": "text/markdown; charset=utf-8",
        "Cache-Control": "private, no-store",
        "X-KV-Increment": "false",
        ...corsHeaders(),
      },
    });
  }
  if (path === "/v1/example" && request.method === "GET") {
    return json({
      ...EXAMPLE_CASE,
      kv_increment: false,
      stored: false,
      synthetic: true,
      certified_instrument: false,
      limitation: LIMITATION,
      note: "Synthetic example results must never be represented as real-case findings.",
    });
  }
  if (path === "/openapi.json" && request.method === "GET") {
    return json(openapiSpec(originOf(request)));
  }
  if ((path === "/ai" || url.pathname === "/ai/") && request.method === "GET") {
    return html(aiHtml(originOf(request)));
  }
  if (path === "/v1/analyze" && request.method === "POST") {
    let body;
    try {
      body = await request.json();
    } catch {
      return json({ error: "JSON body required", limitation: LIMITATION, stored: false, media_stored: false }, 400);
    }
    try {
      const out = await hostedAnalyze(body);
      return json(out, out.error ? 400 : 200);
    } catch (err) {
      return json({ error: String(err && err.message ? err.message : err), stored: false, media_stored: false, limitation: LIMITATION }, 400);
    }
  }
  if (path.startsWith("/v1/") || path === "/v1") {
    return json({ error: "not found", hint: "GET /v1/health  GET /v1/skill  GET /v1/example  POST /v1/analyze", limitation: LIMITATION, stored: false }, 404);
  }
  return null;
}

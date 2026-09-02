# trajectorylock download tracker

Isolated Worker `trajectorylock-download-tracker`. Project `trajectorylock`.
KV namespace `TRAJECTORYLOCK_DOWNLOADS` bound as `DOWNLOADS`.
Does **not** 302 to GitHub on `/download`. Serves gzip via `ASSETS.fetch`,
`Cache-Control: private, no-store`.

GET `/` increments a **page-view** counter (separate from downloads).
GET `/download` increments **downloads**.
`/v1` never increments DOWNLOADS KV. Hosted never stores media.

Host: https://trajectorylock-download-tracker.vibelock.workers.dev

Paper: https://doi.org/10.5281/zenodo.22258015

#!/usr/bin/env bash
# TrajectoryLock one-click install. Counted download via this project's Worker.
# Usage: curl -fsSL https://trajectorylock-download-tracker.vibelock.workers.dev/install.sh | bash
set -euo pipefail

HOST="${TRAJECTORYLOCK_HOST:-https://trajectorylock-download-tracker.vibelock.workers.dev}"
ASSET="${TRAJECTORYLOCK_ASSET:-trajectorylock-0.1.0.tar.gz}"
WORKDIR="${TRAJECTORYLOCK_HOME:-$HOME/trajectorylock}"

mkdir -p "$WORKDIR"
cd "$WORKDIR"

echo "Downloading counted tarball from ${HOST}/download (User-Agent Mozilla/5.0)…"
curl -fsSL -A 'Mozilla/5.0' "${HOST}/download?asset=${ASSET}" -o "${ASSET}"

tar -xzf "${ASSET}"
DIR="$(find . -maxdepth 1 -type d -name 'trajectorylock-*' | head -n 1)"
if [ -n "${DIR}" ]; then
  cd "${DIR}"
fi

python3 -m venv .venv
# shellcheck disable=SC1091
. .venv/bin/activate
python -m pip install -U pip
python -m pip install -e .

echo
echo "Installed TrajectoryLock."
echo
echo "1. trajectorylock ui"
echo "2. Open http://127.0.0.1:8874/"
echo "3. Press Run check."
echo
echo "Author: Aziel Eliab"

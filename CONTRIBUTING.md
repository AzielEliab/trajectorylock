# Contributing to TrajectoryLock

**Forks are first-class.** This project is Apache-2.0; you do not need
permission to fork, patch, or redistribute.

**Forks are welcome and always allowed.**

## How to run tests

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -m pytest -q
```

Python 3.10+. Core depends on NumPy. pytest is the dev extra. No network.

## Ground rules

1. **Not a certified forensic instrument.** Do not claim courtroom readiness.
2. **Three numbers stay separate:** compatibility, match chance P(match | declared model), evidence strength.
3. **Independence groups.** Copies of one clip must not inflate certainty.
4. **UI binds loopback only** (`127.0.0.1:8874`). One obvious screen: load JSON, run check, see result. Import + Export. Do not listen on `0.0.0.0` from `trajectorylock ui`. No telemetry. No CDN.
5. **Do not mix the download tracker** with any other product's Worker or KV. Namespace `TRAJECTORYLOCK_DOWNLOADS` only.
6. **Public identity is Aziel Eliab only.** Never attach a GodLock-plus-AZ identity label.
7. Synthetic example results must never be represented as real-case findings. No private case facts.
8. New behavior needs a test that fails without the change.

## Where to change things

- Geometry: `trajectorylock/geometry.py`
- Scoring: `trajectorylock/scoring.py`
- Pipeline: `trajectorylock/pipeline.py`
- CLI: `trajectorylock/cli.py`
- Doctor: `trajectorylock/doctor.py`
- Local UI: `trajectorylock/server.py`, `trajectorylock/static/`
- Skill: `SKILL.md`
- Flutter: `mobile/`
- Isolated counter: `workers/download-tracker/`

## License of contributions

By submitting a change you agree it is licensed under Apache-2.0, the
same license as the rest of the tree. Keep the copyright lines honest.
Ship as Aziel Eliab.

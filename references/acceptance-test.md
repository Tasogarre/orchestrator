# Installation and acceptance checks

Run from the skill checkout:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
python3 scripts/run_codex_agent.py --help
python3 scripts/run_codex_agent.py run --role worker --effort max \
  --cwd . --prompt "Offline routing check only." --dry-run
python3 scripts/run_codex_agent.py run --role complex-worker \
  --cwd . --prompt "Offline finisher check only." --dry-run
```

These checks start no model, container or VM. They verify safe CLI construction,
exact effort selection, a fresh write-enabled finisher, packaged links and
numeric consistency. They do not establish model access or performance.

In a fresh host session, ask the skill to describe its route for a small coupled
fix, a substantial bounded verifiable unit, a tight deadline, and missing model
support. It should choose automatically without demanding a mode flag; it
should stay direct when delegation gates cannot be supported. A routing
description alone is not an executed workflow or a savings measurement.

Optional: `python3 scripts/run_codex_agent.py doctor --cwd .` exercises default
route plumbing but **starts paid model calls**. Obtain appropriate authority
and budget before running it. It does not test the Max lane or prove benchmark
quality, and is never an automatic installation prerequisite.

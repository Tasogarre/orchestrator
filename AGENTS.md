# Working on Orchestrator

This public repository is the canonical source of the portable skill. SKILL.md
owns behaviour; README.md explains use and value; docs/results.json owns the
published numeric projection. Keep all three aligned.

Use a topic branch and narrow commits. Preserve unrelated changes.
Run `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`
and helper dry runs before shipping. Tests are offline: do not launch paid
models, VMs, containers or a doctor run as an implicit contribution check.

Do not weaken acceptance, permission, isolation, model identity or cleanup
requirements to claim savings. Automatic routing is a model-applied policy,
not a guarantee that the host follows it or that a lower-cost route wins.

Publish only sanitised final insights. No secrets, personal paths, raw sessions,
private host conventions, credentials, private infrastructure URLs, or
intermediate experiment history. Use public-safe Git author identity and inspect
the exact staged file list and reachable history before pushing.

Performance claims must state workload/sample, model/effort, baseline finishing
parity, full arm-cost scope, cache/rate date and limitations. Never extrapolate
GPT-6 results to Claude or GPT-6.1 without a new paired study. Keep research
citations separate from locally measured results.

The aggregate token total is a deduplicated retained subtotal. Cached input
and reasoning output are subsets; do not add them again or call excluded usage
zero. Raw evidence is not bundled, so this summary is not a reproducible
benchmark distribution.

Future model-family studies are backlogged. Any new benchmark campaign needs
explicit task/budget authority, isolated grading, full accounting and cleanup.

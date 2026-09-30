<p align="center">
  <img src="assets/orchestrator.svg" alt="Orchestrator: choose the right owner, keep the quality gate" width="100%">
</p>

# Orchestrator

**Let the model choose when to work directly—and when a cheaper, coherent owner
with capable finishing is worth the handoff.**

An instruction skill for **Codex, Claude Code and OpenClaw**. It keeps intent,
planning and final acceptance with a capable model, delegates only when a useful
boundary exists, and judges the whole workflow—not just the worker's token bill.

[![Offline checks](https://github.com/Tasogarre/orchestrator/actions/workflows/validate.yml/badge.svg)](https://github.com/Tasogarre/orchestrator/actions/workflows/validate.yml)
[![Licence: MIT](https://img.shields.io/badge/Licence-MIT-167D71)](LICENSE)

[Install](#install) · [How it chooses](#how-it-chooses) ·
[Final evidence](#final-evidence) · [Lessons](#what-we-learned) ·
[Research](#research-behind-the-design) ·
[Limitations](#limitations-and-no-guarantees)

## The value, in one sentence

Use a capable model where judgement and acceptance matter; use a lower-cost
model where coherent, verifiable work can repay setup, finishing and repair.
Sometimes the most efficient orchestration decision is **not to delegate**.

There is no route mode for you to manage. Invoke the skill, describe the task,
and state any real deadline, budget or acceptance constraints.

### Start on a capable session model

**The model currently running your session makes the ownership decision.**
Start Orchestrator on a model you trust with planning, judgement and final
acceptance—not merely the cheapest model you intend to use as a worker.
For example, use a capable Sol-class session in Codex or an Opus-class session
in Claude Code, at a reasoning effort appropriate to the task. These are role
examples, not a claim that every model or effort has been benchmarked.

The starting model retains the goal, decides whether to work directly or
delegate, checks the result and owns final acceptance. If you change the main
session model, the model active at the decision point applies the policy.
The skill does not upgrade your session model or purchase a separate router
call. If that model cannot handle the required judgement, use a capable owner
before proceeding; delegating implementation does not fix a weak decision-maker.

## Final evidence

The most useful retained final tactic was **GPT-6 Luna Max implementation →
fresh GPT-6 Sol High finishing and repair**.

On two bounded workflow diagnostics, it achieved **30.7–34.8% lower
API-equivalent cost**, with equal final **100/100** scores against matched direct
controls. The tradeoff was **34.3–95.6% longer model-stage time**.

| Bounded task | Max + capable finishing | Direct + equal finishing | Cost saving | Model-stage time | Final quality, tactic / direct |
| --- | ---: | ---: | ---: | ---: | ---: |
| Instance defaults | $0.28281 | $0.43346 | 34.8% | 34.3% longer | 100 / 100 |
| Strict offset alignment | $0.21262 | $0.30672 | 30.7% | 95.6% longer | 100 / 100 |

**Scope matters:** these are two selected final coherent-workflow diagnostics,
not executions of the published automatic-routing skill text, not an overall
study effect, and not a guarantee of an Orchestrator-versus-direct win. The
policy's comparative performance remains unmeasured.

Both arms received the **same fresh Sol High finish-and-repair opportunity**,
then independent objective checks and blind quality scoring. Arm estimates
include routing, implementation/integration, repairs and finishing; shared case
preparation and independent grading are excluded. Time covers model stages only.
Costs use a frozen **2026-09-23** rate table and actual cache mix, not subscription
billing or a current-price quote. A direct run without equal finishing is a
different, unmeasured baseline.

[Methodology and final findings](references/evaluation.md) ·
[Machine-readable aggregate results](docs/results.json)

### What it took to learn this

**345,097,261 tokens across 426 deduplicated complete calls** were recorded in
the retained research/testing programme, including scenario preparation and
grading. The corresponding frozen-rate API-equivalent estimate is **$127.86**.
This is the programme's audited retained total—not the cost of using the skill
on one task.

| Recorded usage | Tokens |
| --- | ---: |
| Input | 341,131,707 |
| ↳ Cached input, already included above | 322,719,488 |
| ↳ Uncached input | 18,412,219 |
| Output | 3,965,554 |
| ↳ Reasoning output, already included above | 1,991,356 |
| **Total input + output** | **345,097,261** |

This total already includes the final study. It excludes the main conversation,
absent archives, incomplete receipts and unmetered engineering reviews, so it is
an auditable subtotal rather than an exact lifetime total. Cached and reasoning
tokens must not be added a second time. Raw traces and intermediate experiments
remain private; only final insights and aggregate figures are published here.

## How it chooses

Your current capable session model makes the routing decision **inline**,
without buying a separate router call or asking you to choose a mode. Worker
and finisher model selections do not change the parent session model.

```text
Task + acceptance + runtime capabilities
                    │
           Inline ownership decision
              ┌─────┴─────┐
              │           │
        Direct owner   One coherent cheaper owner
              │        at supported strong effort
              │           │
              │        Fresh capable finisher
              │        with scoped repair access
              └─────┬─────┘
                    │
          Objective + semantic checks
                    │
          Parent integration / acceptance
```

| Keep it direct | Use coherent Max + capable finishing |
| --- | --- |
| Small fix or strong warm-context advantage | Substantial, clearly bounded unit |
| Ambiguous task or exploratory debugging | Clear acceptance and owned paths |
| Tightly coupled work or sensitive decisions | Meaningful objective and compatibility checks |
| Handoff/repair cost likely outweighs savings | Plausible saving after the entire finishing loop |
| Tight deadline or unsupported model/effort | Supported runtime and acceptable added latency |

Every delegation gate must hold. If one does not, the skill stays direct and
briefly explains why. Direct execution can still receive a required independent
review; “direct” does not mean “skip quality checks”.

On the measured Codex family the eligible lane is **Luna Max + fresh Sol High
finishing**. Other families use their supported lower-cost strong owner and
capable finisher, not an invented universal “Max” parameter. Those mappings are
unmeasured; unsupported routes fall back to direct.

The finisher may **repair demonstrated defects within scope**, not merely
approve a patch. Writers run sequentially for a coherent unit. Required checks
run again after repairs, and the parent retains final acceptance. Numerical
study tolerances never override your actual requirements.

### Why is there a Python helper for Codex?

[`scripts/run_codex_agent.py`](scripts/run_codex_agent.py) is an **optional CLI
adapter, not the ownership decision-maker**. Use native agent tools first when
they support the required model, effort, fresh context and workspace boundary.
The helper provides a repeatable fallback through `codex exec` when needed.

After the session model selects a route, it supplies a bounded task to the
helper. The helper launches a fresh Codex child with the selected model,
reasoning effort, working directory and sandbox; disables nested delegation;
and returns the final answer, reported token usage, duration and errors as JSON.
It also handles timeouts/cancellation and rejects detected concurrent worktree
or output/log collisions. The sandbox does not itself enforce every owned-file
boundary: the parent still scopes, inspects and verifies the work.

It starts no background daemon, Docker container or VM, and does not change
your main model or profile. Child calls intentionally ignore global user
configuration, including global hooks and provider/profile preferences; use
native tools if those must apply. It uses Codex's existing authentication, not
a separate API client or embedded credential. Live calls consume your Codex
allowance or API usage; `--dry-run` starts no model and the optional
`doctor` starts live model calls. See [routing details](references/routing.md).

The doctrine does not require this helper in Claude Code or OpenClaw; those
hosts use their available, authorised native tools or supported adapters.

### Do I need a sandbox or the eval environment?

**You do not need our benchmark environment, Docker, Lima or a VM to use
Orchestrator.** Invoke the skill in your normal supported coding session. There
is no separate sandbox service to install and no benchmark to run first.

Two different kinds of protection appear in the documentation:

| Protection | Purpose | Needed for ordinary use? |
| --- | --- | --- |
| Your coding host's permissions and execution sandbox | Limit what an agent can read, write or execute while doing your real task. The optional Codex helper requests `read-only` for inspection roles and `workspace-write` for implementation roles by default. | Keep the host's appropriate protections; this is not a separate eval setup. |
| Separate, credential-free evaluation environments | Compare workflows on fresh task copies, keep withheld checks private and grade results independently without risking your working project. | No. This is for optional controlled studies. |

The helper's `--sandbox` option selects a **Codex execution policy**, not a
Docker container or a benchmark VM. Exact enforcement depends on the host and
platform; a sandbox is not proof that credentials are isolated or every
assigned file boundary is enforced. The parent must still respect your
authority, scope and verification requirements. Do not bypass protections
merely to make delegation work; use the direct route when a safe worker route
is unavailable.

For everyday work, normal tests and acceptance checks are enough—you do not
need to benchmark each task. If you want to measure savings on your own
workloads, use isolated task copies, equivalent finishing and independent
grading as described in [the evaluation methodology](references/evaluation.md).
That is an optional study, not an installation requirement; this repository
does not bundle the private eval harness or raw task evidence.

## Install

Requires a compatible skill-capable host. The optional Codex helper also needs
Python 3.10+ and an authenticated, compatible Codex CLI. Model availability is
account-dependent; the skill does not install credentials, change your global
model, add profiles or start background services.

Choose your host below. **If the destination already exists, stop and inspect it
instead of overwriting it.** For a shared multi-host installation, clone once
and link the other hosts' skill directories to it, only after checking for
existing installations.

### Codex

```bash
mkdir -p "$HOME/.agents/skills"
git clone https://github.com/Tasogarre/orchestrator.git \
  "$HOME/.agents/skills/orchestrator"
```

Then use:

```text
Use $orchestrator to implement this change. Preserve the existing API and tests.
```

### Claude Code

```bash
mkdir -p "$HOME/.claude/skills"
git clone https://github.com/Tasogarre/orchestrator.git \
  "$HOME/.claude/skills/orchestrator"
```

Then use `/orchestrator` with your task. This installs the doctrine; it does not
imply Claude performance has been benchmarked.

### OpenClaw

With a compatible version of its skills installer:

```bash
openclaw skills install git:Tasogarre/orchestrator@main --global
```

Use the skill in your task prompt. Honour your existing configured model routes
and agent allowlists. See [host adapters and official documentation](references/hosts.md).
For a reproducible install, replace `main` with a reviewed commit or release ref.

### Verify and update

From the cloned checkout:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
python3 scripts/run_codex_agent.py --help
```

These checks call **no model**. The optional helper's `doctor` command starts
live model calls that consume your Codex allowance or API usage; it is not
required for installation and is not run by CI.

For a Git clone with a clean working tree, `git pull --ff-only` updates the
skill; preserve local edits rather than forcing an update. OpenClaw Git installs
are refreshed through its documented reinstall flow. Existing sessions may
retain already-loaded instructions—start a fresh session for the new version.
A Codex `--profile` is separate configuration and is not changed by this skill.

## What we learned

The useful outcome was a narrower ownership policy, not a rule to always form a
team. These are final lessons from the retained testing programme, without a
run-by-run experiment history.

### Patterns that did not reliably pay off

| Pattern | Observation and likely reason | What the skill does instead |
| --- | --- | --- |
| Delegate first because the worker model is cheaper | Setup, repeated investigation, integration and finishing could cost more than direct delivery. Lower worker rates alone did not predict a lower accepted-delivery bill. | Decide ownership first and consider the complete workflow cost. |
| Split a small or tightly coupled change among several agents | More handoffs bought coordination overhead without enough independent work to repay it. A clean merge did not establish semantic compatibility. | Keep a coherent unit with one owner; parallelise genuinely independent research or isolated units. |
| Route to a cheap worker, then rely on capable review to rescue quality | Review sometimes missed defects or changed already-correct behaviour. A review label was not a reliable quality guarantee. | Give a fresh finisher scoped repair access, preserve green behaviour, and rerun acceptance checks after repairs. |
| Increase effort and assume quality becomes reliable | Stronger effort did not consistently rescue every workload. A precise contract and relevant compatibility checks remained necessary. | Use supported strong effort where justified, but keep task-specific verification as the acceptance gate. |
| Optimise token count in isolation | Different model rates and cache mixes meant more tokens could still cost less. | Account for uncached input, cached input and output at the actual rates; track quality and elapsed time separately. |

These observations do not establish that the patterns can never work. They
explain why this release does not make them blanket defaults.

### Promising, but not settled

- **One coherent Max owner plus capable finishing:** the strongest final
  price-sensitive tactic on the two published diagnostics, with a clear latency
  penalty. Broader task coverage and independent repeats are still needed.
- **Cheaper ownership at lower effort:** attractive cost or speed on some work,
  but quality was not consistent enough to make it the default coherent lane.
  Raising effort is a choice, not a replacement for verification.
- **Inline automatic routing:** avoids deliberately buying a separate router
  call and uses the capable session's existing context. The shipping policy's
  end-to-end savings and quality have not yet been measured.
- **Selective parallel research:** a useful candidate for independent,
  information-heavy questions; success on coding diagnostics does not quantify
  its benefit.
- **Cross-family portability:** the ownership/finishing framework can be applied
  in other harnesses. Claude and GPT-6.1 need their own matched solver studies
  before any quality, speed or savings claim.

The central lesson is **selective delegation with preserved acceptance**.
“Direct” is a legitimate outcome of orchestration—not evidence that the skill
failed to create enough agents.

## Research behind the design

The research informs the ownership policy; **it does not establish the numerical
GPT-6 savings above**.

- **Start simple.** Anthropic's [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
  describes choosing the simplest effective workflow and the cost/latency
  tradeoffs of additional agentic complexity. Here, that means direct-first
  unless delegation has a defensible benefit.
- **Task structure determines the architecture.** [Towards a Science of Scaling
  Agent Systems](https://arxiv.org/abs/2512.08296) studies how coordination,
  task topology and model capability interact. Our application is to select
  ownership boundaries before agent count or model tier.
- **Parallelism earns its place on independent work.** Anthropic's
  [multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)
  illustrates useful parallel research and the importance of explicit
  delegation briefs. Here, independent readers may be batched, while a coherent
  implementation unit keeps one owner and a sequential finisher.

The resulting principle: **optimise total accepted-delivery cost**, including
setup, integration, verification and repair—not tokens or the worker's price in
isolation.

## Limitations and no guarantees

**Results are not guaranteed and will vary** by workload, task, initiating model,
worker and finisher, harness, reasoning effort, available tools, context warmth,
cache reuse, provider pricing, latency and acceptance coverage.

- Evidence is primarily **GPT-6**. **Claude-family and GPT-6.1 solver evaluations
  are backlogged and unmeasured**, even when those models can use this skill.
- Two diagnostics are a small sample, not a statistical generalisation.
- Equal 100/100 scores mean the checked rubric matched; they do not prove the
  absence of every bug. Some broader dependency-based fixtures were unavailable.
- The automatic policy is model-applied instructions, not an enforced routing
  service. Host compliance and capability need verification.
- Raw private evidence is not distributed, so this summary is not a fully
  independently reproducible benchmark package.
- Cheaper can be slower; more tokens can still cost less. A capable finisher can
  miss or introduce defects, which is why final verification remains mandatory.

Use it where the boundary and checks make sense. Stay direct where they do not.

## Contributing

See [AGENTS.md](AGENTS.md) for contribution and evidence rules. CI runs only
offline package/runner checks. New comparative studies require explicit scope,
full accounting, independent quality checks and proper resource cleanup.

**Licence:** [MIT](LICENSE).

---
name: orchestrator
description: >-
  Automatically choose direct execution or a coherent lower-cost implementation
  owner with capable finishing. Use for multi-model task routing, planning,
  delegation, parallel research, and quality-gated delivery in Codex, Claude Code,
  or OpenClaw. Optimise whole-workflow cost without weakening task acceptance.
---

# Orchestrator

Choose ownership before choosing a model. A team is not the default answer.
The current capable session retains intent, planning, authority and final
acceptance. Lower-cost models are useful when their bounded work repays the
handoff, verification and repair cost.

The model currently running the main session is the ownership decision-maker.
Users should start on a model capable of planning, judgement and acceptance;
this skill does not upgrade that model or launch a separate router. Worker and
finisher model choices do not replace the main session model.

## Automatic route selection

When this skill is active, **you choose the route**. Do not ask the user to pick
direct versus Max, require a mode flag, or buy a separate routing-model call.
Make the decision inline using the task, current context, available runtime
capabilities and the user's priorities. Ask only for genuinely missing scope,
acceptance, budget or authority—not for a routing preference.

Default to quality first and lower full-workflow cost where justified. Respect
explicit speed, deadline, budget and model constraints. A slightly slower cheap
route may be worthwhile; never infer unlimited spending or silently relax
acceptance.

**Use direct-first** if the work is small, tightly coupled to the current warm
context, ambiguous, exploratory debugging, security/data/spend-sensitive, poorly
verifiable, or unlikely to repay another context plus capable finishing. Missing
runtime support or uncertain economics also favour direct. Direct means the
capable current session owns implementation; it may still use a bounded reader
or an independently required review. If the current model is insufficient,
request a supported capable owner rather than pretending routing creates ability.

**Automatically use one coherent Max owner plus capable finishing** when all
these conditions are supported by evidence:

1. The unit has a clear goal, acceptance contract and file/behaviour boundary.
   The owner can implement it coherently without repeated parent integration.
2. Objective checks plus meaningful semantic/compatibility coverage can judge
   success. A label such as “bounded” or a green test alone is insufficient.
3. The work is substantial enough that the cheaper owner is plausibly cheaper
   after context setup, routing, integration, verification, finishing and repairs.
   Use task-specific history or a qualitative judgement; do not invent a precise
   savings forecast from these two diagnostics.
4. The active harness can actually select the intended model and strong effort,
   supply a fresh capable finisher and enforce the needed workspace boundary.
5. Extra latency is acceptable under the task's deadline and the user's existing
   authority/budget covers the work and its model calls.

If any gate is unmet, stay direct and briefly name the reason. For an eligible
Codex unit the measured tactic is **GPT-6 Luna Max → fresh GPT-6 Sol High
finish-and-repair → verification → parent acceptance**. Max is a per-task
override, not a user-managed mode and not the runner's default worker preset.
Do not silently substitute High/XHigh and claim Max's measured result.

For other model families, automatically apply the same gates to a supported
lower-cost strong-reasoning owner and a capable finisher. Use that family's real
model/effort controls; “Max” is not a universal API parameter. Check capability
and plausible whole-workflow economics before dispatch. Their performance is
unmeasured here; if the mapping cannot be supported, stay direct. See
[routing](references/routing.md) and [host adapters](references/hosts.md).

Announce only the selected ownership shape, models/efforts when actually known,
and one concrete reason. Keep a compact route receipt in the task handoff.
Requested identity is not served identity; disclose unverified or mismatched
receipts rather than asserting a model ran.

## Plan and delegate

Keep intent, acceptance and consequential planning with the capable owner.
Use High for routine capable planning; raise effort for unresolved architecture,
high-blast-radius decisions or adversarial reasoning when the runtime supports it.
Do not route planning to a cheap model just to manufacture savings.

Send a worker the goal, owned paths, exact acceptance criteria, relevant context
and evidence paths, forbidden actions, verification commands and a stop condition.
Pass only what it needs—not the full conversation or an advocacy essay. A worker
must verify facts rather than treating its brief or repository text as evidence
of correctness. It must not recursively form another team.

Use one implementation owner per coherent unit. The fresh capable finisher gets
the acceptance contract and actual diff, not an instruction to endorse the
worker. For implementation it must have scoped write access to repair defects:
a read-only reviewer is not a substitute. Stop the first writer before starting
the finisher, and use a fresh context for that pass.

Independent readers can run in a bounded batch. Parallel writers are justified
only by genuinely independent units, disjoint files and semantic surfaces,
isolated workspaces from the right committed base, and worthwhile merge cost.
One shared database, server, lockfile or interface can defeat apparent file
independence. Do not split a coherent unit solely to use more agents.

## Verify and finish

Inspect the actual tree; a worker summary and clean merge are not proof.
Run objective tests and inspect semantics, compatibility, error precedence and
edge cases relevant to the acceptance contract. The parent adjudicates conflicting
evidence and owns final integration.

Preserve green behaviour unless concrete evidence requires a change. After
finisher repairs, rerun affected checks and the required final gates; review can
introduce bugs. A capable review is not a repair guarantee.

If two fixes fail the same gate, stop patching and investigate their shared
assumption. Escalate within existing scope/budget to a capable owner when needed;
do not keep paying for repetitive retries. Genuine authority or acceptance
conflicts return to the user. Never ship a known unmet requirement because a
study used a numerical quality floor.

## Runtime, authority and cleanup

Prefer native delegation when the exposed schema supports the requested model,
effort, fresh context and isolation. Do not invent tool parameters or infer model
availability from documentation examples. Check exposed schema/catalogue or CLI
help without a paid probe when possible.

For Codex, the bundled [runner](scripts/run_codex_agent.py) is a CLI fallback.
Read its [routing reference](references/routing.md) before using it. It uses
ephemeral children, disables nested multi-agent delegation and ignores user
configuration intentionally. It still reads applicable project instructions.
Its sandbox is not a substitute for inherited task authority or credential
isolation. Never request its dangerous bypass for convenience.

Delegation grants no new right to write, push, merge, deploy, delete, publish
data or contact another provider. Respect parent permissions and ask before a
new external recipient where the user's authority does not cover it.

Use existing environments when safe. Creating containers or VMs is not required
by this skill. If task-scoped resources are authorised, record exact ownership
and clean them up after verified evidence is retained; stop reusable resources
when finished. Never delete shared/pre-existing resources on an inferred mandate.

## Evidence and checks

The [final findings](references/evaluation.md) support a bounded GPT-6 tactic,
not guaranteed savings or measured proof of this automatic policy. Results vary
with task, initiating model, context, harness, cache mix and acceptance coverage.
Claude and GPT-6.1 solver performance remain backlogged.

Use [offline acceptance checks](references/acceptance-test.md) for installation.
The runner's doctor starts paid model calls and is not an automatic prerequisite.

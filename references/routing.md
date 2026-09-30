# Model and execution routing

Select the ownership shape in the current session before paying for another
context. The SKILL's automatic gates govern execution; this table describes the
bundled Codex helper, not a requirement to instantiate every role.

| Role | Default model | Effort | Access |
| --- | --- | --- | --- |
| explorer | GPT-6 Luna | Low | Read-only |
| probe | GPT-6 Luna | Medium | Read-only |
| worker | GPT-6 Luna | High | Workspace-write |
| worker-high | GPT-6 Luna | XHigh | Workspace-write |
| complex-worker | GPT-6 Sol | High | Workspace-write |
| reviewer | GPT-6 Sol | High | Read-only |
| critical-reviewer | GPT-6 Sol | XHigh | Read-only |
| advisor | GPT-6 Sol | High | Read-only |

Model IDs are defaults from the measured family, not guaranteed account
availability. The automatic coherent implementation tactic explicitly overrides
`worker` effort to `max` and uses `complex-worker` for capable finishing.
The latter is write-enabled; `reviewer` is not a finish-and-repair role.
No preset changes your session model or global Codex profile.

## Native first, CLI fallback

Use a native agent mechanism only when its exposed schema supports the required
model, effort, fresh context and workspace boundary. A same-model child is not
a multi-model saving. Confirm isolation rather than assuming a subagent has it.
The native child brief prohibits nested delegation and unowned writes.

If needed, use the helper installed alongside SKILL.md. Resolve its absolute path
from the actual installation—not the project working directory. Python 3.10+
and a compatible Codex CLI are required; model support depends on the account.
CLI execution was used with Codex 0.155.1 in the diagnostics.

The helper constructs ephemeral `codex exec` calls, ignores user configuration,
disables multi-agent children, uses the specified sandbox and records JSON output.
An ignored global config includes global hooks and provider/profile preferences;
use native tools if those are necessary. Review its `--help` before launch.

These **dry-run examples do not call a model**. Replace `/path/to/orchestrator`
with the real skill path and supply the project's actual acceptance brief.

```bash
python3 /path/to/orchestrator/scripts/run_codex_agent.py run \
  --role worker --effort max --cwd . \
  --prompt "Implement this one bounded unit; verify its acceptance contract." \
  --dry-run

python3 /path/to/orchestrator/scripts/run_codex_agent.py run \
  --role complex-worker --cwd . \
  --prompt "Independently inspect the actual diff against the acceptance contract, repair demonstrated defects within scope, then rerun its checks." \
  --dry-run
```

Remove `--dry-run` only for authorised work. These are **sequential stages** in
the same assigned isolated worktree, not two concurrent writers. Provide both
real briefs with owned paths, baseline, checks, forbidden actions and stop rules.
The fresh finisher sees actual files/diff and requirements, not hidden grading
answers or the worker's endorsement narrative.

Other supported per-call options include `--model`, `--effort`, `--timeout`,
`--prompt-file` and `--log-dir`. Logs and task prompts can contain private
data: keep them outside the public repository. Use `--help` for the full syntax.

The optional environment variables `CODEX_ORCHESTRATOR_SOL_MODEL` and
`CODEX_ORCHESTRATOR_LUNA_MODEL` replace helper model defaults. They do not prove
capability or make unmeasured models inherit the GPT-6 results. Do not send task
data to a new provider without authority.

## Other families

Retain capable intent/planning/acceptance. Where available, select a meaningfully
cheaper coherent owner at a supported strong effort and a fresh capable finisher.
For Claude Code, use the actual native Agent model/effort schema or a documented
authorised CLI route—not Codex flags or invented GPT-to-Claude effort equivalence.
For OpenClaw, use configured allowed agent/model routes and real tool schemas.
Capability and total economics must satisfy the same automatic gates.

High is not universally sufficient; XHigh/Max is not universally more efficient.
Treat unsupported effort or uncertain mapping as a reason for direct execution,
not an invitation to silently substitute. Claude and GPT-6.1 require future
paired solver evaluations before numerical claims.

## Minimal receipt

Report selected shape, rationale, requested/served model and effort (or
unverified identity), owned unit, actual verification outcome, repair status and
resource cleanup. Include whole-workflow usage/cost only when real receipts make
it possible. Cached input is a subset of input, reasoning output a subset of
output—never count either twice.

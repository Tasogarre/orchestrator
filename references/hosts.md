# Harness adapters

This is a portable instruction skill, not a router daemon, universal agent API,
or model-profile installer. Installation makes the doctrine available; the host
model must apply it while the skill is active. Native model selection and
permission enforcement vary by harness and account.

## Codex

Install as a directory containing SKILL.md under `$HOME/.agents/skills`, or
the repository's `.agents/skills`. Invoke `$orchestrator` in the task prompt.
Use the actual exposed agent tool for supported native model overrides. Do not
guess effort or isolation arguments. The bundled CLI helper is a fallback when
the native tool cannot express the route; it does not alter global settings.

Updating the skill does not update a Codex `--profile` entry. A profile chooses
configuration; the skill chooses task ownership within that configuration.
Do not add or change a global profile as an implicit installation step.

## Claude Code

Install under `$HOME/.claude/skills/orchestrator` or
`.claude/skills/orchestrator`, then invoke `/orchestrator`.
Use the native Agent mechanism's currently supported model and effort controls.
Choose a supported lower-cost strong owner and capable fresh finisher only when
the gates justify it; otherwise stay direct. No fixed GPT-to-Claude tier mapping
is assumed and no Claude cost/quality win is claimed.

## OpenClaw

Install through OpenClaw's skills mechanism or in its configured skill directory.
Use its available agent/delegation tools and configured allowlists. A model ID
alone does not establish a callable agent, access to credentials, or permission
to spawn a child. Respect the host's existing provider and routing authority.
When the exact required lower-cost/finisher route is unavailable, stay direct.

For all hosts, a new user or machine needs the relevant CLI/harness, model access
and credentials established separately. No credentials, personal workspace
paths, custom agent identities or user-specific config are bundled here.

Official installation references:

- [Codex skills](https://learn.chatgpt.com/docs/build-skills)
- [Claude Code skills](https://code.claude.com/docs/en/skills)
- [OpenClaw skills](https://docs.openclaw.ai/tools/skills)

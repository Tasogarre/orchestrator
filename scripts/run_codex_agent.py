#!/usr/bin/env python3
"""Run isolated Codex model routes with compact, machine-readable results."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from typing import Any


SOL_MODEL = os.environ.get("CODEX_ORCHESTRATOR_SOL_MODEL", "gpt-6-sol")
LUNA_MODEL = os.environ.get("CODEX_ORCHESTRATOR_LUNA_MODEL", "gpt-6-luna")


@dataclass(frozen=True)
class Preset:
    model: str
    effort: str
    sandbox: str
    verbosity: str


PRESETS: dict[str, Preset] = {
    "explorer": Preset(LUNA_MODEL, "low", "read-only", "low"),
    "probe": Preset(LUNA_MODEL, "medium", "read-only", "low"),
    "worker": Preset(LUNA_MODEL, "high", "workspace-write", "low"),
    "worker-high": Preset(LUNA_MODEL, "xhigh", "workspace-write", "low"),
    "complex-worker": Preset(SOL_MODEL, "high", "workspace-write", "low"),
    "reviewer": Preset(SOL_MODEL, "high", "read-only", "low"),
    "critical-reviewer": Preset(SOL_MODEL, "xhigh", "read-only", "low"),
    "advisor": Preset(SOL_MODEL, "high", "read-only", "low"),
}

DOCTOR_ROLES = (
    "explorer", "probe", "worker", "worker-high", "reviewer", "critical-reviewer"
)

ROLE_GUIDANCE = {
    "explorer": (
        "Explore only. Map the requested facts and execution paths with exact file and "
        "symbol anchors. Do not edit files or expand into solution design."
    ),
    "probe": (
        "Verify the named premise independently. Seek disconfirming evidence, do not edit "
        "files, and return a clear supported/unsupported/uncertain conclusion."
    ),
    "worker": (
        "Implement only the assigned bounded scope. Preserve unrelated changes, do not "
        "revert other work, and run the narrowest relevant gates."
    ),
    "worker-high": (
        "Implement the assigned scope thoroughly. Trace relevant edge cases, preserve "
        "unrelated changes, and run the narrowest relevant gates."
    ),
    "complex-worker": (
        "Own the assigned complex implementation while staying inside its explicit boundary. "
        "Prioritize correctness, safety, and integration evidence over breadth."
    ),
    "reviewer": (
        "Review independently and do not edit files. Lead with concrete correctness, behavior, "
        "security, or missing-test findings; omit style-only commentary."
    ),
    "critical-reviewer": (
        "Perform an adversarial, independent review and do not edit files. Trace assumptions "
        "across boundaries and prioritize exploitable, corrupting, costly, or contract-breaking defects."
    ),
    "advisor": (
        "Answer the bounded decision requested. Analyze the supplied evidence, state the "
        "recommended choice and decisive tradeoff, and avoid taking over execution."
    ),
}

COMMON_GUIDANCE = """
You are an isolated routed Codex execution reporting to a frontier orchestrator.
Read every applicable AGENTS.md before acting. Work only in the supplied working directory.
Do not spawn subagents, delegate, or start another Codex process.
Return compact conclusions rather than raw logs. Unless the task explicitly needs another shape,
keep the final response under 300 words and include: Result; Evidence with file:line anchors or
commands plus exit codes; Changed files (or None); Open risks/blockers. Never claim a gate passed
without running it. If blocked, report the exact blocker and the strongest evidence obtained.
""".strip()

ALLOWED_EFFORTS = {"none", "minimal", "low", "medium", "high", "xhigh", "max"}
ALLOWED_SANDBOXES = {"read-only", "workspace-write", "danger-full-access"}
SAFE_TASK_ID = re.compile(r"^[A-Za-z0-9._-]+$")


@dataclass
class Task:
    task_id: str
    role: str
    cwd: str
    prompt: str
    model: str
    effort: str
    sandbox: str
    verbosity: str
    timeout: int
    yolo: bool
    output: str | None = None
    log: str | None = None


def toml_string(value: str) -> str:
    return json.dumps(value)


def read_prompt(prompt: str | None, prompt_file: str | None) -> str:
    if bool(prompt) == bool(prompt_file):
        raise ValueError("provide exactly one of prompt or prompt_file")
    if prompt_file:
        path = Path(prompt_file).expanduser().resolve()
        if not path.is_file():
            raise ValueError(f"prompt file does not exist: {path}")
        return path.read_text(encoding="utf-8")
    assert prompt is not None
    return prompt


def resolve_task(raw: dict[str, Any], default_timeout: int = 1800) -> Task:
    role = str(raw.get("role", "")).strip()
    if role not in PRESETS:
        raise ValueError(f"unknown role {role!r}; choose from {', '.join(PRESETS)}")
    preset = PRESETS[role]
    cwd = Path(str(raw.get("cwd", ""))).expanduser().resolve()
    if not cwd.is_dir():
        raise ValueError(f"working directory does not exist: {cwd}")
    effort = str(raw.get("effort") or preset.effort)
    if effort not in ALLOWED_EFFORTS:
        raise ValueError(f"unsupported reasoning effort: {effort}")
    sandbox = str(raw.get("sandbox") or preset.sandbox)
    if sandbox not in ALLOWED_SANDBOXES:
        raise ValueError(f"unsupported sandbox: {sandbox}")
    yolo = bool(raw.get("yolo", False))
    if sandbox == "danger-full-access" and not yolo:
        raise ValueError("danger-full-access requires the explicit yolo flag")
    timeout = int(raw.get("timeout") or default_timeout)
    if timeout < 1:
        raise ValueError("timeout must be a positive number of seconds")
    task_id = str(raw.get("id") or raw.get("task_id") or role)
    if not SAFE_TASK_ID.fullmatch(task_id):
        raise ValueError(
            f"unsafe task id {task_id!r}; use only letters, digits, dot, underscore, or hyphen"
        )
    return Task(
        task_id=task_id,
        role=role,
        cwd=str(cwd),
        prompt=read_prompt(raw.get("prompt"), raw.get("prompt_file")),
        model=str(raw.get("model") or preset.model),
        effort=effort,
        sandbox=sandbox,
        verbosity=str(raw.get("verbosity") or preset.verbosity),
        timeout=timeout,
        yolo=yolo,
        output=str(Path(raw["output"]).expanduser().resolve()) if raw.get("output") else None,
        log=str(Path(raw["log"]).expanduser().resolve()) if raw.get("log") else None,
    )


def full_prompt(task: Task) -> str:
    return (
        f"{COMMON_GUIDANCE}\n\nRole instructions:\n{ROLE_GUIDANCE[task.role]}"
        f"\n\nAssigned task:\n{task.prompt.strip()}\n"
    )


def command_for(task: Task, output_path: str) -> list[str]:
    command = [
        "codex",
        "exec",
        "--ephemeral",
        "--ignore-user-config",
        "--skip-git-repo-check",
        "--disable",
        "multi_agent",
        "-C",
        task.cwd,
        "-m",
        task.model,
        "-c",
        f"model_reasoning_effort={toml_string(task.effort)}",
        "-c",
        f"model_verbosity={toml_string(task.verbosity)}",
        "--json",
        "-o",
        output_path,
    ]
    if task.yolo:
        command.append("--dangerously-bypass-approvals-and-sandbox")
    else:
        command.extend(
            [
                "-s",
                task.sandbox,
                "-c",
                'approval_policy="never"',
            ]
        )
    command.append("-")
    return command


def parse_events(stdout: str) -> tuple[str | None, dict[str, Any] | None, list[str], int]:
    thread_id: str | None = None
    usage: dict[str, Any] | None = None
    errors: list[str] = []
    commands = 0
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "thread.started":
            thread_id = event.get("thread_id")
        if event.get("type") == "turn.completed":
            usage = event.get("usage")
        if event.get("type") == "error":
            errors.append(str(event.get("message", "unknown Codex error")))
        item = event.get("item") or {}
        if item.get("type") == "command_execution" and event.get("type") == "item.completed":
            commands += 1
        if item.get("type") == "error":
            errors.append(str(item.get("message", "unknown Codex item error")))
    return thread_id, usage, errors[-5:], commands


def write_log(path: str, command: list[str], stdout: str, stderr: str) -> None:
    log_path = Path(path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "command": command,
        "stdout": stdout,
        "stderr": stderr,
    }
    log_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


class ChildProcesses:
    """Own only this invocation's children; cancellation prevents new launches."""

    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.cancelled = False
        self.active: set[subprocess.Popen] = set()

    def start(self, command: list[str]) -> subprocess.Popen:
        with self.lock:
            if self.cancelled:
                raise RuntimeError("route cancelled before launch")
            process = subprocess.Popen(
                command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, text=True, start_new_session=True,
            )
            self.active.add(process)
            return process

    def release(self, process: subprocess.Popen) -> None:
        with self.lock:
            self.active.discard(process)

    def cancel(self) -> None:
        with self.lock:
            self.cancelled = True
            processes = list(self.active)
        for process in processes:
            signal_group(process, signal.SIGTERM)
        deadline = time.monotonic() + 5
        for process in processes:
            try:
                process.wait(timeout=max(0.001, deadline - time.monotonic()))
            except subprocess.TimeoutExpired:
                signal_group(process, signal.SIGKILL)
                process.wait(timeout=5)
            else:
                # A reaped leader does not imply its command descendants exited.
                signal_group(process, signal.SIGKILL)


def signal_group(process: subprocess.Popen, sig: int) -> None:
    try:
        os.killpg(process.pid, sig)
    except ProcessLookupError:
        pass  # The invocation's group has already exited.


def execute(task: Task, dry_run: bool = False,
            children: ChildProcesses | None = None) -> dict[str, Any]:
    reject_artifact_collisions([task], 1)
    temporary_output = task.output is None
    if temporary_output:
        handle = tempfile.NamedTemporaryFile(prefix="codex-route-", suffix=".txt", delete=False)
        output_path = handle.name
        handle.close()
    else:
        output_path = task.output or ""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    try:
        return execute_with_output(task, output_path, dry_run,
                                   children or ChildProcesses())
    finally:
        if temporary_output:
            Path(output_path).unlink(missing_ok=True)


def execute_with_output(task: Task, output_path: str, dry_run: bool,
                        children: ChildProcesses) -> dict[str, Any]:
    command = command_for(task, output_path)
    if dry_run:
        return {
            "status": "dry-run",
            "task_id": task.task_id,
            "role": task.role,
            "model": task.model,
            "effort": task.effort,
            "sandbox": "danger-full-access" if task.yolo else task.sandbox,
            "cwd": task.cwd,
            "command": command,
        }

    started = time.monotonic()
    stdout = ""
    stderr = ""
    exit_code = 1
    timed_out = False
    process = children.start(command)
    try:
        try:
            stdout, stderr = process.communicate(full_prompt(task), timeout=task.timeout)
            exit_code = int(process.returncode or 0)
        except subprocess.TimeoutExpired:
            timed_out = True
            signal_group(process, signal.SIGTERM)
            try:
                stdout, stderr = process.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                signal_group(process, signal.SIGKILL)
                stdout, stderr = process.communicate(timeout=5)
            else:
                signal_group(process, signal.SIGKILL)
            exit_code = 124
    except BaseException:
        children.cancel()
        raise
    finally:
        children.release(process)

    duration = round(time.monotonic() - started, 3)
    final = ""
    try:
        final = Path(output_path).read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        pass
    thread_id, usage, errors, command_count = parse_events(stdout)
    if timed_out:
        errors.append(f"timed out after {task.timeout} seconds")
    if exit_code != 0 and not errors:
        errors.append(stderr.strip()[-2000:] or f"Codex exited with status {exit_code}")
    warnings: list[str] = []
    if task.log:
        try:
            write_log(task.log, command, stdout, stderr)
        except OSError as exc:
            warnings.append(f"log write failed: {exc}")

    status = "ok" if exit_code == 0 and bool(final) and not timed_out and not errors else "error"
    return {
        "status": status,
        "task_id": task.task_id,
        "role": task.role,
        "model": task.model,
        "effort": task.effort,
        "sandbox": "danger-full-access" if task.yolo else task.sandbox,
        "cwd": task.cwd,
        "exit_code": exit_code,
        "duration_seconds": duration,
        "thread_id": thread_id,
        "command_count": command_count,
        "usage": usage,
        "final": final,
        "errors": errors,
        "warnings": warnings,
        "output": task.output,
        "log": task.log,
    }


def write_identity(task: Task) -> str:
    if not task.yolo and task.sandbox == "read-only":
        return ""
    probe = subprocess.run(
        ["git", "-C", task.cwd, "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"},
        check=False,
    )
    if probe.returncode == 0:
        return str(Path(probe.stdout.strip()).resolve())
    return str(Path(task.cwd).resolve())


def reject_write_collisions(tasks: list[Task], max_concurrency: int) -> None:
    if max_concurrency <= 1:
        return
    seen: dict[str, str] = {}
    for task in tasks:
        identity = write_identity(task)
        if not identity:
            continue
        if identity in seen:
            raise ValueError(
                "parallel write collision: tasks "
                f"{seen[identity]!r} and {task.task_id!r} resolve to the same worktree {identity}"
            )
        seen[identity] = task.task_id


def reject_artifact_collisions(tasks: list[Task], max_concurrency: int) -> None:
    seen: dict[str, str] = {}
    for task in tasks:
        owned: set[str] = set()
        for path in (task.output, task.log):
            if path is None:
                continue
            identity = str(Path(path).expanduser().resolve())
            if identity in owned or (max_concurrency > 1 and identity in seen):
                raise ValueError(f"output/log collision for task {task.task_id!r}: {identity}")
            owned.add(identity)
            seen[identity] = task.task_id


def load_batch(path: str, timeout: int, log_dir: str | None) -> list[Task]:
    spec_path = Path(path).expanduser().resolve()
    payload = json.loads(spec_path.read_text(encoding="utf-8"))
    rows = payload.get("tasks") if isinstance(payload, dict) else payload
    if not isinstance(rows, list) or not rows:
        raise ValueError("batch spec must contain a non-empty task array")
    tasks: list[Task] = []
    ids: set[str] = set()
    for index, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            raise ValueError(f"batch task {index} is not an object")
        normalized = dict(row)
        normalized.setdefault("id", f"task_{index}")
        if log_dir and not normalized.get("log"):
            normalized["log"] = str(Path(log_dir).expanduser().resolve() / f"{normalized['id']}.json")
        task = resolve_task(normalized, timeout)
        if task.task_id in ids:
            raise ValueError(f"duplicate batch task id: {task.task_id}")
        ids.add(task.task_id)
        tasks.append(task)
    return tasks


def print_json(payload: Any) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def run_command(args: argparse.Namespace) -> int:
    task = resolve_task(vars(args), args.timeout)
    result = execute(task, args.dry_run)
    print_json(result)
    return 0 if result["status"] in {"ok", "dry-run"} else 1


def batch_command(args: argparse.Namespace) -> int:
    tasks = load_batch(args.spec, args.timeout, args.log_dir)
    if any(task.yolo for task in tasks) and not args.allow_yolo:
        raise ValueError("batch contains an unsandboxed task; rerun with --allow-yolo only after explicit user authorization")
    max_concurrency = max(1, min(args.max_concurrency, len(tasks)))
    reject_write_collisions(tasks, max_concurrency)
    reject_artifact_collisions(tasks, max_concurrency)
    if args.dry_run:
        results = [execute(task, True) for task in tasks]
    else:
        results_by_id: dict[str, dict[str, Any]] = {}
        children = ChildProcesses()
        with ThreadPoolExecutor(max_workers=max_concurrency) as executor:
            futures = {}
            try:
                futures = {executor.submit(execute, task, False, children): task.task_id
                           for task in tasks}
                for future in as_completed(futures):
                    task_id = futures[future]
                    try:
                        results_by_id[task_id] = future.result()
                    except Exception as exc:  # preserve the rest of a fan-out on one error
                        results_by_id[task_id] = {
                            "status": "error", "task_id": task_id,
                            "errors": [f"runner exception: {exc}"],
                        }
            except BaseException:
                children.cancel()
                for future in futures:
                    future.cancel()
                raise
        results = [results_by_id[task.task_id] for task in tasks]
    payload = {
        "status": "ok" if all(result["status"] in {"ok", "dry-run"} for result in results) else "error",
        "max_concurrency": max_concurrency,
        "results": results,
    }
    print_json(payload)
    return 0 if payload["status"] == "ok" else 1


def doctor_command(args: argparse.Namespace) -> int:
    cwd = str(Path(args.cwd).expanduser().resolve())
    roles = list(DOCTOR_ROLES)
    tasks = [
        resolve_task(
            {
                "id": f"doctor_{role}",
                "role": role,
                "cwd": cwd,
                "sandbox": "read-only",
                "timeout": args.timeout,
                "prompt": (
                    "Use the shell to run pwd and verify that the reported path is the current "
                    f"working directory. Do not modify files. End the final response with ROUTE_OK:{role}."
                ),
            },
            args.timeout,
        )
        for role in roles
    ]
    results: list[dict[str, Any]] = []
    children = ChildProcesses()
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {}
        try:
            futures = {executor.submit(execute, task, False, children): task.role
                       for task in tasks}
            for future in as_completed(futures):
                results.append(future.result())
        except BaseException:
            children.cancel()
            for future in futures:
                future.cancel()
            raise
    results.sort(key=lambda result: roles.index(result["role"]))
    passed = all(
        result["status"] == "ok" and f"ROUTE_OK:{result['role']}" in result["final"]
        for result in results
    )
    payload = {"status": "ok" if passed else "error", "routes": results}
    print_json(payload)
    return 0 if passed else 1


def add_task_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--role", required=True, choices=PRESETS.keys())
    parser.add_argument("--cwd", required=True)
    prompts = parser.add_mutually_exclusive_group(required=True)
    prompts.add_argument("--prompt")
    prompts.add_argument("--prompt-file")
    parser.add_argument("--id", default=None)
    parser.add_argument("--model")
    parser.add_argument("--effort", choices=sorted(ALLOWED_EFFORTS))
    parser.add_argument("--sandbox", choices=sorted(ALLOWED_SANDBOXES))
    parser.add_argument("--verbosity", choices=["low", "medium", "high"])
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument("--output")
    parser.add_argument("--log")
    parser.add_argument("--yolo", action="store_true")
    parser.add_argument("--dry-run", action="store_true")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="run one routed Codex execution")
    add_task_arguments(run_parser)
    run_parser.set_defaults(handler=run_command)

    batch_parser = subparsers.add_parser("batch", help="run independent routes concurrently")
    batch_parser.add_argument("--spec", required=True)
    batch_parser.add_argument("--max-concurrency", type=int, default=3)
    batch_parser.add_argument("--timeout", type=int, default=1800)
    batch_parser.add_argument("--log-dir")
    batch_parser.add_argument("--allow-yolo", action="store_true")
    batch_parser.add_argument("--dry-run", action="store_true")
    batch_parser.set_defaults(handler=batch_command)

    doctor_parser = subparsers.add_parser("doctor", help="live-test all model/effort tiers")
    doctor_parser.add_argument("--cwd", required=True)
    doctor_parser.add_argument("--timeout", type=int, default=300)
    doctor_parser.set_defaults(handler=doctor_command)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return int(args.handler(args))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print_json({"status": "error", "errors": [str(exc)]})
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

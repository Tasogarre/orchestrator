"""Offline contracts for the bundled Codex runner; no model calls."""

from pathlib import Path
import argparse
import importlib
import os
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch


RUNNER_DIR = Path(__file__).resolve().parents[1] / "scripts"
with patch.object(sys, "path", [str(RUNNER_DIR), *sys.path]), \
     patch.object(sys, "dont_write_bytecode", True):
    import run_codex_agent as runner  # noqa: E402


class OrchestratorRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._clean_env = patch.dict(os.environ, {}, clear=True)
        cls._clean_env.start()
        with patch.object(sys, "path", [str(RUNNER_DIR), *sys.path]), \
             patch.object(sys, "dont_write_bytecode", True):
            importlib.reload(runner)

    @classmethod
    def tearDownClass(cls):
        cls._clean_env.stop()
        with patch.object(sys, "path", [str(RUNNER_DIR), *sys.path]), \
             patch.object(sys, "dont_write_bytecode", True):
            importlib.reload(runner)

    def test_quality_first_role_defaults(self):
        expected = {
            "explorer": ("gpt-6-luna", "low", "read-only"),
            "probe": ("gpt-6-luna", "medium", "read-only"),
            "worker": ("gpt-6-luna", "high", "workspace-write"),
            "worker-high": ("gpt-6-luna", "xhigh", "workspace-write"),
            "complex-worker": ("gpt-6-sol", "high", "workspace-write"),
            "reviewer": ("gpt-6-sol", "high", "read-only"),
            "critical-reviewer": ("gpt-6-sol", "xhigh", "read-only"),
            "advisor": ("gpt-6-sol", "high", "read-only"),
        }
        self.assertEqual(
            {role: (preset.model, preset.effort, preset.sandbox)
             for role, preset in runner.PRESETS.items()},
            expected,
        )

    def test_doctor_covers_each_configured_model_effort_tier(self):
        self.assertEqual(
            runner.DOCTOR_ROLES,
            ("explorer", "probe", "worker", "worker-high", "reviewer", "critical-reviewer"),
        )
        self.assertEqual(
            {(runner.PRESETS[role].model, runner.PRESETS[role].effort)
             for role in runner.DOCTOR_ROLES},
            {(preset.model, preset.effort) for preset in runner.PRESETS.values()},
        )

    def test_task_override_and_safe_command(self):
        task = runner.resolve_task({
            "role": "worker",
            "cwd": str(Path(__file__).resolve().parents[1]),
            "prompt": "Make the bounded change.",
            "model": "gpt-6-sol",
            "effort": "medium",
        })
        self.assertEqual((task.model, task.effort), ("gpt-6-sol", "medium"))
        command = runner.command_for(task, "/tmp/codex-route-test-output.txt")
        self.assertEqual(command[command.index("-m") + 1], "gpt-6-sol")
        self.assertIn('model_reasoning_effort="medium"', command)
        self.assertEqual(command[command.index("-s") + 1], "workspace-write")
        self.assertIn('approval_policy="never"', command)
        self.assertNotIn("--dangerously-bypass-approvals-and-sandbox", command)

    def test_probe_remains_read_only(self):
        task = runner.resolve_task({
            "role": "probe",
            "cwd": str(Path(__file__).resolve().parents[1]),
            "prompt": "Check the premise.",
        })
        command = runner.command_for(task, "/tmp/codex-route-test-output.txt")
        self.assertEqual((task.model, task.effort), ("gpt-6-luna", "medium"))
        self.assertEqual(command[command.index("-s") + 1], "read-only")

    def test_finisher_is_fresh_write_enabled_and_capable(self):
        task = runner.resolve_task({
            "role": "complex-worker",
            "cwd": str(Path(__file__).resolve().parents[1]),
            "prompt": "Repair only demonstrated defects; rerun acceptance checks.",
        })
        command = runner.command_for(task, "/tmp/codex-finisher-contract.txt")
        self.assertEqual((task.model, task.effort), ("gpt-6-sol", "high"))
        self.assertEqual(command[command.index("-s") + 1], "workspace-write")
        self.assertIn("--ephemeral", command)
        self.assertIn("--ignore-user-config", command)
        self.assertIn("multi_agent", command)
        self.assertNotIn("--dangerously-bypass-approvals-and-sandbox", command)

    def test_max_override_preserves_worker_model_and_sandbox(self):
        task = runner.resolve_task({
            "role": "worker", "effort": "max",
            "cwd": str(Path(__file__).resolve().parents[1]),
            "prompt": "Implement the bounded unit.",
        })
        command = runner.command_for(task, "/tmp/codex-max-route-test-output.txt")
        self.assertEqual(command[command.index("-m") + 1], "gpt-6-luna")
        self.assertIn('model_reasoning_effort="max"', command)
        self.assertEqual(command[command.index("-s") + 1], "workspace-write")
        self.assertIn('approval_policy="never"', command)
        self.assertNotIn("--dangerously-bypass-approvals-and-sandbox", command)

    def task(self, role="worker", **overrides):
        return runner.resolve_task({
            "role": role, "cwd": str(RUNNER_DIR.parent),
            "prompt": "Offline test only.", **overrides,
        })

    def test_parallel_writers_share_git_identity_and_are_rejected(self):
        with tempfile.TemporaryDirectory(prefix="orchestrator-guard-test-") as folder:
            root = Path(folder)
            child = root / "child"
            child.mkdir()
            subprocess.run(["git", "init", "--quiet", str(root)], check=True)
            tasks = [self.task(id="one", cwd=str(root)),
                     self.task(id="two", cwd=str(child))]
            with self.assertRaisesRegex(ValueError, "parallel write collision"):
                runner.reject_write_collisions(tasks, 2)
            runner.reject_write_collisions(tasks, 1)
            runner.reject_write_collisions([self.task("probe"), self.task()], 2)
            with patch.object(runner, "write_identity", side_effect=["tree-one", "tree-two"]):
                runner.reject_write_collisions(tasks, 2)

    def test_batch_unsandboxed_opt_in_is_required(self):
        args = argparse.Namespace(spec="unused", timeout=1, log_dir=None,
                                  allow_yolo=False, max_concurrency=1, dry_run=True)
        task = self.task(yolo=True)
        with patch.object(runner, "load_batch", return_value=[task]), \
             patch.object(runner, "execute", return_value={"status": "dry-run"}) as execute, \
             patch.object(runner, "print_json"):
            with self.assertRaisesRegex(ValueError, "unsandboxed task"):
                runner.batch_command(args)
            execute.assert_not_called()
            args.allow_yolo = True
            self.assertEqual(runner.batch_command(args), 0)
            execute.assert_called_once_with(task, True)

    def test_dangerous_sandbox_requires_explicit_yolo(self):
        with self.assertRaises(ValueError):
            self.task(sandbox="danger-full-access")

    def test_shared_batch_artifacts_reject_read_only_tasks_before_execution(self):
        tasks = [self.task("probe", id="one", output="/tmp/route-shared.txt"),
                 self.task("probe", id="two", output="/tmp/route-shared.txt")]
        args = argparse.Namespace(spec="unused", timeout=1, log_dir=None,
                                  allow_yolo=False, max_concurrency=2, dry_run=False)
        with patch.object(runner, "load_batch", return_value=tasks), \
             patch.object(runner.subprocess, "Popen") as popen:
            with self.assertRaisesRegex(ValueError, "output/log collision"):
                runner.batch_command(args)
            popen.assert_not_called()
        runner.reject_artifact_collisions(tasks, 1)
        with self.assertRaisesRegex(ValueError, "output/log collision"):
            runner.reject_artifact_collisions([
                self.task(output="/tmp/route-shared.txt", log="/tmp/route-shared.txt")
            ], 1)
        with self.assertRaisesRegex(ValueError, "output/log collision"):
            runner.reject_artifact_collisions([
                tasks[0], self.task("probe", log="/tmp/route-shared.txt")
            ], 2)

    def test_interruption_terminates_child_and_removes_owned_temp(self):
        process = Mock(pid=12345)
        process.communicate.side_effect = KeyboardInterrupt
        with patch.object(runner.subprocess, "Popen", return_value=process) as popen, \
             patch.object(runner.os, "killpg") as kill:
            with self.assertRaises(KeyboardInterrupt):
                runner.execute(self.task())
            self.assertEqual(kill.call_args_list,
                             [unittest.mock.call(12345, runner.signal.SIGTERM),
                              unittest.mock.call(12345, runner.signal.SIGKILL)])
            process.wait.assert_called_once()
            command = popen.call_args.args[0]
            self.assertFalse(Path(command[command.index("-o") + 1]).exists())

    def test_cancellation_blocks_new_launches_and_escalates(self):
        children = runner.ChildProcesses()
        process = Mock(pid=12345)
        process.wait.side_effect = [runner.subprocess.TimeoutExpired("fake", 5), None]
        children.active.add(process)
        with patch.object(runner.os, "killpg") as kill, \
             patch.object(runner.subprocess, "Popen") as popen:
            children.cancel()
            self.assertEqual(kill.call_args_list,
                             [unittest.mock.call(12345, runner.signal.SIGTERM),
                              unittest.mock.call(12345, runner.signal.SIGKILL)])
            with self.assertRaisesRegex(RuntimeError, "cancelled before launch"):
                children.start(["never-run"])
            popen.assert_not_called()

    def test_batch_and_doctor_cancel_before_executor_exit(self):
        args = argparse.Namespace(spec="unused", timeout=1, log_dir=None,
                                  allow_yolo=False, max_concurrency=1,
                                  dry_run=False, cwd=str(RUNNER_DIR.parent))
        for handler in (runner.batch_command, runner.doctor_command):
            with self.subTest(handler=handler.__name__), \
                 patch.object(runner, "load_batch", return_value=[self.task()]), \
                 patch.object(runner, "ThreadPoolExecutor") as pool, \
                 patch.object(runner, "ChildProcesses") as owner, \
                 patch.object(runner, "as_completed", side_effect=KeyboardInterrupt):
                executor = pool.return_value.__enter__.return_value
                def exiting(*_):
                    owner.return_value.cancel.assert_called_once()
                pool.return_value.__exit__.side_effect = exiting
                with self.assertRaises(KeyboardInterrupt):
                    handler(args)
                owner.return_value.cancel.assert_called_once()
                executor.submit.return_value.cancel.assert_called()

    def test_timeout_escalation_is_bounded_and_reported(self):
        process = Mock(pid=12345)
        process.communicate.side_effect = [
            runner.subprocess.TimeoutExpired("fake", 1),
            runner.subprocess.TimeoutExpired("fake", 5), ("", ""),
        ]
        with patch.object(runner.subprocess, "Popen", return_value=process), \
             patch.object(runner.os, "killpg") as kill:
            result = runner.execute(self.task(timeout=1))
        self.assertEqual((result["status"], result["exit_code"]), ("error", 124))
        self.assertEqual(kill.call_args_list,
                         [unittest.mock.call(12345, runner.signal.SIGTERM),
                          unittest.mock.call(12345, runner.signal.SIGKILL)])
        self.assertEqual(process.communicate.call_args_list[-1].kwargs, {"timeout": 5})

    def test_optional_log_error_preserves_completed_result(self):
        process = Mock(pid=12345, returncode=0)
        process.communicate.return_value = ("", "")
        with patch.object(runner.subprocess, "Popen", return_value=process), \
             patch.object(runner.Path, "read_text", return_value="Verified result."), \
             patch.object(runner, "write_log", side_effect=OSError("disk full")):
            result = runner.execute(self.task(log="/tmp/route-log.json"))
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["final"], "Verified result.")
        self.assertEqual(result["warnings"], ["log write failed: disk full"])

    def test_single_run_rejects_overlapping_output_log_before_launch(self):
        with patch.object(runner.subprocess, "Popen") as popen:
            with self.assertRaisesRegex(ValueError, "output/log collision"):
                runner.execute(self.task(output="/tmp/shared.txt", log="/tmp/shared.txt"))
            popen.assert_not_called()

    def test_timeout_kills_residual_group_after_leader_finishes(self):
        process = Mock(pid=12345)
        process.communicate.side_effect = [
            runner.subprocess.TimeoutExpired("fake", 1), ("", ""),
        ]
        with patch.object(runner.subprocess, "Popen", return_value=process), \
             patch.object(runner.os, "killpg") as kill:
            result = runner.execute(self.task(timeout=1))
        self.assertEqual(result["exit_code"], 124)
        self.assertEqual(kill.call_args_list,
                         [unittest.mock.call(12345, runner.signal.SIGTERM),
                          unittest.mock.call(12345, runner.signal.SIGKILL)])


if __name__ == "__main__":
    unittest.main()

import os
import tempfile
import unittest
from pathlib import Path

from shawn_core_mcp import server


class ServerTests(unittest.TestCase):
    def test_all_specialists_have_uniform_contract(self):
        self.assertEqual(len(server.SPECIALISTS), 15)
        for name, specialist in server.SPECIALISTS.items():
            self.assertTrue(specialist["role"], name)
            self.assertTrue(specialist["aliases"], name)

    def test_routing_keeps_simple_work_with_orchestrator(self):
        self.assertEqual(server.route({"task": "Rename one local file"})["specialist"], "orchestrator")
        self.assertEqual(server.route({"task": "Audit Blender mesh collision"})["specialist"], "cad")
        self.assertEqual(server.route({"task": "Review xEdit master conflicts"})["specialist"], "carl")

    def test_changelog_contract_uses_luna_limits(self):
        policy = server.SPECIALISTS["changelog"]["subprocess"]
        self.assertEqual(policy, {"model": "gpt-5.6-luna", "compact_at_tokens": 64000, "hard_context_limit_tokens": 100000})

    def test_git_snapshot_and_explicit_commit(self):
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            os.environ["SHAWN_CORE_GIT_ROOTS"] = str(repo)
            server.git(repo, "init")
            server.git(repo, "config", "user.name", "Shawn")
            server.git(repo, "config", "user.email", "shawn@example.test")
            (repo / "README.md").write_text("test\n", encoding="utf-8")
            committed = server.git_commit({"repo_path": str(repo), "paths": ["README.md"], "message": "Initial test", "execute": True})
            self.assertEqual(committed["status"], "committed")
            intake = server.changelog_intake({"repo_path": str(repo)})
            self.assertEqual(intake["subprocess_policy"]["model"], "gpt-5.6-luna")
            self.assertEqual(intake["subprocess_policy"]["compact_at_tokens"], 64000)

    def test_atlas_cartographer_card_is_local_and_compact(self):
        with tempfile.TemporaryDirectory() as temporary:
            os.environ["SHAWN_CORE_CONTINUITY_HOME"] = temporary
            result = server.atlas_continuity_record({"title": "Test", "summary": "Validated a local card.", "source": "tests/test_server.py"})
            self.assertEqual(result["specialist"], "atlas-cartographer")
            self.assertTrue(Path(result["path"]).is_file())

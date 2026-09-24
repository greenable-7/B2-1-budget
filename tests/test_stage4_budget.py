import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class Stage4BudgetTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.data_dir = Path(self.temp_dir.name) / "data"

    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(PROJECT_ROOT)
        return subprocess.run(
            [sys.executable, "-B", "-m", "budget_app", "--data-dir", str(self.data_dir), *args],
            text=True,
            capture_output=True,
            cwd=self.temp_dir.name,
            env=environment,
            check=False,
        )

    def test_budget_set_persists_and_show_reads_it_in_another_run(self) -> None:
        saved = self.run_cli("budget", "set", "--month", "2026-09", "--amount", "500000")
        shown = self.run_cli("budget", "show", "--month", "2026-09")

        self.assertEqual(saved.returncode, 0, saved.stderr)
        self.assertIn("예산 설정 완료: 2026-09 | 500000", saved.stdout)
        self.assertEqual(shown.returncode, 0, shown.stderr)
        self.assertIn("2026-09 예산: 500000", shown.stdout)
        records = [
            json.loads(line)
            for line in (self.data_dir / "budgets.jsonl").read_text(encoding="utf-8").splitlines()
        ]
        self.assertEqual(records, [{"month": "2026-09", "amount": 500000}])

    def test_budget_set_updates_the_same_month(self) -> None:
        self.run_cli("budget", "set", "--month", "2026-09", "--amount", "500000")
        updated = self.run_cli("budget", "set", "--month", "2026-09", "--amount", "600000")
        shown = self.run_cli("budget", "show", "--month", "2026-09")

        self.assertEqual(updated.returncode, 0, updated.stderr)
        self.assertIn("2026-09 예산: 600000", shown.stdout)
        self.assertEqual(len((self.data_dir / "budgets.jsonl").read_text(encoding="utf-8").splitlines()), 1)

    def test_budget_show_reports_an_unset_month(self) -> None:
        result = self.run_cli("budget", "show", "--month", "2026-10")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("2026-10 예산이 설정되지 않았습니다.", result.stdout)

    def test_budget_rejects_invalid_month_and_amount_without_traceback(self) -> None:
        invalid_month = self.run_cli("budget", "show", "--month", "2026-13")
        invalid_amount = self.run_cli("budget", "set", "--month", "2026-09", "--amount", "0")

        self.assertEqual(invalid_month.returncode, 1)
        self.assertIn("YYYY-MM", invalid_month.stderr)
        self.assertNotIn("Traceback", invalid_month.stderr)
        self.assertEqual(invalid_amount.returncode, 1)
        self.assertIn("0보다 큰 정수", invalid_amount.stderr)
        self.assertNotIn("Traceback", invalid_amount.stderr)


if __name__ == "__main__":
    unittest.main()

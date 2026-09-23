import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class Stage2ListTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.data_dir = Path(self.temp_dir.name) / "data"
        self.run_cli("category", "add", input_text="food\n")

    def run_cli(self, *args: str, input_text: str = "") -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(PROJECT_ROOT)
        return subprocess.run(
            [sys.executable, "-B", "-m", "budget_app", "--data-dir", str(self.data_dir), *args],
            input=input_text,
            text=True,
            capture_output=True,
            cwd=self.temp_dir.name,
            env=environment,
            check=False,
        )

    def add_transaction(self, date: str, amount: int, memo: str) -> None:
        result = self.run_cli(
            "add",
            input_text=f"{date}\nexpense\nfood\n{amount}\n{memo}\nmeal\n",
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_list_outputs_latest_dates_first_and_respects_limit(self) -> None:
        self.add_transaction("2026-09-01", 1000, "첫째 날")
        self.add_transaction("2026-09-20", 2000, "마지막 날")
        self.add_transaction("2026-09-10", 3000, "중간 날")

        result = self.run_cli("list", "--limit", "2")

        self.assertEqual(result.returncode, 0, result.stderr)
        lines = result.stdout.splitlines()
        self.assertEqual(len(lines), 2)
        self.assertIn("2026-09-20", lines[0])
        self.assertIn("2026-09-10", lines[1])
        self.assertNotIn("2026-09-01", result.stdout)

    def test_list_rejects_non_positive_limit(self) -> None:
        result = self.run_cli("list", "--limit", "0")

        self.assertEqual(result.returncode, 1)
        self.assertIn("0보다 큰 정수", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_list_reports_when_no_transactions_exist(self) -> None:
        result = self.run_cli("list")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("거래 내역이 없습니다", result.stdout)


if __name__ == "__main__":
    unittest.main()

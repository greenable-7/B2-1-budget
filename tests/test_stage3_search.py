import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class Stage3SearchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.data_dir = Path(self.temp_dir.name) / "data"
        self.run_cli("category", "add", input_text="food\n")
        self.run_cli("category", "add", input_text="salary\n")
        self.add_transaction("2026-09-01", "expense", "food", 1000, "Lunch", "meal,work")
        self.add_transaction("2026-09-20", "expense", "food", 2000, "dinner", "meal")
        self.add_transaction("2026-10-01", "income", "salary", 3000, "PAY", "work")

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

    def add_transaction(
        self,
        date: str,
        transaction_type: str,
        category: str,
        amount: int,
        memo: str,
        tags: str,
    ) -> None:
        result = self.run_cli(
            "add",
            input_text=f"{date}\n{transaction_type}\n{category}\n{amount}\n{memo}\n{tags}\n",
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_search_combines_filters_and_outputs_latest_first(self) -> None:
        result = self.run_cli(
            "search",
            "--from",
            "2026-09-01",
            "--to",
            "2026-09-30",
            "--category",
            "food",
            "--type",
            "expense",
            "--q",
            "N",
            "--tag",
            "meal",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        lines = result.stdout.splitlines()
        self.assertEqual(len(lines), 2)
        self.assertIn("2026-09-20", lines[0])
        self.assertIn("2026-09-01", lines[1])
        self.assertNotIn("2026-10-01", result.stdout)

    def test_search_rejects_invalid_or_reversed_dates(self) -> None:
        invalid = self.run_cli("search", "--from", "2026-02-30")
        reversed_range = self.run_cli("search", "--from", "2026-10-01", "--to", "2026-09-01")

        self.assertEqual(invalid.returncode, 1)
        self.assertIn("YYYY-MM-DD", invalid.stderr)
        self.assertNotIn("Traceback", invalid.stderr)
        self.assertEqual(reversed_range.returncode, 1)
        self.assertIn("늦을 수 없습니다", reversed_range.stderr)

    def test_search_reports_no_results(self) -> None:
        result = self.run_cli("search", "--category", "unknown")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("검색 결과가 없습니다.", result.stdout)


if __name__ == "__main__":
    unittest.main()

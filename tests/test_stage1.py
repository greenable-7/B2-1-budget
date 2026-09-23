import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class Stage1CliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.data_dir = Path(self.temp_dir.name) / "data"

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

    def test_add_persists_transaction_and_category_across_runs(self) -> None:
        self.assertEqual(self.run_cli("category", "add", input_text="food\n").returncode, 0)
        added = self.run_cli("add", input_text="2026-09-23\nexpense\nfood\n12000\n점심\nmeal,lunch\n")
        self.assertEqual(added.returncode, 0, added.stderr)
        self.assertIn("거래 저장 완료: TX-", added.stdout)

        listed = self.run_cli("category", "list")
        self.assertEqual(listed.returncode, 0, listed.stderr)
        self.assertEqual(listed.stdout.strip(), "food")

        records = [json.loads(line) for line in (self.data_dir / "transactions.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["amount"], 12000)
        self.assertEqual(records[0]["tags"], ["meal", "lunch"])
        self.assertEqual(json.loads((self.data_dir / "categories.jsonl").read_text(encoding="utf-8")), {"name": "food"})

    def test_invalid_date_does_not_save_transaction(self) -> None:
        self.run_cli("category", "add", input_text="food\n")
        result = self.run_cli("add", input_text="2026-02-30\nexpense\nfood\n12000\n\n\n")
        self.assertEqual(result.returncode, 1)
        self.assertIn("날짜", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual((self.data_dir / "transactions.jsonl").read_text(encoding="utf-8"), "")

    def test_used_category_cannot_be_removed(self) -> None:
        self.run_cli("category", "add", input_text="food\n")
        self.run_cli("add", input_text="2026-09-23\nexpense\nfood\n12000\n\n\n")
        result = self.run_cli("category", "remove", input_text="food\n")
        self.assertEqual(result.returncode, 1)
        self.assertIn("사용 중", result.stderr)
        self.assertEqual(self.run_cli("category", "list").stdout.strip(), "food")


if __name__ == "__main__":
    unittest.main()

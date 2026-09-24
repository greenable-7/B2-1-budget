import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class Stage5SummaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.data_dir = Path(self.temp_dir.name) / "data"
        self.data_dir.mkdir(parents=True)
        records = [
            self.make_record("1", "income", "2026-09-01", 100000, "salary"),
            self.make_record("2", "expense", "2026-09-10", 30000, "food"),
            self.make_record("3", "expense", "2026-09-20", 10000, "transport"),
            self.make_record("4", "expense", "2026-10-01", 99999, "food"),
        ]
        text = "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records)
        (self.data_dir / "transactions.jsonl").write_text(text, encoding="utf-8")

    @staticmethod
    def make_record(
        transaction_id: str,
        transaction_type: str,
        date: str,
        amount: int,
        category: str,
    ) -> dict[str, object]:
        return {
            "id": transaction_id,
            "type": transaction_type,
            "date": date,
            "amount": amount,
            "category": category,
            "memo": "",
            "tags": [],
        }

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

    def test_summary_calculates_totals_top_category_and_budget_status(self) -> None:
        self.run_cli("budget", "set", "--month", "2026-09", "--amount", "35000")
        result = self.run_cli("summary", "--month", "2026-09", "--top", "1")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("수입 합계: 100000", result.stdout)
        self.assertIn("지출 합계: 40000", result.stdout)
        self.assertIn("잔액: 60000", result.stdout)
        self.assertIn("1. food | 30000", result.stdout)
        self.assertNotIn("transport | 10000", result.stdout)
        self.assertIn("예산 사용률: 114.29%", result.stdout)
        self.assertIn("예산 상태: 초과", result.stdout)
        self.assertNotIn("99999", result.stdout)

    def test_summary_reports_an_unset_budget(self) -> None:
        result = self.run_cli("summary", "--month", "2026-09")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("예산: 미설정", result.stdout)

    def test_summary_reports_when_the_month_has_no_transactions(self) -> None:
        result = self.run_cli("summary", "--month", "2026-11")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("2026-11 거래 내역이 없습니다.", result.stdout)
        self.assertNotIn("수입 합계", result.stdout)

    def test_summary_rejects_invalid_month_and_top_without_traceback(self) -> None:
        invalid_month = self.run_cli("summary", "--month", "2026-13")
        invalid_top = self.run_cli("summary", "--month", "2026-09", "--top", "0")

        self.assertEqual(invalid_month.returncode, 1)
        self.assertIn("YYYY-MM", invalid_month.stderr)
        self.assertNotIn("Traceback", invalid_month.stderr)
        self.assertEqual(invalid_top.returncode, 1)
        self.assertIn("0보다 큰 정수", invalid_top.stderr)
        self.assertNotIn("Traceback", invalid_top.stderr)


if __name__ == "__main__":
    unittest.main()

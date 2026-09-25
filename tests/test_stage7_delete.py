import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class Stage7DeleteTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.data_dir = Path(self.temp_dir.name) / "data"
        self.data_dir.mkdir(parents=True)
        self.original_records = [
            {
                "id": "TX-001",
                "type": "expense",
                "date": "2026-09-01",
                "amount": 1000,
                "category": "food",
                "memo": "lunch",
                "tags": ["meal"],
            },
            {
                "id": "TX-002",
                "type": "income",
                "date": "2026-09-02",
                "amount": 5000,
                "category": "salary",
                "memo": "pay",
                "tags": [],
            },
        ]
        text = "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in self.original_records)
        (self.data_dir / "transactions.jsonl").write_text(text, encoding="utf-8")

    def read_records(self) -> list[dict[str, object]]:
        return [
            json.loads(line)
            for line in (self.data_dir / "transactions.jsonl").read_text(encoding="utf-8").splitlines()
        ]

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

    def test_delete_removes_only_the_requested_transaction(self) -> None:
        result = self.run_cli("delete", "--id", "TX-001")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("거래 삭제 완료: TX-001", result.stdout)
        self.assertEqual(self.read_records(), [self.original_records[1]])
        self.assertFalse((self.data_dir / "transactions.tmp").exists())

    def test_delete_rejects_unknown_id_without_changing_the_file(self) -> None:
        original_text = (self.data_dir / "transactions.jsonl").read_text(encoding="utf-8")
        result = self.run_cli("delete", "--id", "TX-999")

        self.assertEqual(result.returncode, 1)
        self.assertIn("거래 ID를 찾을 수 없습니다", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(
            (self.data_dir / "transactions.jsonl").read_text(encoding="utf-8"),
            original_text,
        )
        self.assertFalse((self.data_dir / "transactions.tmp").exists())

    def test_delete_rejects_a_blank_id_without_changing_the_file(self) -> None:
        original_text = (self.data_dir / "transactions.jsonl").read_text(encoding="utf-8")
        result = self.run_cli("delete", "--id", "   ")

        self.assertEqual(result.returncode, 1)
        self.assertIn("--id를 입력", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(
            (self.data_dir / "transactions.jsonl").read_text(encoding="utf-8"),
            original_text,
        )


if __name__ == "__main__":
    unittest.main()

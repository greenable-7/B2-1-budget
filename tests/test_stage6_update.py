import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class Stage6UpdateTests(unittest.TestCase):
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
        self.write_records(self.original_records)
        categories = [{"name": "food"}, {"name": "salary"}, {"name": "transport"}]
        text = "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in categories)
        (self.data_dir / "categories.jsonl").write_text(text, encoding="utf-8")

    def write_records(self, records: list[dict[str, object]]) -> None:
        text = "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records)
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

    def test_update_changes_only_requested_fields_and_persists(self) -> None:
        result = self.run_cli(
            "update",
            "--id",
            "TX-001",
            "--category",
            "transport",
            "--amount",
            "2500",
            "--memo",
            "bus",
            "--tags",
            "commute,morning",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("거래 수정 완료: TX-001", result.stdout)
        records = self.read_records()
        self.assertEqual(records[0]["category"], "transport")
        self.assertEqual(records[0]["amount"], 2500)
        self.assertEqual(records[0]["memo"], "bus")
        self.assertEqual(records[0]["tags"], ["commute", "morning"])
        self.assertEqual(records[0]["date"], "2026-09-01")
        self.assertEqual(records[0]["type"], "expense")
        self.assertEqual(records[1], self.original_records[1])

    def test_update_can_clear_memo_and_tags(self) -> None:
        result = self.run_cli("update", "--id", "TX-001", "--memo", "", "--tags", "")

        self.assertEqual(result.returncode, 0, result.stderr)
        updated = self.read_records()[0]
        self.assertEqual(updated["memo"], "")
        self.assertEqual(updated["tags"], [])

    def test_update_rejects_unknown_id_without_changing_the_file(self) -> None:
        original_text = (self.data_dir / "transactions.jsonl").read_text(encoding="utf-8")
        result = self.run_cli("update", "--id", "TX-999", "--amount", "2000")

        self.assertEqual(result.returncode, 1)
        self.assertIn("거래 ID를 찾을 수 없습니다", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(
            (self.data_dir / "transactions.jsonl").read_text(encoding="utf-8"),
            original_text,
        )
        self.assertFalse((self.data_dir / "transactions.tmp").exists())

    def test_update_rejects_invalid_value_without_changing_the_file(self) -> None:
        original_text = (self.data_dir / "transactions.jsonl").read_text(encoding="utf-8")
        result = self.run_cli("update", "--id", "TX-001", "--date", "2026-02-30")

        self.assertEqual(result.returncode, 1)
        self.assertIn("날짜", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(
            (self.data_dir / "transactions.jsonl").read_text(encoding="utf-8"),
            original_text,
        )

    def test_update_requires_at_least_one_change(self) -> None:
        result = self.run_cli("update", "--id", "TX-001")

        self.assertEqual(result.returncode, 1)
        self.assertIn("수정할 옵션을 하나 이상", result.stderr)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()

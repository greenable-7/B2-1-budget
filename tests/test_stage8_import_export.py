import csv
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CSV_FIELDS = ["date", "type", "category", "amount", "memo", "tags"]


class Stage8ImportExportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.data_dir = self.root / "data"
        self.data_dir.mkdir(parents=True)
        categories = [{"name": "food"}, {"name": "salary"}, {"name": "transport"}]
        text = "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in categories)
        (self.data_dir / "categories.jsonl").write_text(text, encoding="utf-8")

    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(PROJECT_ROOT)
        return subprocess.run(
            [sys.executable, "-B", "-m", "budget_app", "--data-dir", str(self.data_dir), *args],
            text=True,
            capture_output=True,
            cwd=self.root,
            env=environment,
            check=False,
        )

    def write_csv(self, path: Path, rows: list[dict[str, object]]) -> None:
        with path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
            writer.writeheader()
            writer.writerows(rows)

    def seed_transactions(self) -> None:
        records = [
            {
                "id": "TX-001",
                "type": "expense",
                "date": "2026-09-01",
                "amount": 1000,
                "category": "food",
                "memo": "lunch",
                "tags": ["meal", "work"],
            },
            {
                "id": "TX-002",
                "type": "income",
                "date": "2026-09-20",
                "amount": 5000,
                "category": "salary",
                "memo": "pay",
                "tags": [],
            },
            {
                "id": "TX-003",
                "type": "expense",
                "date": "2026-10-01",
                "amount": 2000,
                "category": "transport",
                "memo": "bus",
                "tags": ["commute"],
            },
        ]
        text = "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records)
        (self.data_dir / "transactions.jsonl").write_text(text, encoding="utf-8")

    def read_transactions(self) -> list[dict[str, object]]:
        return [
            json.loads(line)
            for line in (self.data_dir / "transactions.jsonl").read_text(encoding="utf-8").splitlines()
        ]

    def test_import_saves_valid_rows_and_reports_invalid_rows(self) -> None:
        source = self.root / "input.csv"
        self.write_csv(
            source,
            [
                {
                    "date": "2026-09-01",
                    "type": "expense",
                    "category": "food",
                    "amount": "12000",
                    "memo": "lunch",
                    "tags": "meal,work",
                },
                {
                    "date": "2026-09-02",
                    "type": "expense",
                    "category": "food",
                    "amount": "not-a-number",
                    "memo": "invalid amount",
                    "tags": "",
                },
                {
                    "date": "2026-09-03",
                    "type": "expense",
                    "category": "unknown",
                    "amount": "1000",
                    "memo": "invalid category",
                    "tags": "",
                },
                {
                    "date": "2026-09-04",
                    "type": "income",
                    "category": "salary",
                    "amount": "50000",
                    "memo": "pay, bonus",
                    "tags": "work",
                },
            ],
        )

        result = self.run_cli("import", "--from", str(source))

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("성공: 2건, 건너뜀: 2건", result.stdout)
        records = self.read_transactions()
        self.assertEqual(len(records), 2)
        self.assertTrue(all(str(record["id"]).startswith("TX-") for record in records))
        self.assertEqual(records[0]["tags"], ["meal", "work"])
        self.assertEqual(records[1]["memo"], "pay, bonus")

    def test_import_rejects_an_invalid_header_without_traceback(self) -> None:
        source = self.root / "bad-header.csv"
        source.write_text("date,type,category,amount\n2026-09-01,expense,food,1000\n", encoding="utf-8")

        result = self.run_cli("import", "--from", str(source))

        self.assertEqual(result.returncode, 1)
        self.assertIn("CSV 헤더", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(self.read_transactions(), [])

    def test_export_month_writes_utf8_schema_and_matching_rows(self) -> None:
        self.seed_transactions()
        destination = self.root / "september.csv"

        result = self.run_cli("export", "--out", str(destination), "--month", "2026-09")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("내보내기 완료: 2건", result.stdout)
        with destination.open("r", encoding="utf-8", newline="") as file:
            rows = list(csv.DictReader(file))
        self.assertEqual(list(rows[0]), CSV_FIELDS)
        self.assertEqual([row["date"] for row in rows], ["2026-09-20", "2026-09-01"])
        self.assertEqual(rows[1]["tags"], "meal,work")
        self.assertNotIn("id", rows[0])

    def test_export_date_range_and_empty_result(self) -> None:
        self.seed_transactions()
        ranged = self.root / "range.csv"
        empty = self.root / "empty.csv"

        range_result = self.run_cli(
            "export",
            "--out",
            str(ranged),
            "--from",
            "2026-09-15",
            "--to",
            "2026-10-01",
        )
        empty_result = self.run_cli("export", "--out", str(empty), "--month", "2026-11")

        self.assertEqual(range_result.returncode, 0, range_result.stderr)
        with ranged.open("r", encoding="utf-8", newline="") as file:
            ranged_rows = list(csv.DictReader(file))
        self.assertEqual([row["date"] for row in ranged_rows], ["2026-10-01", "2026-09-20"])
        self.assertEqual(empty_result.returncode, 0, empty_result.stderr)
        self.assertIn("내보내기 완료: 0건", empty_result.stdout)
        self.assertEqual(empty.read_text(encoding="utf-8").strip(), ",".join(CSV_FIELDS))

    def test_export_rejects_missing_conflicting_and_invalid_conditions(self) -> None:
        destination = self.root / "output.csv"
        missing = self.run_cli("export", "--out", str(destination))
        conflicting = self.run_cli(
            "export",
            "--out",
            str(destination),
            "--month",
            "2026-09",
            "--from",
            "2026-09-01",
            "--to",
            "2026-09-30",
        )
        incomplete = self.run_cli("export", "--out", str(destination), "--from", "2026-09-01")
        reversed_range = self.run_cli(
            "export",
            "--out",
            str(destination),
            "--from",
            "2026-10-01",
            "--to",
            "2026-09-01",
        )

        for result in (missing, conflicting, incomplete, reversed_range):
            self.assertEqual(result.returncode, 1)
            self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()

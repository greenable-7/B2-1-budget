import json
from collections.abc import Iterable, Iterator
from pathlib import Path

from .model import Transaction


class JsonlRepository:
    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir
        self.path = data_dir / "transactions.jsonl"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.path.touch(exist_ok=True)

    def iter_transactions(self) -> Iterator[Transaction]:
        with self.path.open("r", encoding="utf-8") as file:
            for line in file:
                record = json.loads(line)
                transaction = Transaction(
                    record["id"],
                    record["type"],
                    record["date"],
                    record["amount"],
                    record["category"],
                    record["memo"],
                    record["tags"],
                )
                yield transaction



    def append_transaction(self, transaction: Transaction) -> None:
        record = {
            "id": transaction.transaction_id,
            "type": transaction.transaction_type,
            "date": transaction.date,
            "amount": transaction.amount,
            "category": transaction.category,
            "memo": transaction.memo,
            "tags": transaction.tags,
        }
        line = json.dumps(record, ensure_ascii=False)
        with self.path.open("a", encoding="utf-8") as file:
            file.write(line + "\n")




    # TODO: update/delete 결과를 임시 파일에 쓰고 원자적으로 교체한다.
    def rewrite_transactions(self, transactions: Iterable[Transaction]) -> None:
        pass


class CategoryStore:
    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir
        self.path = data_dir / "categories.jsonl"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.path.touch(exist_ok=True)

    def read_categories(self) -> list[str]:
        categories = []
        with self.path.open("r", encoding="utf-8") as file:
            for line in file:
                record = json.loads(line)
                # 기존에 문자열 한 줄로 저장된 카테고리도 계속 읽는다.
                categories.append(record if isinstance(record, str) else record["name"])
        return categories

    # TODO: 카테고리 목록을 안전하게 저장한다.
    def save_categories(self, categories: list[str]) -> None:
        with self.path.open("w", encoding="utf-8") as file:
            for category in categories:
                file.write(json.dumps({"name": category}, ensure_ascii=False) + "\n")


# TODO: budgets.jsonl의 파일 입출력을 담당한다.
class BudgetStore:
    # TODO: 저장 경로를 보관하고 파일이 없으면 초기화한다.
    def __init__(self, data_dir: Path) -> None:
        pass

    # TODO: 월별 예산을 읽는다.
    def read_budgets(self) -> dict[str, int]:
        pass

    # TODO: 월별 예산을 안전하게 저장한다.
    def save_budgets(self, budgets: dict[str, int]) -> None:
        pass

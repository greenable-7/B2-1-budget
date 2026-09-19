import json
from collections.abc import Iterable, Iterator
from pathlib import Path

from .model import Transaction


# TODO: transactions.jsonl의 파일 입출력을 담당한다.
class JsonlRepository:
    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir
        self.path = data_dir / "transactions.jsonl"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.path.touch(exist_ok=True)

    # TODO: yield 기반 제너레이터로 거래를 한 건씩 읽는다.
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



    # TODO: 거래 한 건을 JSONL로 추가한다.
    def append_transaction(self, transaction: Transaction) -> None:
        record = {
            "id": transaction.transaction_id,
            "type": transaction.transaction_type,
            "date": transaction.date,
            "amount": transaction.amount,
            "category": transaction.category,
            "memo": transaction.memo,
            "tags":  transaction.tags,
        }
        yield transaction
        line = json.dumps(record,ensure_ascii=False)
        with self.path.open("a",encoding="utf-8") as file:
            file.write(line + "\n")




    # TODO: update/delete 결과를 임시 파일에 쓰고 원자적으로 교체한다.
    def rewrite_transactions(self, transactions: Iterable[Transaction]) -> None:
        pass


# TODO: categories.jsonl의 파일 입출력을 담당한다.
class CategoryStore:
    # TODO: 저장 경로를 보관하고 파일이 없으면 초기화한다.
    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir
        self.path = data_dir / "categories.jsonl"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.path.touch(exist_ok=True)

    # TODO: 등록된 카테고리를 읽는다.
    def read_categories(self) -> list[str]:
        categories = []
        with self.path.open("r", encoding="utf-8") as file:
            for line in file:
                categories.append(json.loads(line))
        return categories

    # TODO: 카테고리 목록을 안전하게 저장한다.
    def save_categories(self, categories: list[str]) -> None:
        with self.path.open("w", encoding="utf-8") as file:
            for category in categories:
                file.write(json.dumps(category, ensure_ascii=False) + "\n")


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

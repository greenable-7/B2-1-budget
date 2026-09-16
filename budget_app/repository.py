from collections.abc import Iterable, Iterator
from pathlib import Path

from .model import Transaction


# TODO: transactions.jsonl의 파일 입출력을 담당한다.
class JsonlRepository:
    # TODO: 저장 경로를 보관하고 파일이 없으면 초기화한다.
    def __init__(self, data_dir: Path) -> None:
        pass

    # TODO: yield 기반 제너레이터로 거래를 한 건씩 읽는다.
    def iter_transactions(self) -> Iterator[Transaction]:
        pass

    # TODO: 거래 한 건을 JSONL로 추가한다.
    def append_transaction(self, transaction: Transaction) -> None:
        pass

    # TODO: update/delete 결과를 임시 파일에 쓰고 원자적으로 교체한다.
    def rewrite_transactions(self, transactions: Iterable[Transaction]) -> None:
        pass


# TODO: categories.jsonl의 파일 입출력을 담당한다.
class CategoryStore:
    # TODO: 저장 경로를 보관하고 파일이 없으면 초기화한다.
    def __init__(self, data_dir: Path) -> None:
        pass

    # TODO: 등록된 카테고리를 읽는다.
    def read_categories(self) -> list[str]:
        pass

    # TODO: 카테고리 목록을 안전하게 저장한다.
    def save_categories(self, categories: list[str]) -> None:
        pass


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

import calendar
import heapq
import re
from collections.abc import Iterator
from datetime import date
from pathlib import Path
import uuid

from .model import Transaction
from .repository import BudgetStore, CategoryStore, JsonlRepository


class BudgetService:
    def __init__(self, repository: JsonlRepository, categories: CategoryStore, budgets: BudgetStore) -> None:
        self.repository = repository
        self.categories = categories
        self.budgets = budgets

    def validate_transaction(self, transaction: Transaction) -> None:
        try:
            parsed_date = date.fromisoformat(transaction.date)
            if parsed_date.isoformat() != transaction.date:
                raise ValueError
        except ValueError as exc:
            raise ValueError("날짜는 실제 존재하는 YYYY-MM-DD 형식이어야 합니다.") from exc

        if transaction.transaction_type not in {"income", "expense"}:
            raise ValueError("거래 타입은 income 또는 expense여야 합니다.")
        if type(transaction.amount) is not int or transaction.amount <= 0:
            raise ValueError("금액은 0보다 큰 정수여야 합니다.")
        categories = self.categories.read_categories()
        if transaction.category not in categories:
            raise ValueError("등록되지 않은 카테고리입니다. 먼저 category add로 등록해 주세요.")

    def add_transaction(self, transaction: Transaction) -> str:
        self.validate_transaction(transaction)
        transaction.transaction_id = f"TX-{uuid.uuid4().hex}"
        self.repository.append_transaction(transaction)
        return transaction.transaction_id

    def list_transactions(self, limit: int = 20) -> Iterator[Transaction]:
        if type(limit) is not int or limit <= 0:
            raise ValueError("--limit은 0보다 큰 정수여야 합니다. 예: --limit 20")

        # 파일 전체를 목록에 담지 않고, 필요한 최신 N건만 메모리에 유지한다.
        latest_transactions = heapq.nlargest(
            limit,
            enumerate(self.repository.iter_transactions()),
            key=lambda item: (item[1].date, item[0]),
        )
        for _, transaction in latest_transactions:
            yield transaction

    def search_transactions(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
        category: str | None = None,
        transaction_type: str | None = None,
        query: str | None = None,
        tag: str | None = None,
    ) -> Iterator[Transaction]:
        self._validate_search_date(start_date, "--from")
        self._validate_search_date(end_date, "--to")
        if start_date is not None and end_date is not None and start_date > end_date:
            raise ValueError("--from 날짜는 --to 날짜보다 늦을 수 없습니다.")
        if transaction_type is not None and transaction_type not in {"income", "expense"}:
            raise ValueError("--type은 income 또는 expense여야 합니다.")

        normalized_query = query.casefold() if query is not None else None

        def matches(transaction: Transaction) -> bool:
            return (
                (start_date is None or transaction.date >= start_date)
                and (end_date is None or transaction.date <= end_date)
                and (category is None or transaction.category == category)
                and (transaction_type is None or transaction.transaction_type == transaction_type)
                and (normalized_query is None or normalized_query in transaction.memo.casefold())
                and (tag is None or tag in transaction.tags)
            )

        matching_transactions = (
            (index, transaction)
            for index, transaction in enumerate(self.repository.iter_transactions())
            if matches(transaction)
        )
        for _, transaction in sorted(
            matching_transactions,
            key=lambda item: (item[1].date, item[0]),
            reverse=True,
        ):
            yield transaction

    @staticmethod
    def _validate_search_date(value: str | None, option_name: str) -> None:
        if value is None:
            return
        match = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", value)
        if match is None:
            raise ValueError(f"{option_name}은 실제 존재하는 YYYY-MM-DD 날짜여야 합니다.")

        year, month, day = (int(part) for part in match.groups())
        is_valid = (
            1 <= year <= 9999
            and 1 <= month <= 12
            and 1 <= day <= calendar.monthrange(year, month)[1]
        )
        if not is_valid:
            raise ValueError(f"{option_name}은 실제 존재하는 YYYY-MM-DD 날짜여야 합니다.")

    def summarize_month(self, month: str, top: int = 5) -> dict[str, object]:
        self._validate_month(month)
        if type(top) is not int or top <= 0:
            raise ValueError("--top은 0보다 큰 정수여야 합니다. 예: --top 5")

        total_income = 0
        total_expense = 0
        transaction_count = 0
        expenses_by_category: dict[str, int] = {}

        for transaction in self.repository.iter_transactions():
            if not transaction.date.startswith(f"{month}-"):
                continue

            transaction_count += 1
            if transaction.transaction_type == "income":
                total_income += transaction.amount
            else:
                total_expense += transaction.amount
                expenses_by_category[transaction.category] = (
                    expenses_by_category.get(transaction.category, 0) + transaction.amount
                )

        top_expense_categories = sorted(
            expenses_by_category.items(),
            key=lambda item: (-item[1], item[0]),
        )[:top]
        budget = self.get_budget(month)
        budget_usage_rate = total_expense / budget * 100 if budget is not None else None

        return {
            "month": month,
            "transaction_count": transaction_count,
            "total_income": total_income,
            "total_expense": total_expense,
            "balance": total_income - total_expense,
            "top_expense_categories": top_expense_categories,
            "budget": budget,
            "budget_usage_rate": budget_usage_rate,
            "is_over_budget": total_expense > budget if budget is not None else None,
        }

    def set_budget(self, month: str, amount: int) -> None:
        self._validate_month(month)
        if type(amount) is not int or amount <= 0:
            raise ValueError("--amount는 0보다 큰 정수여야 합니다.")

        budgets = self.budgets.read_budgets()
        budgets[month] = amount
        self.budgets.save_budgets(budgets)

    def get_budget(self, month: str) -> int | None:
        self._validate_month(month)
        return self.budgets.read_budgets().get(month)

    @staticmethod
    def _validate_month(month: str) -> None:
        match = re.fullmatch(r"(\d{4})-(\d{2})", month)
        if match is None:
            raise ValueError("--month는 YYYY-MM 형식이어야 합니다. 예: 2026-09")

        year, month_number = (int(part) for part in match.groups())
        if not 1 <= year <= 9999 or not 1 <= month_number <= 12:
            raise ValueError("--month는 실제 존재하는 YYYY-MM 형식이어야 합니다. 예: 2026-09")

    def add_category(self, name: str) -> None:
        name = name.strip()
        if not name:
            raise ValueError("카테고리 이름을 입력해 주세요.")

        categories = self.categories.read_categories()
        if name in categories:
            raise ValueError("이미 등록된 카테고리입니다.")

        categories.append(name)
        self.categories.save_categories(categories)

    def list_categories(self) -> list[str]:
        return self.categories.read_categories()

    def remove_category(self, name: str) -> None:
        name = name.strip()
        if not name:
            raise ValueError("삭제할 카테고리 이름을 입력해 주세요")

        categories = self.categories.read_categories()
        if name not in categories:
            raise ValueError("등록되지 않은 카테고리입니다")

        if any(transaction.category == name for transaction in self.repository.iter_transactions()):
            raise ValueError("거래에서 사용 중인 카테고리는 삭제할 수 없습니다.")

        categories.remove(name)
        self.categories.save_categories(categories)



    # TODO: id와 수정 필드를 검증하고 안전하게 재작성하며 없는 id를 처리한다.
    def update_transaction(self, transaction_id: str, changes: dict[str, object]) -> None:
        pass

    # TODO: id에 해당하는 거래를 안전하게 삭제하고 없는 id를 처리한다.
    def delete_transaction(self, transaction_id: str) -> None:
        pass

    # TODO: CSV 행을 검증해 가져오고 성공·건너뜀 건수를 제공한다.
    def import_csv(self, source: Path) -> tuple[int, int]:
        pass

    # TODO: 월 또는 시작·종료일 조건을 검증해 CSV를 내보내고 처리 건수를 제공한다.
    def export_csv(self, destination: Path, month: str | None = None, start_date: str | None = None, end_date: str | None = None) -> int:
        pass

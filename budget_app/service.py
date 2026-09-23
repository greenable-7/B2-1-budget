import heapq
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

    # TODO: 기간·카테고리·타입·메모·태그로 스트리밍 검색하고 최신순으로 제공한다.
    def search_transactions(self, start_date: str | None = None, end_date: str | None = None, category: str | None = None, transaction_type: str | None = None, query: str | None = None, tag: str | None = None) -> Iterator[Transaction]:
        pass

    # TODO: 월별 합계·잔액·지출 TOP N·예산 사용률·초과 여부와 빈 결과를 제공한다.
    def summarize_month(self, month: str, top: int = 5) -> dict[str, object]:
        pass

    # TODO: 월과 양수 정수 금액을 검증해 예산을 설정한다.
    def set_budget(self, month: str, amount: int) -> None:
        pass

    # TODO: 해당 월의 예산을 조회하고 미설정 상태를 구분한다.
    def get_budget(self, month: str) -> int | None:
        pass

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

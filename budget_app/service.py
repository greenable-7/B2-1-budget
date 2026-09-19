from collections.abc import Iterator
from pathlib import Path

from .model import Transaction
from .repository import BudgetStore, CategoryStore, JsonlRepository


# TODO: 입력 검증과 가계부 비즈니스 규칙을 담당한다.
class BudgetService:
    # TODO: 거래·카테고리·예산 저장소를 연결한다.
    def __init__(self, repository: JsonlRepository, categories: CategoryStore, budgets: BudgetStore) -> None:
        self.repository = repository
        self.categories = categories
        self.budgets = budgets

    # TODO: 날짜·양수 정수 금액·타입·등록된 카테고리를 검증한다.
    def validate_transaction(self, transaction: Transaction) -> None:
        if transaction.transaction_type not in {"income","expense"}:
            raise ValueError("거래 타입은 income 또는 expense여야 합니다.")
        if transaction.amount <= 0:
            raise ValueError("금액은 0보다 큰 정수여야 합니다.")
        categories = self.categories.read_categories()
        if transaction.category not in categories:
            pass

    # TODO: 거래를 검증하고 고유 id를 부여해 저장한다.
    def add_transaction(self, transaction: Transaction) -> str:
        pass

    # TODO: 스트리밍을 유지하며 최신순으로 기본 20건을 조회한다.
    def list_transactions(self, limit: int = 20) -> Iterator[Transaction]:
        pass

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

    # TODO: 빈 이름과 중복을 검증해 카테고리를 등록한다.
    def add_category(self, name: str) -> None:
        name = name.strip()
        if not name:
            raise ValueError("카테고리 이름을 입력해 주세요.")

        categories = self.categories.read_categories()
        if name in categories:
            raise ValueError("이미 등록된 카테고리입니다.")
        
        categories.append(name)
        self.categories.save_categories(categories)

    # TODO: 등록된 카테고리 목록을 제공한다.
    def list_categories(self) -> list[str]:
        return self.categories.read_categories()

    # TODO: 사용 중인 카테고리의 삭제를 막고 없는 이름을 처리한다.
    def remove_category(self, name: str) -> None:
        name = name.strip()
        if not name:
            raise ValueError("삭제할 카테고리 이름을 입력해 주세요")

        categories = self.categories.read_categories()
        if name not in categories:
            raise ValueError("등록되지 않은 카테고리입니다")

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

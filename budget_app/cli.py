import argparse
from collections.abc import Iterable
from pathlib import Path
from typing import cast

from .decorator import handle_cli_errors
from .model import Transaction
from .repository import BudgetStore, CategoryStore, JsonlRepository
from .service import BudgetService


@handle_cli_errors
def run() -> None:
    parser = argparse.ArgumentParser(description="파일에 저장하는 콘솔 가계부")
    parser.add_argument("--data-dir", type=Path, default=Path("data"), help="데이터 저장 폴더 (기본값: ./data)")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("add", help="거래를 입력하고 저장")
    list_parser = subparsers.add_parser("list", help="거래를 최신순으로 조회")
    list_parser.add_argument("--limit", type=int, default=20, help="출력할 최대 거래 수 (기본값: 20)")
    search_parser = subparsers.add_parser("search", help="조건에 맞는 거래를 최신순으로 검색")
    search_parser.add_argument("--from", dest="start_date", help="검색 시작일 (YYYY-MM-DD, 포함)")
    search_parser.add_argument("--to", dest="end_date", help="검색 종료일 (YYYY-MM-DD, 포함)")
    search_parser.add_argument("--category", help="카테고리")
    search_parser.add_argument("--type", dest="transaction_type", help="거래 타입 (income/expense)")
    search_parser.add_argument("--q", dest="query", help="메모에 포함된 검색어")
    search_parser.add_argument("--tag", help="태그")
    summary_parser = subparsers.add_parser("summary", help="월별 수입과 지출 요약")
    summary_parser.add_argument("--month", required=True, help="요약할 월 (YYYY-MM)")
    summary_parser.add_argument("--top", type=int, default=5, help="표시할 지출 카테고리 수 (기본값: 5)")
    budget_parser = subparsers.add_parser("budget", help="월별 예산을 설정하거나 조회")
    budget_parser.set_defaults(amount=None)
    budget_subparsers = budget_parser.add_subparsers(dest="budget_command", required=True)
    budget_set_parser = budget_subparsers.add_parser("set", help="월별 예산 설정")
    budget_set_parser.add_argument("--month", required=True, help="예산 적용 월 (YYYY-MM)")
    budget_set_parser.add_argument("--amount", type=int, required=True, help="예산 금액")
    budget_show_parser = budget_subparsers.add_parser("show", help="월별 예산 조회")
    budget_show_parser.add_argument("--month", required=True, help="조회할 월 (YYYY-MM)")
    update_parser = subparsers.add_parser("update", help="거래 ID로 원하는 항목만 수정")
    update_parser.add_argument("--id", required=True, help="수정할 거래 ID")
    update_parser.add_argument("--date", help="변경할 날짜 (YYYY-MM-DD)")
    update_parser.add_argument("--type", dest="transaction_type", help="변경할 거래 타입")
    update_parser.add_argument("--category", help="변경할 카테고리")
    update_parser.add_argument("--amount", type=int, help="변경할 금액")
    update_parser.add_argument("--memo", help="변경할 메모")
    update_parser.add_argument("--tags", help="변경할 태그 (쉼표 구분)")
    category_parser = subparsers.add_parser("category")
    category_subparsers = category_parser.add_subparsers(dest="category_command", required=True)
    category_subparsers.add_parser("add")
    category_subparsers.add_parser("list")
    category_subparsers.add_parser("remove")
    args = parser.parse_args()

    service = BudgetService(
        JsonlRepository(args.data_dir),
        CategoryStore(args.data_dir),
        BudgetStore(args.data_dir),
    )
    if args.command == "add":
        handle_add(service)
    elif args.command == "list":
        handle_list(service, args.limit)
    elif args.command == "search":
        handle_search(
            service,
            start_date=args.start_date,
            end_date=args.end_date,
            category=args.category,
            transaction_type=args.transaction_type,
            query=args.query,
            tag=args.tag,
        )
    elif args.command == "summary":
        handle_summary(service, month=args.month, top=args.top)
    elif args.command == "budget":
        handle_budget(
            service,
            budget_command=args.budget_command,
            month=args.month,
            amount=args.amount,
        )
    elif args.command == "update":
        handle_update(
            service,
            transaction_id=args.id,
            date=args.date,
            transaction_type=args.transaction_type,
            category=args.category,
            amount=args.amount,
            memo=args.memo,
            tags=args.tags,
        )
    elif args.command == "category":
        handle_category(service, args.category_command)


def handle_add(service: BudgetService) -> None:
    date_text = input("날짜 (YYYY-MM-DD): ").strip()
    transaction_type = input("타입 (income/expense): ").strip()
    category = input("카테고리: ").strip()
    amount_text = input("금액: ").strip()
    try:
        amount = int(amount_text)
    except ValueError as exc:
        raise ValueError("금액은 0보다 큰 정수로 입력해 주세요.") from exc

    transaction = Transaction(
        transaction_id="",
        transaction_type=transaction_type,
        date=date_text,
        category=category,
        amount=amount,
        memo=input("메모: ").strip(),
        tags=[tag.strip() for tag in input("태그 (쉼표 구분): ").split(",") if tag.strip()],
    )
    print(f"거래 저장 완료: {service.add_transaction(transaction)}")

def handle_list(service: BudgetService, limit: int) -> None:
    print_transactions(service.list_transactions(limit), "거래 내역이 없습니다.")


def print_transactions(transactions: Iterable[Transaction], empty_message: str) -> None:
    has_transactions = False
    for transaction in transactions:
        has_transactions = True
        tags = ",".join(transaction.tags)
        print(
            f"{transaction.transaction_id} | {transaction.date} | "
            f"{transaction.transaction_type} | {transaction.category} | "
            f"{transaction.amount} | {transaction.memo} | {tags}"
        )

    if not has_transactions:
        print(empty_message)


def handle_search(
    service: BudgetService,
    start_date: str | None,
    end_date: str | None,
    category: str | None,
    transaction_type: str | None,
    query: str | None,
    tag: str | None,
) -> None:
    transactions = service.search_transactions(
        start_date=start_date,
        end_date=end_date,
        category=category,
        transaction_type=transaction_type,
        query=query,
        tag=tag,
    )
    print_transactions(transactions, "검색 결과가 없습니다.")

def handle_summary(service: BudgetService, month: str, top: int) -> None:
    summary = service.summarize_month(month, top)
    if summary["transaction_count"] == 0:
        print(f"{month} 거래 내역이 없습니다.")
        return

    print(f"월 요약: {month}")
    print(f"수입 합계: {summary['total_income']}")
    print(f"지출 합계: {summary['total_expense']}")
    print(f"잔액: {summary['balance']}")

    top_categories = cast(list[tuple[str, int]], summary["top_expense_categories"])
    if top_categories:
        print(f"지출 카테고리 TOP {top}:")
        for rank, (category, amount) in enumerate(top_categories, start=1):
            print(f"{rank}. {category} | {amount}")
    else:
        print("지출 내역이 없습니다.")

    budget = cast(int | None, summary["budget"])
    if budget is None:
        print("예산: 미설정")
        return

    usage_rate = cast(float, summary["budget_usage_rate"])
    is_over_budget = cast(bool, summary["is_over_budget"])
    print(f"예산: {budget}")
    print(f"예산 사용률: {usage_rate:.2f}%")
    print(f"예산 상태: {'초과' if is_over_budget else '정상'}")

def handle_budget(
    service: BudgetService,
    budget_command: str,
    month: str,
    amount: int | None,
) -> None:
    if budget_command == "set":
        if amount is None:
            raise ValueError("budget set에는 --amount가 필요합니다.")
        service.set_budget(month, amount)
        print(f"예산 설정 완료: {month} | {amount}")
    elif budget_command == "show":
        saved_amount = service.get_budget(month)
        if saved_amount is None:
            print(f"{month} 예산이 설정되지 않았습니다.")
        else:
            print(f"{month} 예산: {saved_amount}")

def handle_category(service: BudgetService, category_command: str) -> None:
    if category_command == "add":
        name = input("추가할 카테고리 이름: ").strip()
        service.add_category(name)
        print(f"카테고리 추가: {name}")
    elif category_command == "list":
        categories = service.list_categories()
        for category in categories:
            print(category)
    elif category_command == "remove":
        name = input("삭제할 카테고리 이름: ").strip()
        service.remove_category(name)
        print(f"카테고리 삭제: {name}")


def handle_update(
    service: BudgetService,
    transaction_id: str,
    date: str | None,
    transaction_type: str | None,
    category: str | None,
    amount: int | None,
    memo: str | None,
    tags: str | None,
) -> None:
    changes: dict[str, object] = {}
    if date is not None:
        changes["date"] = date
    if transaction_type is not None:
        changes["transaction_type"] = transaction_type
    if category is not None:
        changes["category"] = category
    if amount is not None:
        changes["amount"] = amount
    if memo is not None:
        changes["memo"] = memo
    if tags is not None:
        changes["tags"] = [tag.strip() for tag in tags.split(",") if tag.strip()]

    service.update_transaction(transaction_id, changes)
    print(f"거래 수정 완료: {transaction_id}")

# TODO: --id 옵션으로 거래 삭제를 요청한다.
def handle_delete() -> None:
    pass

def handle_import() -> None:
    parser = argparse.ArgumentParser(prog="budget import")
    parser.add_argument("--from", dest="source", type=Path, required=True)
    args = parser.parse_args()

    data_dir = Path("data")
    service = BudgetService(
        JsonlRepository(data_dir),
        CategoryStore(data_dir),
        BudgetStore(data_dir),
    )
    imported, skipped = service.import_csv(args.source)
    print(f"성공: {imported}건, 건너뜀: {skipped}건")

# TODO: --out과 --month 또는 --from/--to 조건으로 CSV를 내보낸다.
def handle_export() -> None:
    pass

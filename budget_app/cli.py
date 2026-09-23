import argparse
from pathlib import Path

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
    has_transactions = False
    for transaction in service.list_transactions(limit):
        has_transactions = True
        tags = ",".join(transaction.tags)
        print(
            f"{transaction.transaction_id} | {transaction.date} | "
            f"{transaction.transaction_type} | {transaction.category} | "
            f"{transaction.amount} | {transaction.memo} | {tags}"
        )

    if not has_transactions:
        print("거래 내역이 없습니다.")

# TODO: --from, --to, --category, --type, --q, --tag 옵션으로 검색한다.
def handle_search() -> None:
    pass

# TODO: --month, --top 옵션으로 월별 요약을 요청한다.
def handle_summary() -> None:
    pass

# TODO: budget set --month --amount와 budget show --month를 연결한다.
def handle_budget() -> None:
    pass

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


# TODO: --id와 --date, --type, --category, --amount, --memo, --tags로 수정한다.
def handle_update() -> None:
    pass

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

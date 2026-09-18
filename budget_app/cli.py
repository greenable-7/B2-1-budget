import argparse
from pathlib import Path

from .model import Transaction
from .repository import BudgetStore, CategoryStore, JsonlRepository
from .service import BudgetService


# TODO: 전역 --data-dir와 명령별 --help를 구성하고 공통 오류 데코레이터를 이 진입점에만 적용한다.
def run() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")
    category_parser = subparsers.add_parser("category")
    category_subparsers = category_parser.add_subparsers(dest="category_command")
    category_subparsers.add_parser("add")
    category_subparsers.add_parser("list")
    category_subparsers.add_parser("remove")
    args = parser.parse_args()

    if args.command == "category":
         handle_category(args.category_command)

def handle_add() -> None:
    data_dir = Path("data")
    service = BudgetService(
        JsonlRepository(data_dir),
        CategoryStore(data_dir),
        BudgetStore(data_dir),
    )
    transaction = Transaction(
        id="",
        date=input("날짜 (YYYY-MM-DD): ").strip(),
        type=input("타입 (income/expense): ").strip(),
        category=input("카테고리: ").strip(),
        amount=int(input("금액: ").strip()),
        memo=input("메모: ").strip(),
        tags=[tag.strip() for tag in input("태그 (쉼표 구분): ").split(",") if tag.strip()],
    )
    print(service.add_transaction(transaction))

# TODO: --limit 옵션으로 최신순 목록을 요청한다.
def handle_list() -> None:
    pass

# TODO: --from, --to, --category, --type, --q, --tag 옵션으로 검색한다.
def handle_search() -> None:
    pass

# TODO: --month, --top 옵션으로 월별 요약을 요청한다.
def handle_summary() -> None:
    pass

# TODO: budget set --month --amount와 budget show --month를 연결한다.
def handle_budget() -> None:
    pass

# TODO: category add/list/remove를 연결하고 추가·삭제할 이름을 대화형으로 입력받는다.
def handle_category(category_command: str) -> None:
    data_dir = Path("data")
    service = BudgetService(
        JsonlRepository(data_dir),
        CategoryStore(data_dir),
        BudgetStore(data_dir),
    )

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

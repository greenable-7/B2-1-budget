import argparse
from pathlib import Path

from .decorator import handle_cli_errors
from .handlers import (
    handle_add,
    handle_budget,
    handle_category,
    handle_delete,
    handle_export,
    handle_import,
    handle_list,
    handle_search,
    handle_summary,
    handle_update,
)
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
    delete_parser = subparsers.add_parser("delete", help="거래 ID로 삭제")
    delete_parser.add_argument("--id", required=True, help="삭제할 거래 ID")
    import_parser = subparsers.add_parser("import", help="CSV에서 거래 가져오기")
    import_parser.add_argument("--from", dest="source", type=Path, required=True, help="가져올 CSV 파일")
    export_parser = subparsers.add_parser("export", help="거래를 CSV로 내보내기")
    export_parser.add_argument("--out", type=Path, required=True, help="저장할 CSV 파일")
    export_parser.add_argument("--month", help="내보낼 월 (YYYY-MM)")
    export_parser.add_argument("--from", dest="start_date", help="시작일 (YYYY-MM-DD, 포함)")
    export_parser.add_argument("--to", dest="end_date", help="종료일 (YYYY-MM-DD, 포함)")
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
    elif args.command == "delete":
        handle_delete(service, transaction_id=args.id)
    elif args.command == "import":
        handle_import(service, source=args.source)
    elif args.command == "export":
        handle_export(
            service,
            destination=args.out,
            month=args.month,
            start_date=args.start_date,
            end_date=args.end_date,
        )
    elif args.command == "category":
        handle_category(service, args.category_command)

from collections.abc import Iterable
from pathlib import Path
from typing import cast

from .model import Transaction
from .service import BudgetService


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


def handle_delete(service: BudgetService, transaction_id: str) -> None:
    service.delete_transaction(transaction_id)
    print(f"거래 삭제 완료: {transaction_id}")


def handle_import(service: BudgetService, source: Path) -> None:
    imported, skipped = service.import_csv(source)
    print(f"성공: {imported}건, 건너뜀: {skipped}건")


def handle_export(
    service: BudgetService,
    destination: Path,
    month: str | None,
    start_date: str | None,
    end_date: str | None,
) -> None:
    exported = service.export_csv(
        destination,
        month=month,
        start_date=start_date,
        end_date=end_date,
    )
    print(f"내보내기 완료: {exported}건 | {destination}")

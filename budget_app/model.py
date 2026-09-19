# 거래 한 건의 id, type, date, amount, category, memo, tags를 관리한다.
class Transaction:
    def __init__(self, transaction_id: str,transaction_type: str, date: str, amount: int, category: str, memo: str = "", tags: list[str] | None = None) -> None:
        self.transaction_id = transaction_id
        self.transaction_type = transaction_type
        self.date = date
        self.amount = amount
        self.category = category
        self.memo = memo
        self.tags = tags or []


 
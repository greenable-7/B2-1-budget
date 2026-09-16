# repository.py 구현 계획

저장소는 Python 데이터와 파일 사이의 읽기·쓰기를 담당합니다. 사용자 메시지와 비즈니스 판단은 맡지 않습니다.
모든 메서드는 미구현이며 타입 힌트는 예정된 입력·출력 계약입니다.

| 클래스·메서드 | 앞으로 할 일 |
| --- | --- |
| 각 클래스의 __init__ | data_dir를 보관하고 없는 폴더·파일 초기화 |
| JsonlRepository.iter_transactions | transactions.jsonl을 한 줄씩 읽고 Transaction을 yield |
| JsonlRepository.append_transaction | 거래 한 건을 JSONL 한 줄로 추가 |
| JsonlRepository.rewrite_transactions | 수정·삭제 후 남길 거래들을 받아 안전하게 전체 재작성 |
| CategoryStore.read_categories | categories.jsonl에서 name 목록 읽기 |
| CategoryStore.save_categories | 전달받은 카테고리 목록 저장 |
| BudgetStore.read_budgets | budgets.jsonl에서 월과 금액을 읽어 사전으로 제공 |
| BudgetStore.save_budgets | 전달받은 월별 예산 저장 |

세 파일은 UTF-8 JSONL로 계획합니다. 카테고리는 한 줄에 name, 예산은 month와 amount를 저장합니다.
거래 조회는 파일 전체를 목록으로 읽지 않는 제너레이터로 구현할 예정입니다.
현재 iter_transactions는 pass뿐이므로 실제 제너레이터는 아닙니다.

수정·삭제는 같은 디렉터리의 임시 파일에 결과를 모두 쓴 뒤 원본을 원자적으로 교체할 계획입니다.
실패 시 원본 보존과 임시 파일 정리를 고려해야 하며 이 처리도 미구현입니다.
최신순 목록·검색과 스트리밍을 함께 만족하는 저장·읽기 전략은 추후 설계해야 합니다.

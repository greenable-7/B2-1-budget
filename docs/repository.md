# repository.py 구현 계획

저장소는 Python 데이터와 파일 사이의 읽기·쓰기를 담당합니다. 사용자 메시지와 비즈니스 판단은 맡지 않습니다.
거래 한 건 저장·읽기·안전한 재작성, 카테고리 저장·읽기, 예산 저장·읽기는 구현했습니다.

| 클래스·메서드 | 앞으로 할 일 |
| --- | --- |
| 각 클래스의 __init__ | data_dir를 보관하고 없는 폴더·파일 초기화 |
| JsonlRepository.iter_transactions | transactions.jsonl을 한 줄씩 읽고 Transaction을 yield |
| JsonlRepository.append_transaction | 거래 한 건을 JSONL 한 줄로 추가 |
| JsonlRepository.rewrite_transactions | 구현: 수정·삭제 결과를 임시 파일에 쓴 뒤 원본과 교체 |
| CategoryStore.read_categories | categories.jsonl에서 name 목록 읽기 |
| CategoryStore.save_categories | 전달받은 카테고리 목록 저장 |
| BudgetStore.read_budgets | 구현: budgets.jsonl에서 월과 금액을 읽어 사전으로 제공 |
| BudgetStore.save_budgets | 구현: 월별 예산을 월 순서의 UTF-8 JSONL로 저장 |

세 파일은 UTF-8 JSONL로 계획합니다. 카테고리는 한 줄에 name, 예산은 month와 amount를 저장합니다.
`iter_transactions`는 `yield`로 거래를 한 건씩 읽는 제너레이터입니다.
서비스의 `list_transactions`는 이 제너레이터를 사용해 필요한 최신 N건만 메모리에 유지합니다.
검색도 이 제너레이터를 통해 거래를 한 줄씩 읽고 조건을 적용합니다.

예산은 `{"month": "2026-09", "amount": 500000}` 형태로 한 줄에 한 달씩 저장합니다.
같은 달의 예산을 다시 설정하면 사전의 해당 값을 바꾼 뒤 저장하므로 중복 행이 생기지 않습니다.
저장할 때는 임시 파일을 먼저 완성한 뒤 `budgets.jsonl`과 교체해 기존 파일의 손상 위험을 줄입니다.

수정·삭제는 같은 디렉터리의 임시 파일에 결과를 모두 쓴 뒤 원본을 교체합니다.
거래 생성이나 검증 중 오류가 발생하면 원본을 보존하고 `finally`에서 임시 파일을 정리합니다.
최신순 목록·검색과 스트리밍을 함께 만족하는 저장·읽기 전략은 추후 설계해야 합니다.

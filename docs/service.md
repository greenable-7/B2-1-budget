# service.py 구현 계획

BudgetService는 CLI가 받은 요청을 검증하고 저장소를 호출합니다.
거래 추가·검증·최신순 목록·검색·월별 요약, 예산 설정·조회와 카테고리 추가·조회·삭제는 구현됐고, 나머지 메서드는 미구현입니다.
화면 출력이나 직접 파일 입출력은 담당하지 않습니다.

| 메서드 | 앞으로 할 일 |
| --- | --- |
| __init__ | 거래·카테고리·예산 저장소를 받아 연결 |
| validate_transaction | 실제 날짜, 양수 정수 금액, income/expense, 등록된 카테고리 검증 |
| add_transaction | 검증 후 고유 id를 생성하고 저장, id 반환 |
| list_transactions | 기본 20건, 양수 limit 검증, 최신순 스트리밍 조회 |
| search_transactions | 포함 기간·카테고리·타입·메모 부분 문자열·태그 필터를 모두 적용하고 최신순으로 검색 |
| summarize_month | 구현: 월·top 검증, 수입·지출·잔액·카테고리 TOP N·예산 사용률·초과 여부 제공 |
| set_budget / get_budget | 구현: YYYY-MM 월과 양수 정수 금액 검증, 예산 저장·조회와 미설정 구분 |
| add_category / list_categories | 빈 이름·중복 검증, 카테고리 등록·조회 |
| remove_category | 사용 중인 카테고리 삭제 차단, 없는 이름 처리 |
| update_transaction | id 존재 확인, 제공된 수정 필드만 검증·반영하고 안전한 재작성 요청 |
| delete_transaction | id 존재 확인 후 해당 거래를 제외한 안전한 재작성 요청 |
| import_csv | CSV 스키마·행 검증, 새 id 생성, 성공·건너뜀 건수 반환 |
| export_csv | 월 또는 시작·종료일 조건 검증, CSV 생성과 처리 건수 반환 |

빈 카테고리 상태에서는 거래 추가를 막고 category add 안내에 필요한 오류를 전달할 예정입니다.
없는 거래 id는 오류로 구분하고, 거래가 없는 달은 CLI가 데이터 없음을 표시할 수 있게 전달합니다.
검색은 `iter_transactions`로 파일을 한 줄씩 읽어 조건을 모두 만족하는 거래만 고릅니다.
`--from`과 `--to`는 실제 날짜와 순서를 검증하며, `--type`은 income 또는 expense만 허용합니다.
메모 검색은 대소문자를 구분하지 않는 부분 문자열 검색이고 태그 검색은 태그 하나의 정확한 일치 검색입니다.
최신순 정렬에는 필터를 통과한 결과만 메모리에 보관하며, 결과가 없으면 CLI가 별도 메시지를 표시합니다.
`set_budget`은 같은 달의 기존 예산을 갱신하고, `get_budget`은 미설정 월에 `None`을 반환합니다.
CLI는 이 `None`을 이용해 예산이 0인 경우와 설정되지 않은 경우를 구분합니다.
`summarize_month`는 거래 제너레이터를 한 번 순회하며 해당 월의 합계와 카테고리별 지출을 누적합니다.
결과 사전은 `month`, `transaction_count`, `total_income`, `total_expense`, `balance`,
`top_expense_categories`, `budget`, `budget_usage_rate`, `is_over_budget` 키를 제공합니다.
지출 카테고리는 금액 내림차순으로 정렬하고, 같은 금액이면 카테고리 이름순으로 정렬합니다.
예산이 없으면 사용률과 초과 여부는 `None`이며, 거래가 없는 달은 `transaction_count`가 0입니다.
CSV는 UTF-8과 헤더를 사용하고 tags는 쉼표 구분 문자열로 변환합니다.
import_csv 반환 튜플은 (성공 건수, 건너뜀 건수) 순서로 계획합니다.
가져오기 오류 행 처리 정책은 구현 전에 확정해야 합니다.

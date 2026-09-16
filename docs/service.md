# service.py 구현 계획

BudgetService는 CLI가 받은 요청을 검증하고 저장소를 호출할 예정입니다.
화면 출력이나 직접 파일 입출력은 담당하지 않습니다. 아래 메서드는 모두 pass뿐입니다.

| 메서드 | 앞으로 할 일 |
| --- | --- |
| __init__ | 거래·카테고리·예산 저장소를 받아 연결 |
| validate_transaction | 실제 날짜, 양수 정수 금액, income/expense, 등록된 카테고리 검증 |
| add_transaction | 검증 후 고유 id를 생성하고 저장, id 반환 |
| list_transactions | 기본 20건, 양수 limit 검증, 최신순 스트리밍 조회 |
| search_transactions | 기간·카테고리·타입·메모·태그 필터와 최신순 스트리밍 검색 |
| summarize_month | 월·top 검증, 수입·지출·잔액·카테고리 TOP N·예산 사용률·초과 여부 제공 |
| set_budget / get_budget | 유효한 월과 양수 금액 검증, 예산 저장·조회 |
| add_category / list_categories | 빈 이름·중복 검증, 카테고리 등록·조회 |
| remove_category | 사용 중인 카테고리 삭제 차단, 없는 이름 처리 |
| update_transaction | id 존재 확인, 제공된 수정 필드만 검증·반영하고 안전한 재작성 요청 |
| delete_transaction | id 존재 확인 후 해당 거래를 제외한 안전한 재작성 요청 |
| import_csv | CSV 스키마·행 검증, 새 id 생성, 성공·건너뜀 건수 반환 |
| export_csv | 월 또는 시작·종료일 조건 검증, CSV 생성과 처리 건수 반환 |

빈 카테고리 상태에서는 거래 추가를 막고 category add 안내에 필요한 오류를 전달할 예정입니다.
없는 거래 id는 오류로 구분하고, 거래가 없는 달은 CLI가 데이터 없음을 표시할 수 있게 전달합니다.
예산 미설정과 빈 검색 결과도 구분할 예정입니다.
CSV는 UTF-8과 헤더를 사용하고 tags는 쉼표 구분 문자열로 변환합니다.
import_csv 반환 튜플은 (성공 건수, 건너뜀 건수) 순서로 계획합니다.
summary 결과 사전의 구체적인 키와 가져오기 오류 행 처리 정책은 구현 전에 확정해야 합니다.

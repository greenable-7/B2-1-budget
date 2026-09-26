# CLI와 Handler 구조

`cli.py`는 명령과 옵션 정의, 서비스 생성, 명령 분기를 담당합니다.
`handlers.py`는 대화형 입력, 서비스 호출에 필요한 값 변환, 결과 출력을 담당합니다.
현재 `add`, `list --limit`, `search`, `summary`, `budget set/show`, `category add/list/remove`, `update`, `delete`, `import`, `export`가 연결되어 있습니다.

| 모듈 | 함수 | 담당 명령·옵션 |
| --- | --- | --- |
| `cli.py` | `run` | 명령 분기, 전역 `--data-dir`, 모든 명령·하위 명령의 `--help` |
| `handlers.py` | `handle_add` | add: 날짜·타입·카테고리·금액·메모·태그 대화형 입력 |
| `handlers.py` | `handle_list` | list `--limit` (기본 20) |
| `handlers.py` | `handle_search` | search `--from --to --category --type --q --tag`; 여러 조건은 AND 검색 |
| `handlers.py` | `handle_summary` | summary `--month --top` (top 기본 5), 합계·TOP N·예산 상태 출력 |
| `handlers.py` | `handle_budget` | budget set `--month --amount` / budget show `--month` |
| `handlers.py` | `handle_category` | category add/list/remove; 추가·삭제 이름은 대화형 입력 |
| `handlers.py` | `handle_update` | update `--id` 및 `--date --type --category --amount --memo --tags` |
| `handlers.py` | `handle_delete` | delete `--id` |
| `handlers.py` | `handle_import` | import `--from` 및 성공·건너뜀 건수 출력 |
| `handlers.py` | `handle_export` | export `--out` 및 `--month` 또는 `--from`과 `--to`, 처리 건수 출력 |

update는 옵션 방식으로 고정합니다. 옵션 이름은 모두 -- 접두사를 사용합니다.
전역 --data-dir는 명령 앞에 두는 방식으로 계획하며 기본값은 ./data입니다.
`cli.py`는 파싱한 `--data-dir`로 서비스와 저장소를 만들고, 선택한 Handler에 서비스를 전달합니다.
`search`의 조건은 모두 선택 사항입니다. 결과는 `list`와 같은 형식으로 최신순 출력하며,
결과가 없으면 `검색 결과가 없습니다.`를 출력합니다.
`budget set`은 설정 완료 월과 금액을 출력합니다. `budget show`는 저장된 금액을 출력하고,
해당 월이 없으면 예산이 설정되지 않았다는 메시지를 출력합니다.
`summary`는 월별 수입·지출·잔액과 지출 카테고리 TOP N을 출력합니다.
예산이 설정됐으면 사용률과 정상·초과 상태를 표시하고, 없으면 `예산: 미설정`을 표시합니다.
해당 월에 거래가 없으면 합계 대신 거래 내역이 없다는 메시지를 출력합니다.
`update`는 `--id`가 필수이며 나머지 수정 옵션 중 하나 이상을 받아야 합니다.
입력된 옵션만 변경하며 빈 `--memo`와 `--tags`를 사용하면 기존 내용을 비울 수 있습니다.
`delete`는 `--id`로 지정한 거래 한 건을 삭제하고 완료된 ID를 출력합니다.
`import`는 `--from`으로 CSV 경로를 받고 성공·건너뜀 건수를 출력합니다.
`export`는 `--out`과 함께 `--month` 또는 `--from/--to` 조건을 받고 내보낸 건수와 경로를 출력합니다.

`__main__.py`는 `run`을 호출합니다. `handle_cli_errors`는 `run`에 한 번 적용해
`handlers.py`와 Service, Repository에서 전달된 오류를 공통 처리합니다.
현재 구현된 명령은 검증·파일 오류를 메시지와 종료 코드 1로 처리합니다.
실제 명령 예시는 README에 있으며 모든 계획 명령이 동작합니다.

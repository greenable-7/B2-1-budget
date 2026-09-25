# cli.py 구현 계획

CLI는 명령 해석, 대화형 입력, 결과 출력을 담당합니다.
현재 `add`, `list --limit`, `search`, `summary`, `budget set/show`, `category add/list/remove`, `update`가 연결되어 있습니다. 다른 명령 함수는 미구현입니다.

| 함수 | 앞으로 받을 명령·옵션 |
| --- | --- |
| run | 명령 분기, 전역 --data-dir, 모든 명령·하위 명령의 --help |
| handle_add | add: 날짜·타입·카테고리·금액·메모·태그 대화형 입력 |
| handle_list | list --limit (기본 20) |
| handle_search | search --from --to --category --type --q --tag; 여러 조건은 AND 검색 |
| handle_summary | 구현: summary --month --top (top 기본 5), 합계·TOP N·예산 상태 출력 |
| handle_budget | 구현: budget set --month --amount / budget show --month |
| handle_category | category add/list/remove; 추가·삭제 이름은 대화형 입력 |
| handle_update | 구현: update --id 및 --date --type --category --amount --memo --tags |
| handle_delete | delete --id |
| handle_import | import --from |
| handle_export | export --out 및 --month 또는 --from과 --to |

update는 옵션 방식으로 고정합니다. 옵션 이름은 모두 -- 접두사를 사용합니다.
전역 --data-dir는 명령 앞에 두는 방식으로 계획하며 기본값은 ./data입니다.
구현된 명령은 파싱한 `--data-dir`로 서비스와 저장소를 만들고 서비스에 요청합니다.
`search`의 조건은 모두 선택 사항입니다. 결과는 `list`와 같은 형식으로 최신순 출력하며,
결과가 없으면 `검색 결과가 없습니다.`를 출력합니다.
`budget set`은 설정 완료 월과 금액을 출력합니다. `budget show`는 저장된 금액을 출력하고,
해당 월이 없으면 예산이 설정되지 않았다는 메시지를 출력합니다.
`summary`는 월별 수입·지출·잔액과 지출 카테고리 TOP N을 출력합니다.
예산이 설정됐으면 사용률과 정상·초과 상태를 표시하고, 없으면 `예산: 미설정`을 표시합니다.
해당 월에 거래가 없으면 합계 대신 거래 내역이 없다는 메시지를 출력합니다.
`update`는 `--id`가 필수이며 나머지 수정 옵션 중 하나 이상을 받아야 합니다.
입력된 옵션만 변경하며 빈 `--memo`와 `--tags`를 사용하면 기존 내용을 비울 수 있습니다.

`__main__.py`는 `run`을 호출합니다. `handle_cli_errors`는 `run`에 한 번 적용했습니다.
현재 구현된 명령은 검증·파일 오류를 메시지와 종료 코드 1로 처리합니다.
실제 명령 예시는 README에 있으며 `add`, `list`, `search`, `summary`, `budget`, `category`, `update`가 동작합니다.

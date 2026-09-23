# cli.py 구현 계획

CLI는 명령 해석, 대화형 입력, 결과 출력을 담당합니다.
현재 `add`, `list --limit`, `category add/list/remove`가 연결되어 있습니다. 다른 명령 함수는 미구현입니다.

| 함수 | 앞으로 받을 명령·옵션 |
| --- | --- |
| run | 명령 분기, 전역 --data-dir, 모든 명령·하위 명령의 --help |
| handle_add | add: 날짜·타입·카테고리·금액·메모·태그 대화형 입력 |
| handle_list | list --limit (기본 20) |
| handle_search | search --from --to --category --type --q --tag |
| handle_summary | summary --month --top (top 기본 5) |
| handle_budget | budget set --month --amount / budget show --month |
| handle_category | category add/list/remove; 추가·삭제 이름은 대화형 입력 |
| handle_update | update --id 및 --date --type --category --amount --memo --tags |
| handle_delete | delete --id |
| handle_import | import --from |
| handle_export | export --out 및 --month 또는 --from과 --to |

update는 옵션 방식으로 고정합니다. 옵션 이름은 모두 -- 접두사를 사용합니다.
전역 --data-dir는 명령 앞에 두는 방식으로 계획하며 기본값은 ./data입니다.
구현된 명령은 파싱한 `--data-dir`로 서비스와 저장소를 만들고 서비스에 요청합니다.

`__main__.py`는 `run`을 호출합니다. `handle_cli_errors`는 `run`에 한 번 적용했습니다.
현재 구현된 명령은 검증·파일 오류를 메시지와 종료 코드 1로 처리합니다.
실제 명령 예시는 README에 있으며 `add`, `list`, `category`가 동작합니다.

# cli.py 구현 계획

CLI는 명령 해석, 대화형 입력, 결과 출력만 담당할 예정입니다.
현재 모든 함수는 pass뿐이며 argparse 구성, input 호출, 출력은 없습니다.

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
각 명령 함수에 전달할 파싱 결과와 서비스 인자는 argparse 구현 단계에서 구체화할 예정입니다.

기존 __main__.py는 run을 호출합니다. 현재 실행하면 출력 없이 종료합니다.
향후 handle_cli_errors를 run에만 한 번 적용하고 개별 명령에는 중복 적용하지 않을 예정입니다.
정상 종료는 0, 오류는 0이 아닌 코드와 원인·해결 힌트를 제공할 계획입니다.
실제 명령 예시는 README에 있으며 아직 동작하지 않습니다.

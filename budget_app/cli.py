# TODO: 전역 --data-dir와 명령별 --help를 구성하고 공통 오류 데코레이터를 이 진입점에만 적용한다.
def run() -> None:
    pass

# TODO: 날짜·타입·카테고리·금액·메모·태그를 대화형으로 입력받고 생성 id를 출력한다.
def handle_add() -> None:
    pass

# TODO: --limit 옵션으로 최신순 목록을 요청한다.
def handle_list() -> None:
    pass

# TODO: --from, --to, --category, --type, --q, --tag 옵션으로 검색한다.
def handle_search() -> None:
    pass

# TODO: --month, --top 옵션으로 월별 요약을 요청한다.
def handle_summary() -> None:
    pass

# TODO: budget set --month --amount와 budget show --month를 연결한다.
def handle_budget() -> None:
    pass

# TODO: category add/list/remove를 연결하고 추가·삭제할 이름을 대화형으로 입력받는다.
def handle_category() -> None:
    pass

# TODO: --id와 --date, --type, --category, --amount, --memo, --tags로 수정한다.
def handle_update() -> None:
    pass

# TODO: --id 옵션으로 거래 삭제를 요청한다.
def handle_delete() -> None:
    pass

# TODO: --from 옵션의 CSV를 가져오고 처리 건수를 출력한다.
def handle_import() -> None:
    pass

# TODO: --out과 --month 또는 --from/--to 조건으로 CSV를 내보낸다.
def handle_export() -> None:
    pass

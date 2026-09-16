# B2-1 Python 콘솔 가계부

파일 기반 가계부를 만들며 모듈 분리, 데이터 보호, 제너레이터, 데코레이터,
타입 힌트를 학습하는 프로젝트입니다. Python 3.10 이상과 표준 라이브러리만 사용합니다.

## 현재 단계

**뼈대만 작성했으며 모든 가계부 기능은 미구현입니다.**
클래스와 함수는 짧은 TODO 주석, 타입 힌트, `pass` 본문으로 구성했습니다.
`Transaction`의 필드와 dataclass 적용은 아직 미구현입니다.
반환 타입은 앞으로 구현할 계약이며, 현재 빈 메서드는 해당 값을 반환하지 않습니다.

프로젝트 루트에서 실행합니다.

```sh
python -m budget_app
```

현재 `__main__.py`는 `cli.run()`을 호출합니다. `run()`이 빈 함수이므로
출력이나 파일 변경 없이 종료합니다. 명령 해석, 입력, 도움말, 오류 처리는 미구현입니다.

## 현재 폴더 구조

```text
budget_app/
  __init__.py
  __main__.py
  cli.py
  model.py
  repository.py
  service.py
  decorator.py
data/
  .gitkeep
docs/
  model.md
  repository.md
  service.md
  cli.md
  decorator.md
README.md
```

CLI는 입력·출력, model은 거래 구조, repository는 파일 입출력,
service는 검증·비즈니스 규칙, decorator는 공통 오류 처리를 담당할 예정입니다.
각 모듈의 자세한 계획은 [docs](docs/cli.md)에 설명합니다.

## 예정된 10개 기능 — 모두 미구현

| 명령 | 구현할 기능 |
| --- | --- |
| add | 대화형 거래 입력, 검증, 저장, 고유 id 출력 |
| list | 최신순 목록, 기본 20건 및 --limit, 스트리밍 조회 |
| search | 기간·카테고리·타입·메모·태그 검색, 최신순 스트리밍 결과 |
| summary | 월별 수입·지출·잔액, 지출 TOP N, 예산 사용률·초과 경고, 데이터 없음 표시 |
| budget | 월별 예산 설정·조회 및 영구 저장 |
| category | 카테고리 추가·조회·삭제, 사용 중인 카테고리 삭제 차단 |
| update | 옵션으로 지정한 필드 수정, 없는 id 처리 |
| delete | id 기반 삭제, 없는 id 처리 |
| import | CSV 가져오기, 검증 및 처리 건수 출력 |
| export | 월 또는 시작·종료일 조건으로 CSV 내보내기, 처리 건수 출력 |

## 저장 계획 — 미구현

기본 경로는 프로젝트 루트에서 실행할 때의 `./data`이며, 전역 `--data-dir`로 변경할 예정입니다.
다음 세 파일은 **아직 생성하지 않았습니다**.

| 예정 파일 | 한 줄에 저장할 JSON 객체 |
| --- | --- |
| data/transactions.jsonl | 거래 한 건: id, type, date, amount, category, memo, tags |
| data/categories.jsonl | 카테고리 한 건: name |
| data/budgets.jsonl | 월 예산 한 건: month, amount |

모두 UTF-8 JSONL로 저장하며 한 줄에 JSON 객체 하나를 기록합니다.
전체 파일을 JSON 배열로 감싸지 않습니다. CSV는 가져오기·내보내기 형식으로만 사용합니다.
최초 실행에는 폴더와 없는 파일을 생성할 예정입니다.
카테고리가 비어 있으면 `category add`를 안내하고 거래 추가를 막는 방식을 선택합니다.
거래 읽기는 `yield` 기반 스트리밍, 수정·삭제는 임시 파일 작성 후 원자적 교체를 계획합니다.
최신순 출력과 스트리밍을 함께 만족할 읽기·정렬 전략은 추후 구현 단계에서 설계합니다.

## Transaction 필드 — 실제 필드 선언 미구현

추후 dataclass로 정의할 예정입니다.

| 필드 | 예정 타입·규칙 |
| --- | --- |
| id | str, 유일한 거래 식별자 |
| type | str, income 또는 expense |
| date | str, 유효한 날짜 YYYY-MM-DD |
| amount | int, 양수 정수 원 단위 |
| category | str, 등록된 카테고리 이름 |
| memo | str, 선택 입력, 기본 빈 문자열 |
| tags | list[str], 선택 입력, 기본 빈 목록 |

## 최종 명령 예시 — 현재는 모두 미구현

옵션은 `--`로 통일합니다. 모든 명령과 하위 명령에 `--help`를 제공할 예정입니다.
`add`는 대화형, `update`는 **옵션 방식**으로 고정합니다.
`category add/remove`는 이름을 대화형으로 입력받을 예정입니다.

```sh
python -m budget_app --help
python -m budget_app --data-dir ./data add
python -m budget_app list --limit 20
python -m budget_app search --from 2026-09-01 --to 2026-09-30 --category food --type expense --q 점심 --tag meal
python -m budget_app summary --month 2026-09 --top 3
python -m budget_app budget set --month 2026-09 --amount 500000
python -m budget_app budget show --month 2026-09
python -m budget_app category add
python -m budget_app category list
python -m budget_app category remove
python -m budget_app update --id TX-000001 --amount 12000 --memo 점심 --tags meal,lunch
python -m budget_app delete --id TX-000001
python -m budget_app import --from input.csv
python -m budget_app export --out output.csv --month 2026-09
python -m budget_app export --out output.csv --from 2026-09-01 --to 2026-09-30
```

`budget show`는 과제의 예산 조회를 위한 프로젝트 내 예정 명령입니다.
`export`는 월 조건 또는 시작일·종료일 조건이 필수입니다.
정상 종료 코드는 0, 오류 종료 코드는 0이 아닌 값으로 정할 예정입니다.
오류는 스택트레이스 대신 원인과 해결 힌트를 표시할 계획입니다.
공통 오류 데코레이터는 CLI 메인 진입 함수 `run()`에 한 번만 적용할 예정입니다.

## import/export CSV 최소 스키마 — 미구현

UTF-8, 헤더 포함이며 다음 열을 사용합니다. 선택 항목은 빈 값으로 둘 수 있습니다.

| 열 | 값 필수 | 규칙 |
| --- | --- | --- |
| date | Y | YYYY-MM-DD |
| type | Y | income / expense |
| category | Y | 등록된 카테고리 |
| amount | Y | 양수 정수 |
| memo | N | 문자열 |
| tags | N | 쉼표로 구분한 문자열 |

```csv
date,type,category,amount,memo,tags
2026-09-16,expense,food,12000,점심,"meal,lunch"
```

쉼표가 포함된 필드는 CSV 따옴표 규칙에 따라 처리할 예정입니다.
CSV에는 id 열이 없으므로 가져올 때 고유 id를 생성할 예정입니다.

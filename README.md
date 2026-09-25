# B2-1 Python 콘솔 가계부

파일 기반 가계부를 만들며 모듈 분리, 데이터 보호, 제너레이터, 데코레이터,
타입 힌트를 학습하는 프로젝트입니다. Python 3.10 이상과 표준 라이브러리만 사용합니다.

## 현재 단계

`category add/list/remove`, 대화형 `add`, `list --limit`, `search`, `summary`, `budget set/show`,
`update`, `delete`, `import`, `export`를 구현했습니다.
거래와 카테고리는 `--data-dir` 폴더의 JSONL 파일에 저장됩니다.
사용 중인 카테고리는 삭제할 수 없고, 잘못된 거래 입력은 오류 메시지와 종료 코드 1로 처리합니다.
`list`는 거래 파일을 한 줄씩 읽고 필요한 개수만 메모리에 유지해 날짜 최신순으로 출력합니다.
`Transaction`은 일반 클래스로 구현되어 있으며 dataclass는 적용하지 않았습니다.

프로젝트 루트에서 실행합니다.

```sh
python -m budget_app
```

계획한 모든 명령을 사용할 수 있습니다.
`--data-dir`는 명령 앞에 둡니다. Python 3.10 이상이 필요합니다.

처음 사용할 때는 `python -m budget_app category add`로 카테고리를 등록한 뒤
`python -m budget_app add`로 거래를 입력합니다.

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
service는 검증·비즈니스 규칙, decorator는 공통 오류 처리를 담당합니다.
각 모듈의 자세한 계획은 [docs](docs/cli.md)에 설명합니다.

## 기능별 진행 상태

| 명령 | 구현할 기능 |
| --- | --- |
| add | 구현: 대화형 거래 입력, 검증, 저장, 고유 id 출력 |
| list | 구현: 날짜 최신순 목록, 기본 20건 및 --limit, 스트리밍 조회 |
| search | 구현: 포함 기간·카테고리·타입·메모 키워드·태그의 AND 검색, 최신순 결과 |
| summary | 구현: 월별 수입·지출·잔액, 지출 TOP N, 예산 사용률·초과 경고, 데이터 없음 표시 |
| budget | 구현: 월별 예산 설정·조회, 같은 달 갱신 및 영구 저장 |
| category | 구현: 카테고리 추가·조회·삭제, 사용 중인 카테고리 삭제 차단 |
| update | 구현: 옵션으로 지정한 필드만 수정, 검증 실패·없는 id에서 원본 보존 |
| delete | 구현: id 기반 삭제, 없는 id에서 원본 보존 |
| import | 구현: CSV 가져오기, 행 검증, 새 ID 생성 및 성공·건너뜀 건수 출력 |
| export | 구현: 월 또는 시작·종료일 조건으로 CSV 내보내기, 처리 건수 출력 |

## 저장 형식

기본 경로는 프로젝트 루트에서 실행할 때의 `./data`이며, 전역 `--data-dir`로 변경할 수 있습니다.
거래·카테고리·예산 파일은 명령 실행 시 생성됩니다.

| 파일 | 한 줄에 저장할 JSON 객체 |
| --- | --- |
| data/transactions.jsonl | 거래 한 건: id, type, date, amount, category, memo, tags |
| data/categories.jsonl | 카테고리 한 건: name |
| data/budgets.jsonl | 월 예산 한 건: month, amount |

세 데이터 파일은 UTF-8 JSONL로 저장하며 한 줄에 JSON 객체 하나를 기록합니다.
전체 파일을 JSON 배열로 감싸지 않습니다. CSV는 가져오기·내보내기 형식으로만 사용합니다.
거래 추가 시 카테고리가 등록되지 않았다면 `category add`를 안내합니다.
거래 읽기는 `yield` 기반 스트리밍이며, 수정·삭제는 임시 파일 작성 후 원본을 교체합니다.
목록은 최신 N건만 메모리에 유지하고, 검색은 조건을 통과한 거래만 최신순으로 정렬합니다.

## Transaction 필드

현재 일반 클래스의 필드로 정의했습니다.

| 필드 | 타입·규칙 |
| --- | --- |
| id | str, 유일한 거래 식별자 |
| type | str, income 또는 expense |
| date | str, 유효한 날짜 YYYY-MM-DD |
| amount | int, 양수 정수 원 단위 |
| category | str, 등록된 카테고리 이름 |
| memo | str, 선택 입력, 기본 빈 문자열 |
| tags | list[str], 선택 입력, 기본 빈 목록 |

## 최종 명령 예시

옵션은 `--`로 통일합니다. 현재 구현된 명령은 `--help`를 제공합니다.
`add`는 대화형, `update`는 **옵션 방식**으로 고정합니다.
`category add/remove`는 이름을 대화형으로 입력받습니다.

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

`export`는 월 조건 또는 시작일·종료일 조건이 필수입니다.
현재 구현된 명령에서 정상 종료 코드는 0이고, 검증·파일 오류는 메시지를 출력한 뒤 1로 종료합니다.
공통 오류 데코레이터는 CLI 메인 진입 함수 `run()`에 한 번만 적용했습니다.

## import/export CSV 스키마

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

쉼표가 포함된 필드는 표준 CSV 따옴표 규칙에 따라 처리합니다.
CSV에는 id 열이 없으므로 가져올 때 고유 id를 생성합니다.
헤더가 잘못된 파일은 가져오지 않습니다. 헤더가 정상이라면 유효한 행은 저장하고 잘못된 행은 건너뛴 뒤 각각의 건수를 출력합니다.

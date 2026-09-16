from collections.abc import Callable
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


# TODO: CLI run에 한 번만 적용할 공통 오류 처리 데코레이터를 구현한다.
def handle_cli_errors(func: Callable[P, R]) -> Callable[P, R]:
    pass

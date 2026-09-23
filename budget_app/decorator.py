from collections.abc import Callable
from functools import wraps
import sys
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def handle_cli_errors(func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        try:
            return func(*args, **kwargs)
        except (ValueError, OSError, EOFError) as exc:
            print(f"오류: {exc}", file=sys.stderr)
            raise SystemExit(1) from None

    return wrapper

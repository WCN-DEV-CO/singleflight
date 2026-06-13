"""singleflight — collapse concurrent duplicate calls into one in-flight execution.

When N callers ask for the same key at the same time, only ONE does the work; the
rest wait and share its result. Classic thundering-herd / cache-stampede guard.
Original implementation of a well-known pattern (Go's golang.org/x/sync/singleflight).

Zero dependencies. Pure standard library. MIT licensed.
"""
from __future__ import annotations
import threading
from dataclasses import dataclass, field
from typing import Any, Callable

__version__ = "0.1.0"
__all__ = ["Group", "Call"]


@dataclass
class Call:
    event: threading.Event = field(default_factory=threading.Event)
    value: Any = None
    error: BaseException | None = None
    dups: int = 0          # how many callers shared this single execution


class Group:
    """Dedupes concurrent calls keyed by a string. The first caller for a key runs fn;
    concurrent callers for the same key block until it finishes and share the result."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._calls: dict[str, Call] = {}

    def do(self, key: str, fn: Callable[[], Any]) -> tuple[Any, bool]:
        """Returns (result, shared). `shared` is True if this caller did NOT execute fn
        but received another caller's result."""
        with self._lock:
            call = self._calls.get(key)
            if call is not None:
                call.dups += 1
                shared = True
            else:
                call = Call()
                self._calls[key] = call
                shared = False
        if shared:
            call.event.wait()
            if call.error is not None:
                raise call.error
            return call.value, True
        # leader executes
        try:
            call.value = fn()
        except BaseException as e:  # noqa: BLE001 — propagate to all waiters
            call.error = e
        finally:
            with self._lock:
                self._calls.pop(key, None)
            call.event.set()
        if call.error is not None:
            raise call.error
        return call.value, False

    def forget(self, key: str) -> None:
        with self._lock:
            self._calls.pop(key, None)

from dataclasses import dataclass

from pstg.domain.error_info import ErrorInfo


@dataclass
class RawBlockResult:
    fc: int
    addr: int
    count: int
    unit_id: int
    ok: bool
    registers: list[int] | None = None
    error: ErrorInfo | None = None
    duration_ms: float | None = None
    ts_block_end: float | None = None  # epoch seconds или time.time()

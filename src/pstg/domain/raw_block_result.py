from dataclasses import dataclass

from pstg.domain.error_info import ErrorInfo


@dataclass
class RawBlockResult:
    fc: int = 0
    addr: int = 0
    count: int = 0
    unit_id: int = 0
    ok: bool | None = None
    registers: list[int] | None = None
    error: ErrorInfo | None = None
    duration_ms: float | None = None
    ts_block_end: float | None = None  # epoch seconds или time.time()

from dataclasses import dataclass, field

from pstg.domain.connection_state import ConnectionState
from pstg.domain.raw_block_result import RawBlockResult
from pstg.domain.signal_value import SignalValue


@dataclass
class PollResult:
    run_id: str = ""
    poll_seq: int = 0
    ts_poll_start: float = 0
    ts_poll_end: float = 0
    connection_state: ConnectionState | None = None  # "UP" | "DOWN"
    blocks: list[RawBlockResult] = field(default_factory=list)

    # 20260301
    signals: dict[str, SignalValue] = field(default_factory=dict)

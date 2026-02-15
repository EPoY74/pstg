from dataclasses import dataclass, field

from pstg.domain.raw_block_result import RawBlockResult
from pstg.domain.connection_state import ConnectionState


@dataclass
class PollResult:
    poll_seq: int = 0
    ts_poll_start: float = 0
    ts_poll_end: float = 0
    connection_state: ConnectionState | None = None  # "UP" | "DOWN"
    blocks: list[RawBlockResult] = field(default_factory=list)

from dataclasses import dataclass

from pstg.domain.raw_block_result import RawBlockResult
from pstg.domain.connection_state import ConnectionState


@dataclass
class PollResult:
    poll_seq: int
    ts_poll_start: float
    ts_poll_end: float
    connection_state: ConnectionState  # "UP" | "DOWN"
    blocks: list[RawBlockResult]

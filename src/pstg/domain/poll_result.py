from dataclasses import dataclass

from domain.raw_block_result import RawBlockResult
from domain.connection_state import ConnectionState


@dataclass
class PollResult:
    poll_seq: int
    ts_poll_start: float
    ts_poll_end: float
    connection_state: ConnectionState  # "UP" | "DOWN"
    blocks: list[RawBlockResult]

from dataclasses import dataclass

from domain.raw_block_result import RawBlockResult


@dataclass
class PollResult:
    poll_seq: int
    ts_poll_start: float
    ts_poll_end: float
    connection_state: str  # "UP" | "DOWN"
    blocks: list[RawBlockResult]

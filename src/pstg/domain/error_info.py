from dataclasses import dataclass

from pstg.domain.kind_state import KindState


@dataclass
class ErrorInfo:
    message: str
    kind: KindState | None = None  # "TRANSPORT" | "DEVICE"
    exception_code: int | None = None  # для device, если есть
    exc_type: str | None = None  # для transport, если есть

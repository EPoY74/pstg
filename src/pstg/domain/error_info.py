from dataclasses import dataclass

from pstg.domain.kind_state import KindState


@dataclass
class ErrorInfo:
    kind: KindState  # "TRANSPORT" | "DEVICE"
    message: str
    exception_code: int | None = None  # для device, если есть
    exc_type: str | None = None  # для transport, если есть

from dataclasses import dataclass


@dataclass
class ErrorInfo:
    kind: str  # "transport" | "device"
    message: str
    exception_code: int | None = None  # для device, если есть
    exc_type: str | None = None  # для transport, если есть

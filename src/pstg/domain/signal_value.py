from dataclasses import dataclass

from pstg.domain.signal_sourse import SignalSource


@dataclass
class SignalValue:
    value: float | None  # None если нет валидного значения
    unit: str  # "bar"
    ok: bool  # True если value валиден
    ts: float  # epoch seconds
    source: SignalSource | None  # откуда декодировали
    error: str | None = None  # коротко, если ok=False

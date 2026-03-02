from dataclasses import dataclass

from pstg.domain.signal_sourse import SignalSource


@dataclass
class SignalValue:
    # Значение сигнала или None если нет валидного значения
    value: float = 0.0

    # "bar"
    unit: str = ""

    # True если value валиден
    ok: bool = False

    # epoch seconds
    ts: float = 0.0

    # откуда декодировали
    source: SignalSource | None = None

    # коротко, если ok=False
    error: str | None = None

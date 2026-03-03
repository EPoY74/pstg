from dataclasses import dataclass
from typing import Literal

from pstg.domain.signal_word_order import SignalWordOrder


@dataclass(frozen=True)
class SignalSpec:
    """
    Спецификация считываемого сигнала
    """

    signal_name: str  # Наименование датчика (сигнала)"pt1", "pt2"
    fc: int  # Номер типа регистра откуда читаем 3 или 4
    addr: int  # стартовый адрес (offset/смещение)
    dtype: Literal["u16", "s16", "u32", "s32", "f32"]  # тип данных
    word_order: SignalWordOrder = SignalWordOrder.LITTLE  # Порядок байт в слове
    unit: str = ""  # Единица измерения сигнала "bar", "rpm", ...

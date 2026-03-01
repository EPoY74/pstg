from dataclasses import dataclass
from typing import Literal

from pstg.domain.signal_word_order import SignalWordOrder


@dataclass(frozen=True)
class SignalSpec:
    signal_name: str  # "pt1", "pt2"
    fc: int  # 3 или 4
    addr: int  # стартовый адрес (offset/смещение)
    dtype: Literal["u16", "s16", "u32", "s32", "f32"]  # тип данных
    word_order: SignalWordOrder = SignalWordOrder.LITTLE
    unit: str = ""  # "bar", "rpm", ...

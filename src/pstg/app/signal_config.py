from pstg.domain.signal_spec import SignalSpec
from pstg.domain.signal_word_order import SignalWordOrder

SIGNALS_START_ADDR: int = 56
SIGNALS_COUNT: int = 12

SIGNALS: list[SignalSpec] = [
    SignalSpec("PT1", 3, 56, "f32", SignalWordOrder.LITTLE, "Bar"),
    SignalSpec("PT2", 3, 58, "f32", SignalWordOrder.LITTLE, "Bar"),
    SignalSpec("PT3", 3, 60, "f32", SignalWordOrder.LITTLE, "Bar"),
    SignalSpec("FlowPerHour", 3, 64, "f32", SignalWordOrder.LITTLE, "m3/h"),
    SignalSpec("FlowAmount", 3, 66, "f32", SignalWordOrder.LITTLE, "m3"),
]

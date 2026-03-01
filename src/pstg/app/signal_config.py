from pstg.domain.signal_spec import SignalSpec
from pstg.domain.signal_word_order import SignalWordOrder

SIGNALS: list[SignalSpec] = [
    SignalSpec("PT1", 3, 56, "f32", SignalWordOrder.LITTLE, "Bar"),
    SignalSpec("PT2", 3, 56, "f32", SignalWordOrder.LITTLE, "Bar"),
    SignalSpec("PT3", 3, 56, "f32", SignalWordOrder.LITTLE, "Bar"),
    SignalSpec("FlowPerHour", 3, 56, "f32", SignalWordOrder.LITTLE, "m3/h"),
    SignalSpec("FlowAmount", 3, 56, "f32", SignalWordOrder.LITTLE, "m3"),
]

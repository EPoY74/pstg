from pstg.domain.signal_spec import SignalSpec
from pstg.domain.signal_word_order import SignalWordOrder
from pstg.domain.signals_modbus_device_settings import (
    SignalsModbusDeviceSettings,
)


def get_signals_config() -> SignalsModbusDeviceSettings:

    SIGNALS_START_ADDR: int = 56
    SIGNALS_COUNT: int = 12

    SIGNALS: list[SignalSpec] = [
        SignalSpec("PT1", 3, 56, "f32", SignalWordOrder.LITTLE, "Bar"),
        SignalSpec("PT2", 3, 58, "f32", SignalWordOrder.LITTLE, "Bar"),
        SignalSpec("PT3", 3, 60, "f32", SignalWordOrder.LITTLE, "Bar"),
        SignalSpec("FlowPerHour", 3, 64, "f32", SignalWordOrder.LITTLE, "m3/h"),
        SignalSpec("FlowAmount", 3, 66, "f32", SignalWordOrder.LITTLE, "m3"),
    ]

    return SignalsModbusDeviceSettings(
        offset=SIGNALS_START_ADDR, read_count=SIGNALS_COUNT, signals_map=SIGNALS
    )

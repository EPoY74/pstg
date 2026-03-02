"""
Читает сигналы из контроллеры по указанным адресам
"""

from pymodbus.client import AsyncModbusTcpClient

# import pstg.app.modbus_config
# import pstg.app.read_config
# import pstg.app.read_signal_config
from pstg.app.read_signal_config import get_signals_config
from pstg.domain.poll_result import PollResult
from pstg.domain.registers_modbus_device_settings import (
    RegistersModbusDeviceSettings,
)
from pstg.domain.signal_value import SignalValue
from pstg.domain.signals_modbus_device_settings import (
    SignalsModbusDeviceSettings,
)
from pstg.drivers.read_registers_safely import read_registers_safely


async def read_signals(
    fc: int,
    device_being_polled: AsyncModbusTcpClient,
    device_poll_settings: RegistersModbusDeviceSettings,
    signals_setting: SignalsModbusDeviceSettings,
) -> dict[str, SignalValue]:
    was_read_signals: PollResult = PollResult()

    # signal_config: SignalsModbusDeviceSettings = get_signals_config()

    # Формирую
    signals_polling_setting = RegistersModbusDeviceSettings(
        device_id=device_poll_settings.device_id,
        offset=signals_setting.offset,
        read_count=signals_setting.read_count,
    )
    was_read_signals = await read_registers_safely(
        device_being_polled, signals_polling_setting
    )
    parsed_signal = was_read_signals.blocks[0].registers
    print()
    print(
        "Signals:",
        parsed_signal,
    )
    print()
    pt1 = device_being_polled.convert_from_registers(
        parsed_signal[0:2],
        device_being_polled.DATATYPE.FLOAT32,
        word_order="little",
    )
    pt2 = device_being_polled.convert_from_registers(
        parsed_signal[2:4],
        device_being_polled.DATATYPE.FLOAT32,
        word_order="little",
    )
    pt3 = device_being_polled.convert_from_registers(
        parsed_signal[4:6],
        device_being_polled.DATATYPE.FLOAT32,
        word_order="little",
    )
    flow_per_hour = device_being_polled.convert_from_registers(
        parsed_signal[6:8],
        device_being_polled.DATATYPE.FLOAT32,
        word_order="little",
    )
    flow_amount = device_being_polled.convert_from_registers(
        parsed_signal[8:10],
        device_being_polled.DATATYPE.FLOAT32,
        word_order="little",
    )
    print(f"pt1: {pt1}\n")
    print(f"pt2: {pt2}\n")
    print(f"pt3: {pt3}\n")
    print(f"flow per hour:: {flow_per_hour}\n")
    print(f"flow amount: {flow_amount}\n")
    return {"pt1": SignalValue()}

import sys
import time

from pymodbus.client import AsyncModbusTcpClient

from pstg.domain.registers_modbus_device_settings import (
    RegistersModbusDeviceSettings,
)
from pstg.domain.signal_sourse import SignalSource
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
    signal_value: float = -sys.float_info.max
    signals_polling_setting = RegistersModbusDeviceSettings(
        device_id=device_poll_settings.device_id,
        offset=signals_setting.start_address_of_block,
        read_count=signals_setting.read_count,
        fc=signals_setting.fc,
        enable_signals_reading=True,
    )
    was_read_signals = await read_registers_safely(
        device_being_polled, signals_polling_setting
    )
    ts = time.time()
    if not was_read_signals.blocks or not was_read_signals.blocks[0].registers:
        return {
            signal.signal_name: SignalValue(
                unit=signal.unit,
                ok=False,
                ts=ts,
                error="Failed to read signals",
            )
            for signal in signals_setting.signals_map
        }

    parsed_signal = was_read_signals.blocks[0].registers
    output: dict[str, SignalValue] = {}
    for signal in signals_setting.signals_map:
        register_count = 2 if signal.dtype == "f32" else 1
        start = signal.addr - signals_setting.start_address_of_block
        raw_registers = parsed_signal[start : start + register_count]

        if signal.dtype != "f32" or len(raw_registers) != register_count:
            output[signal.signal_name] = SignalValue(
                unit=signal.unit,
                ok=False,
                ts=ts,
                error="Unsupported or incomplete signal data",
            )
            continue

        temp_value = device_being_polled.convert_from_registers(
            raw_registers,
            device_being_polled.DATATYPE.FLOAT32,
            word_order="little",
        )
        if isinstance(temp_value, float):
            signal_value = temp_value
        output[signal.signal_name] = SignalValue(
            value=float(signal_value),
            unit=signal.unit,
            ok=True,
            ts=ts,
            source=SignalSource(
                fc=fc,
                address=signal.addr,
                count=register_count,
                device_id=signals_polling_setting.device_id,
                word_odder=signal.word_order,
            ),
        )
    return output

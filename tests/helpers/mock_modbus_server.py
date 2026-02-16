# tests/helpers/mock_modbus_server.py
from pymodbus.datastore import (
    ModbusSequentialDataBlock,
    ModbusDeviceContext,
    ModbusServerContext,
)


def build_context() -> ModbusServerContext:
    # 0..99 регистров/коилов для простоты
    di = ModbusSequentialDataBlock(0, [False] * 100)
    co = ModbusSequentialDataBlock(0, [False] * 100)
    ir = ModbusSequentialDataBlock(0, [0] * 100)   # Input Registers (FC04)
    hr = ModbusSequentialDataBlock(0, [0] * 100)   # Holding Registers (FC03)

    dev = ModbusDeviceContext(di=di, co=co, ir=ir, hr=hr)

    # single=False => можно разнести разные device_id по разным контекстам
    return ModbusServerContext(devices={1: dev}, single=False)

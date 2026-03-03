# Проверяет успешное чтение блока и заполнение метаданных.
import asyncio

from pstg.domain.registers_modbus_device_settings import (
    RegistersModbusDeviceSettings,
)
from pstg.drivers.read_block import read_block


class SuccessfulResponse:
    def __init__(self, registers: list[int]) -> None:
        self.registers = registers

    def isError(self) -> bool:
        return False


async def successful_reader(*args, **kwargs) -> SuccessfulResponse:
    return SuccessfulResponse(registers=[10, 20, 30])


def test_read_block_returns_successful_block_with_registers() -> None:
    settings = RegistersModbusDeviceSettings(
        device_id=1, offset=5, read_count=3, fc=4
    )

    block, got_response = asyncio.run(
        read_block(successful_reader, 4, object(), settings)
    )

    assert got_response is True
    assert block.ok is True
    assert block.fc == 4
    assert block.unit_id == 1
    assert block.addr == 5
    assert block.count == 3
    assert block.registers == [10, 20, 30]
    assert block.current_error_info is None
    assert block.duration_ms is not None
    assert block.ts_block_end is not None

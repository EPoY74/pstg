#   Проверяет device error: got_response=True, ok=False, ошибка заполнена,
#  регистры сохраняются.

import asyncio

from pstg.domain.kind_state import KindState
from pstg.domain.registers_modbus_device_settings import (
    RegistersModbusDeviceSettings,
)
from pstg.drivers.read_block import read_block


class DeviceErrorResponse:
    def __init__(self, exception_code: int, registers: list[int]) -> None:
        self.exception_code = exception_code
        self.registers = registers

    def isError(self) -> bool:
        return True


async def device_error_reader(*args, **kwargs) -> DeviceErrorResponse:
    # Регистр тоже возвращаем, потому что в текущем контракте проекта
    # сырые данные при device error сохраняются для анализа.
    return DeviceErrorResponse(exception_code=2, registers=[99, 100])


def test_read_block_marks_device_error_but_keeps_response() -> None:
    settings = RegistersModbusDeviceSettings(
        device_id=1, offset=0, read_count=2
    )

    block, got_response = asyncio.run(
        read_block(device_error_reader, 4, object(), settings)
    )

    assert got_response is True
    assert block.ok is False
    assert block.registers == [99, 100]
    assert block.current_error_info is not None
    assert block.current_error_info.kind == KindState.DEVICE
    assert block.current_error_info.exception_code == 2

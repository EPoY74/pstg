import logging
import time

from pymodbus.client import AsyncModbusTcpClient

from pstg.domain.connection_state import ConnectionState
from pstg.domain.poll_result import PollResult
from pstg.domain.registers_modbus_device_settings import (
    RegistersModbusDeviceSettings,
)
from pstg.drivers.read_block import read_block
from pstg.drivers.read_fc03_holding_register import read_fc03_holding_register
from pstg.drivers.read_fc04_input_regoster import read_fc04_input_register

logger = logging.getLogger(__name__)


def _get_connection_state(is_correct: bool) -> ConnectionState:
    return ConnectionState.UP if is_correct else ConnectionState.DOWN


async def read_registers_safely(
    device_being_polled: AsyncModbusTcpClient,
    device_poll_settings: RegistersModbusDeviceSettings,
) -> PollResult:
    readed_poll_result = PollResult(connection_state=ConnectionState.DOWN)
    readed_poll_result.ts_poll_start = time.time()

    if device_poll_settings.fc == 3:
        read_func = read_fc03_holding_register
    elif device_poll_settings.fc == 4:
        read_func = read_fc04_input_register
    else:
        raise RuntimeError(f"Unsupported function code: {device_poll_settings.fc}")

    try:
        raw_readed_data, got_response = await read_block(
            read_func,
            device_poll_settings.fc,
            device_being_polled,
            device_poll_settings,
        )
        readed_poll_result.connection_state = _get_connection_state(
            got_response
        )
        readed_poll_result.blocks.append(raw_readed_data)
    except RuntimeError as err:
        logger.error("Ошибка: %s", err)

    readed_poll_result.ts_poll_end = time.time()
    return readed_poll_result

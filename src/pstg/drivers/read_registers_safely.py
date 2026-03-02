import asyncio
import logging
import time

from pymodbus.client import AsyncModbusTcpClient

from pstg.domain.connection_state import ConnectionState
from pstg.domain.kind_state import KindState
from pstg.domain.poll_result import PollResult
from pstg.domain.raw_block_result import RawBlockResult
from pstg.domain.registers_modbus_device_settings import (
    RegistersModbusDeviceSettings,
)
from pstg.drivers.read_block import read_block
from pstg.drivers.read_fc03_holding_register import read_fc03_holding_register
from pstg.drivers.read_fc04_input_regoster import read_fc04_input_register

logger = logging.getLogger(__name__)


def init_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def _get_connection_state(is_correct: bool) -> ConnectionState:
    return ConnectionState.UP if is_correct else ConnectionState.DOWN


RECONNECT_DELAY_S: int = 10


async def _reconnect_break(reason: str) -> None:
    logger.warning("%s: Ожидаю %s секунд", reason, RECONNECT_DELAY_S)
    await asyncio.sleep(RECONNECT_DELAY_S)
    logger.warning("%s: Прерываю для переподключения", reason)


async def read_registers_safely(
    device_being_polled: AsyncModbusTcpClient,
    device_poll_settings: RegistersModbusDeviceSettings,
) -> PollResult:

    readed_poll_result: PollResult = PollResult()

    readed_poll_result.connection_state = ConnectionState.DOWN

    raw_readed_data_fc04: RawBlockResult = RawBlockResult()
    raw_readed_data_fc03: RawBlockResult = RawBlockResult()

    full_read_start_time: float = 0.0
    full_read_end_time: float = 0.0
    full_read_start_time = time.time()

    got_response_04: bool = False

    try:
        logger.info("Читаю регистры fc04")
        (raw_readed_data_fc04, got_response_04) = await read_block(
            read_fc04_input_register,
            4,
            device_being_polled,
            device_poll_settings,
        )
        readed_poll_result.connection_state = _get_connection_state(
            got_response_04
        )
    except RuntimeError as err:
        logger.error("Ошибка: %s", err)

    if (raw_readed_data_fc04.current_error_info) and (
        raw_readed_data_fc04.current_error_info.kind == KindState.DEVICE
    ):
        try:
            got_response_03: bool = False
            logger.info("Читаю регистры fc03")
            (raw_readed_data_fc03, got_response_03) = await read_block(
                read_fc03_holding_register,
                3,
                device_being_polled,
                device_poll_settings,
            )
            readed_poll_result.connection_state = _get_connection_state(
                got_response_04 or got_response_03
            )
        except RuntimeError as err:
            logger.error("Ошибка: %s", err)

    full_read_end_time = time.time()
    readed_poll_result.blocks.append(raw_readed_data_fc04)
    readed_poll_result.blocks.append(raw_readed_data_fc03)

    readed_poll_result.ts_poll_start = full_read_start_time
    readed_poll_result.ts_poll_end = full_read_end_time

    return readed_poll_result

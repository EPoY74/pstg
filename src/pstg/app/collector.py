# запуск:  uv run python -m pstg.app.collector
# перед запуском может понадобиться выполнение команд:
# uv sync
# uv pip install -e .   - Использовать в проде запрещено!!!!

import asyncio
import logging
import time
from collections.abc import AsyncIterator

from pymodbus.client import AsyncModbusTcpClient

from pstg.app.modbus_corfig import get_modbus_config
from pstg.app.read_config import get_device_read_settings
from pstg.domain.connection_state import ConnectionState
from pstg.domain.kind_state import KindState
from pstg.domain.modbus_config import ModbusConfig
from pstg.domain.modbus_device_read_settings import ModbusDeviceReadSettings
from pstg.domain.poll_result import PollResult
from pstg.domain.raw_block_result import RawBlockResult
from pstg.drivers.open_connection_modbus_tcp import open_connection_modbus_tcp
from pstg.drivers.read_block import read_block
from pstg.drivers.read_fc03_holding_register import read_fc03_holding_register
from pstg.drivers.read_fc04_input_regoster import read_fc04_input_register

logger = logging.getLogger(__name__)


# Выше данной функции другие фунции не писать! Только импорты и т.д.!
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


async def poll_device(
    device_being_polled: AsyncModbusTcpClient,
    device_poll_settings: ModbusDeviceReadSettings,
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


async def poll_forever(
    device_config: ModbusConfig, device_poll_settings: ModbusDeviceReadSettings
) -> AsyncIterator[PollResult]:

    poll_result: PollResult = PollResult()
    time_start: float = 0
    time_end: float = 0

    device_being_polled: AsyncModbusTcpClient | None = None
    while True:
        try:
            logger.info("Запуск цикла опроса.")
            logger.info(
                "Поднимаю коннект по ip %s порт %s",
                device_config.host,
                device_config.port,
            )
            while True:
                try:
                    time_start = time.time()
                    device_being_polled = await open_connection_modbus_tcp(
                        device_config.host, device_config.port
                    )
                    break
                except ConnectionError as err:
                    time_end = time.time()

                    poll_result.connection_state = ConnectionState.DOWN
                    poll_result.ts_poll_start = time_start
                    poll_result.ts_poll_end = time_end
                    yield poll_result

                    logger.error("Клиент не подключен: %s", err)
                    logger.warning(
                        "Попытка повторного подключения через 30 секунд"
                    )
                    await asyncio.sleep(30)
                    logger.warning("Повторное подключение...")
                    continue

            logger.info(
                "Коннект по ip %s порт %s поднят успешно!",
                device_config.host,
                device_config.port,
            )
            while True:
                try:
                    poll_result = await poll_device(
                        device_being_polled, device_poll_settings
                    )
                    yield poll_result
                    if poll_result.connection_state == ConnectionState.DOWN:
                        logger.warning("Проблема с подключением к устройству.")
                        await _reconnect_break("Dconnection_state=DOWN")
                        break

                    #  TODO реализовать задержку, что бы она
                    # не плавала. Высчитывать, сколько будет между ними

                    await asyncio.sleep(device_config.poll_interval_s)
                except RuntimeError as err:
                    logger.error("Runtime Error: Ошибка: %s", err)
                    # Это страховка. Скорее всего это не нужно
                    # Но лишним - не будет
                    await _reconnect_break("Runtime Error")
                    break

        finally:
            logger.info(
                "Закрываю Коннект по ip %s порт %s!",
                device_config.host,
                device_config.port,
            )
            if device_being_polled:
                device_being_polled.close()
            logger.info("Коннект закрыт")


async def main() -> None:
    async for result in poll_forever(
        get_modbus_config(), get_device_read_settings()
    ):
        logger.info("%s", result)
    return


if __name__ == "__main__":
    # device_config: ModbusConfig = await get_modbus_config()
    # ✅ Настройка логов только при запуске как скрипт
    try:
        init_logging()

        logger.info("Запуск Pump Station Telemetry Gateway")
        asyncio.run(main(), debug=False)

    except KeyboardInterrupt:
        logger.info("Пользователь нажал Ctrl+C")
    finally:
        logger.info("Остановка Pump Station Telemetry Gateway")

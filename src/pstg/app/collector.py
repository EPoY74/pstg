import asyncio
import copy
import logging
import time
from collections.abc import AsyncIterator

from pymodbus.client import AsyncModbusTcpClient

from pstg.app.modbus_config import get_modbus_config
from pstg.app.read_config import get_device_read_settings
from pstg.app.read_signal_config import get_signals_config
from pstg.domain.connection_state import ConnectionState
from pstg.domain.modbus_config import ModbusConfig
from pstg.domain.poll_result import PollResult
from pstg.domain.registers_modbus_device_settings import (
    RegistersModbusDeviceSettings,
)
from pstg.drivers.open_connection_modbus_tcp import open_connection_modbus_tcp
from pstg.drivers.read_registers_safely import read_registers_safely
from pstg.drivers.read_signals import read_signals

logger = logging.getLogger(__name__)


def init_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


RECONNECT_DELAY_S = 10


async def _reconnect_break(reason: str) -> None:
    logger.warning("%s: Ожидаю %s секунд", reason, RECONNECT_DELAY_S)
    await asyncio.sleep(RECONNECT_DELAY_S)
    logger.warning("%s: Прерываю для переподключения", reason)


async def poll_device(
    device_being_polled: AsyncModbusTcpClient,
    device_poll_settings: RegistersModbusDeviceSettings,
) -> PollResult:
    return await read_registers_safely(
        device_being_polled, device_poll_settings
    )


async def poll_forever(
    device_config: ModbusConfig,
    device_poll_settings: RegistersModbusDeviceSettings,
) -> AsyncIterator[PollResult]:
    poll_result = PollResult()
    time_start = 0.0
    time_end = 0.0

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
                    if device_poll_settings.enable_signals_reading:
                        poll_result.signals = copy.deepcopy(
                            await read_signals(
                                3,
                                device_being_polled,
                                device_poll_settings,
                                get_signals_config(),
                            )
                        )
                    yield poll_result
                    if poll_result.connection_state == ConnectionState.DOWN:
                        logger.warning("Проблема с подключением к устройству.")
                        await _reconnect_break("connection_state=DOWN")
                        break

                    await asyncio.sleep(device_config.poll_interval_s)
                except RuntimeError as err:
                    logger.error("Runtime Error: Ошибка: %s", err)
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
        logger.info("%s \n\n", result)


if __name__ == "__main__":
    try:
        init_logging()
        logger.info("Запуск Pump Station Telemetry Gateway")
        asyncio.run(main(), debug=False)
    except KeyboardInterrupt:
        logger.info("Пользователь нажал Ctrl+C")
    finally:
        logger.info("Остановка Pump Station Telemetry Gateway")
        for i in range(5, 0, -1):
            logger.info(
                "Остановка Pump Station Telemetry Gateway через %d секунд", i
            )
            asyncio.run(asyncio.sleep(1))
        logger.info("Pump Station Telemetry Gateway остановлен")

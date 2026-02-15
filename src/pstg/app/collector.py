import asyncio
import logging
import time
from typing import AsyncIterator

from pymodbus.client import AsyncModbusTcpClient
from pymodbus.pdu import ModbusPDU


from pstg.app.modbus_corfig import get_modbus_config
from pstg.app.read_config import get_device_read_settings

from pstg.domain.error_info import ErrorInfo
from pstg.domain.kind_state import KindState
from pstg.domain.connection_state import ConnectionState
from pstg.domain.modbus_device_read_settings import ModbusDeviceReadSettings
from pstg.domain.modbus_config import ModbusConfig
from pstg.drivers.open_connection_modbus_tcp import open_connection_modbus_tcp
from pstg.domain.poll_result import PollResult
from pstg.domain.raw_block_result import RawBlockResult
from pstg.drivers.read_fc03_holding_register import read_fc03_holding_register
from pstg.drivers.read_fc04_input_regoster import read_fc04_input_register

logger = logging.getLogger(__name__)


# Выше данной функции другие фунции не писать! Только импорты и т.д.!
def init_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


async def poll_device(
    device_being_polled: AsyncModbusTcpClient,
    device_poll_settings: ModbusDeviceReadSettings,

    readed_data: ModbusPDU | None = None
):
    readed_poll_result: PollResult = PollResult()

    readed_poll_result.connection_state = ConnectionState.DOWN

    raw_readed_data_fc04: RawBlockResult = RawBlockResult()
    raw_readed_data_fc03: RawBlockResult = RawBlockResult()

    raw_error_info: ErrorInfo | None = None

    is_not_correct_reading_fc04: bool | None = None

    read_stop_time: float = 0.0
    read_end_time: float = 0.0
    duration_ms: float = 0.0
    full_read_start_time: float = 0.0
    full_read_end_time: float = 0.0

    try:

        logger.info("Читаю регистры fc04")
        full_read_start_time = time.time()               # когда начали (epoch)
        # старт измерения длительности (монотонно)
        read_start_time: float = time.perf_counter()

        readed_data = await read_fc04_input_register(
            device_being_polled,
            offset=device_poll_settings.offset,
            read_count=device_poll_settings.read_count,
            plc_id=device_poll_settings.device_id,
        )
        if readed_data and readed_data.isError is not True:
            raw_readed_data_fc04.ok = True

        read_stop_time = time.perf_counter()
        read_end_time = time.time()             # когда закончили (epoch)
        duration_ms = (read_stop_time - read_start_time) * 1000

        is_not_correct_reading_fc04 = False

        if readed_data and (readed_data.isError() is True):
            raw_readed_data_fc04.ok = False
            exception_code = readed_data.exception_code
            is_not_correct_reading_fc04 = True
            err_message = "1. Ошибка от PLC. Регистры - fc04"
            logger.warning(err_message)
            logger.warning("Код ошибки: %s", exception_code)

            if raw_error_info is None:
                raw_error_info = ErrorInfo(
                    exception_code=exception_code, message=err_message, kind=KindState.DEVICE)

            if raw_readed_data_fc04.error is None:
                raw_readed_data_fc04.error = raw_error_info

    except RuntimeError as err:
        raw_readed_data_fc04.ok = False
        is_not_correct_reading_fc04 = True
        err_message = "2. Ошибка от PLC. Регистры - fc04"
        logger.warning(err_message)
        logger.warning("RuntimeError: %s", err)
        if raw_error_info is None:
            raw_error_info = ErrorInfo(
                exception_code=None, message=err_message, kind=KindState.TRANSPORT)

    finally:
        if readed_data:
            raw_readed_data_fc04.ok = True
            raw_readed_data_fc04.fc = 4
            raw_readed_data_fc04.unit_id = device_poll_settings.device_id
            raw_readed_data_fc04.addr = device_poll_settings.offset
            raw_readed_data_fc04.count = device_poll_settings.read_count
            raw_readed_data_fc04.registers = readed_data.registers[:]
            raw_readed_data_fc04.duration_ms = duration_ms
            raw_readed_data_fc04.ts_block_end = read_end_time
            if raw_readed_data_fc04 and raw_error_info:
                raw_readed_data_fc04.error = ErrorInfo(
                    message=raw_error_info.message, kind=raw_error_info.kind, exception_code=raw_error_info.exception_code, exc_type=raw_error_info.exc_type)
        if raw_error_info:
            readed_data = None

    if is_not_correct_reading_fc04:
        try:
            logger.info("Читаю регистры fc03")
            # старт измерения длительности (монотонно)
            read_start_time = time.perf_counter()

            readed_data = await read_fc03_holding_register(
                device_being_polled,
                offset=device_poll_settings.offset,
                read_count=device_poll_settings.read_count,
                plc_id=device_poll_settings.device_id,
            )
            if readed_data and readed_data.isError is not True:
                raw_readed_data_fc03.ok = True
            read_stop_time = time.perf_counter()
            read_end_time = time.time()             # когда закончили (epoch)
            duration_ms = (read_stop_time - read_start_time) * 1000

            if readed_data and (readed_data.isError() is True):
                raw_readed_data_fc03.ok = False
                exception_code = readed_data.exception_code
                err_message = "1. Ошибка от PLC. Регистры - fc03"
                logger.warning(err_message)
                logger.warning("Код ошибки: %s", exception_code)

                if raw_error_info is None:
                    raw_error_info = ErrorInfo(
                        exception_code=exception_code, message=err_message, kind=KindState.DEVICE)

                if raw_readed_data_fc04.error is None:
                    raw_readed_data_fc04.error = raw_error_info

        except RuntimeError as err:
            raw_readed_data_fc03.ok = False
            # is_not_correct_reading_fc03 = True
            err_message = "2. Ошибка от PLC. Регистры - fc03"
            logger.warning(err_message)
            logger.warning("RuntimeError: %s", err)
            if raw_error_info is None:
                raw_error_info = ErrorInfo(
                    exception_code=None, message=err_message, kind=KindState.TRANSPORT)
        finally:
            if readed_data:
                raw_readed_data_fc03.ok = True
                raw_readed_data_fc03.fc = 3
                raw_readed_data_fc03.unit_id = device_poll_settings.device_id
                raw_readed_data_fc03.addr = device_poll_settings.offset
                raw_readed_data_fc03.count = device_poll_settings.read_count
                # TODO Проверить, скопировалось ли или нет....
                raw_readed_data_fc03.registers = readed_data.registers[:]
                raw_readed_data_fc03.duration_ms = duration_ms
                raw_readed_data_fc03.ts_block_end = read_end_time
                if raw_readed_data_fc03 and raw_error_info:
                    raw_readed_data_fc03.error = ErrorInfo(
                        message=raw_error_info.message, kind=raw_error_info.kind, exception_code=raw_error_info.exception_code, exc_type=raw_error_info.exc_type)

    read_stop_time = time.perf_counter()
    full_read_end_time = time.time()
    readed_poll_result.blocks.append(raw_readed_data_fc04)
    readed_poll_result.blocks.append(raw_readed_data_fc03)
    readed_poll_result.ts_poll_start = full_read_start_time
    readed_poll_result.ts_poll_end = full_read_end_time
    if raw_readed_data_fc03.ok or raw_readed_data_fc04.ok:
        readed_poll_result.connection_state = ConnectionState.UP

    return readed_poll_result


async def poll_forever(
    device_config: ModbusConfig, device_poll_settings: ModbusDeviceReadSettings
) -> AsyncIterator[PollResult]:

    poll_result: PollResult = PollResult()
    time_start: float = 0
    time_end: float = 0

    device_being_polled: AsyncModbusTcpClient | None = None
    try:
        logger.info("Запуск цикла опроса.")
        logger.info(
            "Поднимаю коннект по ip %s порт %s",
            device_config.host,
            device_config.port,
        )
        while (True):
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
                    "Попытка повторного подключения через 30 секунд")
                await asyncio.sleep(30)
                logger.warning("Повторное подключение...")
                continue

        logger.info(
            "Коннект по ip %s порт %s поднят успешно!",
            device_config.host,
            device_config.port,
        )
        while True:
            poll_result = await poll_device(device_being_polled, device_poll_settings)
            yield poll_result

            #  TODO реализовать задержку, что бы она
            # не плавала. Высчитывать, сколько будет между ними

            await asyncio.sleep(device_config.poll_interval_s)
    finally:
        logger.info(
            "Закрываю Коннект по ip %s порт %s!",
            device_config.host,
            device_config.port,
        )
        if device_being_polled:
            device_being_polled.close()
        logger.info("Коннект закрыт")


async def main():
    async for result in poll_forever(get_modbus_config(), get_device_read_settings()):
        logger.info("%s", result)
    return


if __name__ == "__main__":
    # device_config: ModbusConfig = await get_modbus_config()
    # ✅ Настройка логов только при запуске как скрипт
    try:
        init_logging()

        logger.info("Запуск Pump Station Telemetry Gateway")
        asyncio.run(
            main(), debug=False
        )

    except KeyboardInterrupt:
        logger.info("Пользователь нажал Ctrl+C")
    finally:
        logger.info("Остановка Pump Station Telemetry Gateway")

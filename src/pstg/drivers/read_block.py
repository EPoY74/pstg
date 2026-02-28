"""
Функция получает на вход функцию для чтения конкретного регистра
обрабатывает и выдает результат. Добавлена для того, что бы убрать
дублирование кода, так как обвязка вокруг функций одинаковая.

"""

import time
from collections.abc import Awaitable, Callable

from pymodbus.client import AsyncModbusTcpClient
from pymodbus.pdu import ModbusPDU

from pstg.domain.error_info import ErrorInfo
from pstg.domain.kind_state import KindState
from pstg.domain.modbus_device_read_settings import ModbusDeviceReadSettings
from pstg.domain.raw_block_result import RawBlockResult

Reader = Callable[..., Awaitable[ModbusPDU | None]]


async def read_block(
    reader: Reader,
    fc: int,
    device_being_polled: AsyncModbusTcpClient,
    device_poll_settings: ModbusDeviceReadSettings,
) -> tuple[RawBlockResult, bool]:
    """Читает с помощью переданной функции reader состояние
    modbus устройства

    Args:
        reader (Reader): фунекция, читающия данные.
        Пример: Если функция назавается my_read_func(),
        то передаем её как my_read_funr, без скобок
        fc (int): номер регистра, который читаем. Не провереяеся.
        Служит только для формирования номера в RawBlockResult
        Пример: 3, 4
        device_being_polled (AsyncModbusTcpClient):Поднятый коннект до
        modbus устройства
        device_poll_settings (ModbusDeviceReadSettings): Настройки для чтения
        с устройства: смещение откуда читаем; сколько читаем адресов;
         номер устройства, с которого читаем

    Returns:
        tuple[RawBlockResult, bool]: Возвращает кортеж, содержащий прочтенные
        данный и флаг, определяющий состояние подключения: True - устройство
        ответило(ошибка - тожесчитаетс за ответ), False - устройство не
        ответило (никак, вообще не ответило, ошибка транспорта до
        устройства, например)
    """

    raw_was_read_data_fc: RawBlockResult = RawBlockResult()
    raw_error_info: ErrorInfo | None = None
    got_response: bool = False

    read_stop_time: float = 0.0
    read_end_time: float = 0.0
    duration_ms: float = 0.0

    try:
        read_start_time: float = time.perf_counter()

        readed_data = await reader(
            device_being_polled,
            offset=device_poll_settings.offset,
            read_count=device_poll_settings.read_count,
            plc_id=device_poll_settings.device_id,
        )

        # ok?
        # READ_WAS_SUCCESSFUL = ...

        # if READ_WAS_SUCCESSFUL:
        #     ...
        #     return корректный возврат
        # else:
        #     ...
        #     return информация об ошибке

        if readed_data is None:
            raw_was_read_data_fc.ok = False

        if readed_data and readed_data.isError() is not True:
            got_response = True
            raw_was_read_data_fc.ok = True

        read_stop_time = time.perf_counter()
        read_end_time = time.time()  # когда закончили (epoch)
        duration_ms = (read_stop_time - read_start_time) * 1000

        if readed_data and (readed_data.isError() is True):
            got_response = True
            raw_was_read_data_fc.ok = False
            exception_code = readed_data.exception_code
            err_message = f"1. Ошибка от PLC. Регистры - fc{fc}"

            # if raw_error_info is None:
            raw_error_info = ErrorInfo(
                exception_code=exception_code,
                message=err_message,
                kind=KindState.DEVICE,
            )

            if raw_was_read_data_fc.current_error_info is None:
                raw_was_read_data_fc.current_error_info = raw_error_info

        if readed_data:
            raw_was_read_data_fc.fc = fc
            raw_was_read_data_fc.unit_id = device_poll_settings.device_id
            raw_was_read_data_fc.addr = device_poll_settings.offset
            raw_was_read_data_fc.count = device_poll_settings.read_count
            if hasattr(readed_data, "registers"):
                raw_was_read_data_fc.registers = readed_data.registers[:]
            raw_was_read_data_fc.duration_ms = duration_ms
            raw_was_read_data_fc.ts_block_end = read_end_time
            # if raw_error_info:
            #     raw_was_read_data_fc.current_error_info = ErrorInfo(
            #         message=raw_error_info.message,
            #         kind=raw_error_info.kind,
            #         exception_code=raw_error_info.exception_code,
            #         exc_type=raw_error_info.exc_type,
            #     )

    except RuntimeError as err:
        got_response = False
        raw_was_read_data_fc.ok = False
        err_message = f"2. Ошибка от PLC. Регистры - fc{fc}: {err}"
        if raw_error_info is None:
            raw_error_info = ErrorInfo(
                exception_code=None,
                message=err_message,
                kind=KindState.TRANSPORT,
            )

    finally:
        if raw_error_info:
            raw_was_read_data_fc.current_error_info = ErrorInfo(
                message=raw_error_info.message,
                kind=raw_error_info.kind,
                exception_code=raw_error_info.exception_code,
                exc_type=raw_error_info.exc_type,
            )

    return (
        raw_was_read_data_fc,
        got_response,
    )

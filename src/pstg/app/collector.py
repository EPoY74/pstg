import asyncio
import logging

from pymodbus.client import AsyncModbusTcpClient
from pymodbus.pdu import ModbusPDU

from pstg.domain.modbus_device_read_settings import ModbusDeviceReadSettings
from pstg.domain.modbus_config import ModbusConfig
from pstg.drivers.open_connection_modbus_tcp import open_connection_modbus_tcp
from pstg.drivers.read_fc03_holding_register import read_fc03_holding_register
from pstg.drivers.read_fc04_input_regoster import read_fc04_input_register

logger = logging.getLogger(__name__)


# Выше данной функции другие фунции не писать! Только импорты и т.д.!
def init_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def get_modbus_config() -> ModbusConfig:
    # IP адрес устройства, с которого получаем данные
    DEVICE_IP: str = "10.0.6.10"

    #  Порт, через который работаем с устройством
    DEVICE_PORT: int = 506

    #  Период опроса устройства
    DEVICE_POLL_INTERVAL_S: float = 2
    return ModbusConfig(
        host=DEVICE_IP, port=DEVICE_PORT, poll_interval_s=DEVICE_POLL_INTERVAL_S
    )


def get_device_read_settings() -> ModbusDeviceReadSettings:
    #  ID устройства, с которого считываем данные=
    DEVICE_ID: int = 1

    # Начальное смещение, с которого считаывем
    DATA_OFFSET: int = 0

    # Сколько регистров читать, начиная с DATA_OFFSET
    # Пример: 16-bit word
    # Правило Modbus: значения могут занимать несколько регистров
    #  (напр. float32 обычно = 2 регистра)
    READ_DATA_COUNT: int = 12
    return ModbusDeviceReadSettings(
        device_id=DEVICE_ID, offset=DATA_OFFSET, read_count=READ_DATA_COUNT
    )


async def poll_device(
    device_being_polled: AsyncModbusTcpClient,
    device_poll_settings: ModbusDeviceReadSettings,
    is_not_correct_reading: bool | None = None
) -> None:
    readed_data: ModbusPDU | None = None

    try:
        logger.info("Читаю регистры fc04")
        readed_data = await read_fc04_input_register(
            device_being_polled,
            offset=device_poll_settings.offset,
            read_count=device_poll_settings.read_count,
            plc_id=device_poll_settings.device_id,
        )
        is_not_correct_reading = False
        if ((readed_data)
            and (
            (readed_data.isError() is True)
            or (readed_data.exception_code != 0)
        )):
            is_not_correct_reading = True
            logger.warning
            ("Ошибка от PLC. Регистры - fc04")
            logger.warning("Код ошибки: %s", readed_data.exception_code)
            readed_data = None

    except RuntimeError as err:
        # logger.warning
        # if ((readed_data)
        #     and (
        #     (readed_data.isError() is True)
        #     or (readed_data.exception_code != 0)
        # )):
        logger.warning("Ошибка от PLC. Регистры - fc04")
        logger.warning("RuntimeError: %s", err)
        readed_data = None

    if is_not_correct_reading:
        try:
            logger.info("Читаю регистры fc03")
            readed_data = await read_fc03_holding_register(
                device_being_polled,
                offset=device_poll_settings.offset,
                read_count=device_poll_settings.read_count,
                plc_id=device_poll_settings.device_id,
            )
            if ((readed_data)
                and (
                (readed_data.isError() is True)
                or (readed_data.exception_code != 0)
            )):
                logger.info("Ошибка от PLC. Регистры - fc03")
                logger.info("Код ошибки: %s", readed_data.exception_code)
        except RuntimeError as err:
            logger.error("Ошибка от PLC. Регистры FC03: %s", err)
        if readed_data:
            logger.info("Данные: %s", readed_data.registers)
            logger.info("Exception code: %s",
                        readed_data.exception_code)


async def main(
    device_config: ModbusConfig, device_poll_settings: ModbusDeviceReadSettings
) -> None:

    device_being_polled: AsyncModbusTcpClient | None = None
    try:
        logger.info("Запуск цикла опроса.")
        logger.info(
            "Поднимаю коннект по ip %s порт %s",
            device_config.host,
            device_config.port,
        )
        device_being_polled = await open_connection_modbus_tcp(
            device_config.host, device_config.port
        )
        logger.info(
            "Коннект по ip %s порт %s поднят успешно!",
            device_config.host,
            device_config.port,
        )
        while True:
            await poll_device(device_being_polled, device_poll_settings)

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


if __name__ == "__main__":
    # device_config: ModbusConfig = await get_modbus_config()
    # ✅ Настройка логов только при запуске как скрипт
    try:
        init_logging()

        logger.info("Запуск Pump Station Telemetry Gateway")
        asyncio.run(
            main(get_modbus_config(), get_device_read_settings()), debug=False
        )

    except KeyboardInterrupt:
        logger.info("Пользователь нажал Ctrl+C")
    finally:
        logger.info("Остановка Pump Station Telemetry Gateway")

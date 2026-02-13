import asyncio
import logging

from pymodbus.pdu import ModbusPDU

from pstg.domain.modbus_device_read_settings import ModbusDeviceReadSennings
from pstg.domain.modbus_config import ModbusConfig
from pstg.drivers.open_connection_modbus_tcp import open_connection_modbus_tcp
from pstg.drivers.read_fc03_holding_register import read_fc03_holding_register
from pstg.drivers.read_fc04_input_regoster import read_fc04_input_register


# Выше данной функции другие фунции не писать! Только импорты и т.д.!
def get_modbus_config() -> ModbusConfig:
    # IP адрес устройства, с которого получаем данные
    DEVICE_IP: str = "10.0.6.10"

    #  Порт, через который работаем с устройством
    DEVICE_PORT: int = 506

    #  Период опроса устройства
    DEVICE_POLL_INTERVAL_S: float = 0.5
    return ModbusConfig(
        host=DEVICE_IP, port=DEVICE_PORT, poll_interval_s=DEVICE_POLL_INTERVAL_S
    )


def get_device_read_settings() -> ModbusDeviceReadSennings:
    #  ID устройства, с которого считываем данные=
    DEVICE_ID: int = 1

    # Начальное смещение, с которого считаывем
    DATA_OFFSET: int = 0

    # Сколько регистров читать, начиная с DATA_OFFSET
    # Пример: 16-bit word
    # Правило Modbus: значения могут занимать несколько регистров
    #  (напр. float32 обычно = 2 регистра)
    READ_DATA_COUNT: int = 1
    return ModbusDeviceReadSennings(
        device_id=DEVICE_ID, offset=DATA_OFFSET, read_count=READ_DATA_COUNT
    )


async def poll_device(device_config: ModbusConfig) -> None:
    readed_data: ModbusPDU | None = None

    device_being_polled = await open_connection_modbus_tcp(
        device_config.host, device_config.port
    )
    try:
        readed_data = await read_fc04_input_register(
            device_being_polled,
            offset=ModbusDeviceReadSennings.offset,
            read_count=ModbusDeviceReadSennings.read_count,
            plc_id=ModbusDeviceReadSennings.device_id,
        )
        if (readed_data) and (readed_data.isError is True):
            readed_data = await read_fc03_holding_register(
                device_being_polled,
                offset=ModbusDeviceReadSennings.offset,
                read_count=ModbusDeviceReadSennings.read_count,
                plc_id=ModbusDeviceReadSennings.device_id,
            )

    finally:
        device_being_polled.close()


async def main(device_config: ModbusConfig) -> None:
    while True:
        await poll_device(device_config)


if __name__ == "__main__":
    # device_config: ModbusConfig = await get_modbus_config()

    asyncio.run(main(get_modbus_config()), debug=True)

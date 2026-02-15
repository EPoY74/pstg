from pstg.domain.modbus_config import ModbusConfig


def get_modbus_config() -> ModbusConfig:
    """
    Функция содержит настройки сетевого подключения к Modbus устройству

    :return: Настройки подключения
    :rtype: ModbusConfig
    """
    # IP адрес устройства, с которого получаем данные
    DEVICE_IP: str = "10.0.6.10"

    #  Порт, через который работаем с устройством
    DEVICE_PORT: int = 506

    #  Период опроса устройства
    DEVICE_POLL_INTERVAL_S: float = 2
    return ModbusConfig(
        host=DEVICE_IP, port=DEVICE_PORT, poll_interval_s=DEVICE_POLL_INTERVAL_S
    )

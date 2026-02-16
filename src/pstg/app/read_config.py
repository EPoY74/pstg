from pstg.domain.modbus_device_read_settings import ModbusDeviceReadSettings


def get_device_read_settings() -> ModbusDeviceReadSettings:
    """
    Функция содержит настройки устройства, с которого читаем информацию

    :return: Настройки устройства
    :rtype: ModbusDeviceReadSettings
    """
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

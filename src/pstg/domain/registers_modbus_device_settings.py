from dataclasses import dataclass


@dataclass
class RegistersModbusDeviceSettings:
    """
    Конфигурация устройства, с которого считываем данные.

    device_id (int): ID устройства, с которого считываем данные
    offset (int): Смещение (адрес), откуда читаем
    read_count (int): Сколько читать от смещения (адреса)
    enable_signals_reading (int): Включение чтения аналоговых данных с преобразованием

    """  # noqa: E501

    device_id: int
    offset: int
    read_count: int
    fc: int
    enable_signals_reading: bool

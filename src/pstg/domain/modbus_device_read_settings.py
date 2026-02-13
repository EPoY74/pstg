from dataclasses import dataclass


@dataclass
class ModbusDeviceReadSennings:
    """
    Конфигурация устройства, с которого считываем данные.

    device_id (int): ID устройства, с которого считываем данные
    offset (int): Смещение (адрес), откуда читаем
    read_count (int): Сколько читать от смещения (адреса)

    """

    device_id: int
    offset: int
    read_count: int

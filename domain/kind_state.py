from enum import Enum


class KindState(str, Enum):
    """Определяет источник получения данных.
    Values:
        TRANSPORT: Фейковые данные
        DEVICE: Данные от устройства
    """

    TRANSPORT = "TRANSPORT"
    DEVICE = "DEVICE"

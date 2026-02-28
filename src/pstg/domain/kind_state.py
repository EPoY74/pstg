from enum import Enum


class KindState(str, Enum):
    """Определяет источник ошибки.
    Values:
        TRANSPORT: Ошибка транспорта
        DEVICE: Ошибка устройства
    """

    TRANSPORT = "TRANSPORT"
    DEVICE = "DEVICE"

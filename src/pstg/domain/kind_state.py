from enum import StrEnum


class KindState(StrEnum):
    """Определяет источник ошибки.
    Values:
        TRANSPORT: Ошибка транспорта
        DEVICE: Ошибка устройства
    """

    TRANSPORT = "TRANSPORT"
    DEVICE = "DEVICE"

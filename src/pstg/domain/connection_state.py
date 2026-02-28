from enum import StrEnum


class ConnectionState(StrEnum):
    """Определяет состояние подуключения.

    Values:
        UP: Соединение установлено
        DOWN: Соединение отсутствует
    """

    UP = "UP"
    DOWN = "DOWN"

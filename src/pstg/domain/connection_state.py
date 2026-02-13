from enum import Enum


class ConnectionState(str, Enum):
    """Определяет состояние подуключения.

    Values:
        UP: Соединение установлено
        DOWN: Соединение отсутствует
    """

    UP = "UP"
    DOWN = "DOWN"

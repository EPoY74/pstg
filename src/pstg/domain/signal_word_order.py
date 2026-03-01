from enum import StrEnum


class SignalWordOrder(StrEnum):
    """
    Порядок слов при чтении real из plc
    """

    LITTLE = "LITTLE"
    BIG = "BIG"

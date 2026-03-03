from dataclasses import dataclass

from pstg.domain.signal_spec import SignalSpec


@dataclass
class SignalsModbusDeviceSettings:
    """
    Конфигурация устройства, с которого считываем аналоговые данные.
    offset: int  # Смещение от начала
    read_count: int  # Сколько читать
    signals_map: list[SignalSpec]  # Параметры сигналов
    """

    start_address_of_block: int  # Смещение от начала
    read_count: int  # Сколько читать
    fc: int  # С какого типа регистра читаем
    signals_map: list[SignalSpec]  # Параметры сигналов

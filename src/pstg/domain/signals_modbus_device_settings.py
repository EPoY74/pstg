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

    offset: int  # Смещение от начала
    read_count: int  # Сколько читать
    signals_map: list[SignalSpec]  # Параметры сигналов

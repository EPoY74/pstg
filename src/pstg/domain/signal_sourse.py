from dataclasses import dataclass

from pstg.domain.signal_word_order import SignalWordOrder


@dataclass
class SignalSource:
    """
    Источник сигнала.
    """

    # fc (Function Code / код функции Modbus):
    # Каким Modbus-методом читали/писали. Примеры:
    # 3 = Read Holding Registers (чтение holding-регистров),
    # 4 = Read Input Registers (чтение input-регистров).
    fc: int

    # addr (Address / адрес старта, смещение):
    # Стартовый адрес (offset), с которого начали чтение в этом запросе.
    address: int

    # count (Count / количество):
    # Сколько регистров (16-bit регистров Modbus) запросили
    # подряд начиная с addr.
    # Важно: одно "значение" может занимать несколько
    # регистров (например float32 = 2 регистра).
    count: int

    # Номер устройства, откуда читаем
    device_id: int

    # Порядок слов в данных.
    # Первый байт LITTLE или BIG
    word_odder: SignalWordOrder

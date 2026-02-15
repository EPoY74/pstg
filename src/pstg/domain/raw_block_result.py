from dataclasses import dataclass, field

from pstg.domain.error_info import ErrorInfo


@dataclass
class RawBlockResult:
    # fc (Function Code / код функции Modbus):
    # Каким Modbus-методом читали/писали. Примеры:
    # 3 = Read Holding Registers (чтение holding-регистров),
    # 4 = Read Input Registers (чтение input-регистров).
    fc: int = 0

    # addr (Address / адрес старта, смещение):
    # Стартовый адрес (offset), с которого начали чтение в этом запросе.
    # Если offset=0 и count=12, то registers[0] соответствует addr=0,
    # registers[1] -> addr=1, ... registers[11] -> addr=11.
    addr: int = 0

    # count (Count / количество):
    # Сколько регистров (16-bit регистров Modbus) запросили подряд начиная с addr.
    # Важно: одно "значение" может занимать несколько регистров (например float32 = 2 регистра).
    count: int = 0

    # unit_id (Unit Identifier / идентификатор устройства):
    # Адрес ведомого устройства (slave id) в терминах Modbus.
    # В Modbus TCP часто равен 1, но может использоваться при работе через шлюз
    # (например Modbus TCP -> Modbus RTU), чтобы выбрать RTU-устройство за шлюзом.
    unit_id: int = 0

    # ok (Успех блока):
    # True  -> блок прочитан/записан успешно, registers заполнен.
    # False -> блок не получен (ошибка устройства или транспорта), registers НЕ использовать.
    # None сейчас допускается, но best practice: сделать просто bool и всегда заполнять.
    ok: bool | None = None

    # registers (Регистры / сырые значения):
    # Сырые 16-bit слова (word) из Modbus-ответа, порядок как пришёл.
    # Имеет смысл только если ok=True.
    #
    # Best practice: сделать Optional[list[int]] и ставить None при ok=False,
    # чтобы "нет данных" не путалось с "данные есть, но пусто".
    registers: list[int] = field(default_factory=list)

    # error (Ошибка блока):
    # Структурированная ошибка для этого конкретного чтения:
    # - kind="transport" (ошибка транспорта): таймаут, разрыв TCP, и т.п.
    # - kind="device" (ошибка устройства): Modbus exception (Illegal Function / Illegal Data Address и т.д.).
    # Если ok=True -> error обычно None.
    error: ErrorInfo | None = None

    # duration_ms (Длительность, миллисекунды):
    # Сколько заняло это чтение "от отправки запроса до получения ответа" (latency).
    # Нужно для диагностики: лаги сети/ПЛК, перегруз, деградация связи.
    duration_ms: float | None = None

    # ts_block_end (Timestamp / метка времени конца блока, epoch seconds):
    # Время (по часам шлюза), когда завершили обработку ответа по этому блоку.
    # Используется для привязки "когда реально получили данные".
    # Обычно epoch seconds = time.time().
    ts_block_end: float | None = None  # epoch seconds или time.time()

# Pump Station Telemetry Gateway

`PSTG` это асинхронный `Modbus TCP` polling-сервис для сбора телеметрии, мониторинга и диагностики промышленных устройств, PLC, RTU, насосных станций, шкафов автоматики и другого оборудования industrial IoT / SCADA.

Текущая реализация:

- читает `FC04` (`Input Registers`)
- при `device error` делает fallback на `FC03` (`Holding Registers`)
- на каждый цикл возвращает `PollResult`
- умеет работать с локальным Modbus simulator без реального оборудования

## Что уже есть

- async polling через `pymodbus.client.AsyncModbusTcpClient`
- разделение на `app`, `drivers`, `domain`
- reconnect на уровне приложения
- локальный Modbus TCP simulator для разработки
- unit, scenario и integration tests

## Структура проекта

```text
src/
  pstg/
    app/
      collector.py
      modbus_corfig.py
      read_config.py
    domain/
      connection_state.py
      error_info.py
      kind_state.py
      modbus_config.py
      modbus_device_read_settings.py
      poll_result.py
      raw_block_result.py
    drivers/
      open_connection_modbus_tcp.py
      read_block.py
      read_fc03_holding_register.py
      read_fc04_input_regoster.py
    simulator/
      config.py
      server.py
tests/
  ...
```

## Требования

- Python `3.12+`
- `uv`

## Установка

Из корня репозитория:

```powershell
uv sync
uv pip install -e .
```

Проверка:

```powershell
uv --version
```

## Запуск collector

```powershell
uv run python -m pstg.app.collector
```

Остановка:

- `Ctrl + C`

## Текущая конфигурация collector

### Modbus TCP

Файл: [modbus_corfig.py](C:\repos-win\source\pstg\src\pstg\app\modbus_corfig.py)

- `DEVICE_IP = "127.0.0.1"`
- `DEVICE_PORT = 1502`
- `DEVICE_POLL_INTERVAL_S = 2`

### Параметры чтения

Файл: [read_config.py](C:\repos-win\source\pstg\src\pstg\app\read_config.py)

- `DEVICE_ID = 1`
- `DATA_OFFSET = 0`
- `READ_DATA_COUNT = 12`

## Контракт polling

### `PollResult.connection_state`

- `UP`, если хотя бы один блок дал любой Modbus-ответ
- `DOWN`, если ни один блок не ответил и были только transport-проблемы

### `RawBlockResult.ok`

- `True`, если чтение успешно и ответ без `isError()`
- `False`, если был `device error` или `transport error`

### Ошибки

- `KindState.DEVICE` = устройство ответило Modbus exception
- `KindState.TRANSPORT` = до устройства не удалось нормально достучаться

## Что возвращает poll

Каждый цикл опроса возвращает `PollResult`:

- `connection_state`
- `ts_poll_start`
- `ts_poll_end`
- `blocks`

Каждый элемент `blocks` это `RawBlockResult`:

- `fc`
- `unit_id`
- `addr`
- `count`
- `ok`
- `registers`
- `duration_ms`
- `ts_block_end`
- `current_error_info`

## Поля `PollResult`

### `run_id: str`

Идентификатор запуска процесса или сессии polling.

Нужен, если позже захочешь:

- группировать результаты одного запуска
- разбирать логи по сессиям
- связывать telemetry batch с конкретным процессом

Сейчас поле зарезервировано под дальнейшее развитие.

### `poll_seq: int`

Порядковый номер цикла опроса.

Нужен для:

- диагностики пропущенных циклов
- анализа drift и стабильности polling loop
- последующей привязки трендов и time-series данных к номеру цикла

Сейчас поле тоже зарезервировано.

### `ts_poll_start: float`

Unix timestamp в секундах, когда начался цикл опроса устройства.

Полезно для:

- телеметрии
- мониторинга
- построения временных рядов
- корреляции с логами PLC, gateway, SCADA, historian

### `ts_poll_end: float`

Unix timestamp в секундах, когда цикл опроса завершился.

Позволяет:

- измерять длительность полного цикла
- понимать, когда данные реально были получены
- анализировать задержки polling

### `connection_state: ConnectionState | None`

Итоговое состояние канала связи по результату цикла опроса.

Смысл:

- `UP` = хотя бы один блок дал Modbus-ответ
- `DOWN` = ни один блок не ответил, были только transport-ошибки

Это поле отвечает именно за доступность канала, а не за валидность прикладных данных.

### `blocks: list[RawBlockResult]`

Список блоков чтения внутри одного цикла опроса.

Сейчас обычно содержит:

- блок `FC04`
- блок `FC03`

Это удобно для диагностики Modbus fallback логики и анализа поведения устройства.

## Поля `RawBlockResult`

### `fc: int`

Номер Modbus function code, которым читался блок.

Типичные значения:

- `4` = `Read Input Registers`
- `3` = `Read Holding Registers`

Нужно для:

- диагностики
- логирования
- анализа fallback `FC04 -> FC03`

### `addr: int`

Стартовый адрес чтения, то есть Modbus offset.

Если читается диапазон с `addr=0` и `count=12`, значит чтение начинается с первого адреса блока.

Полезно для:

- отладки карты регистров
- верификации address map
- проверки правильности Modbus addressing

### `count: int`

Количество регистров, которое было запрошено подряд.

Это важно, потому что одно логическое значение может занимать:

- 1 регистр
- 2 регистра
- 4 регистра

Например при дальнейшем декодировании `float32`, `int32`, битовых масок и статусов.

### `unit_id: int`

Modbus Unit ID / Slave ID устройства.

В Modbus TCP часто равен `1`, но особенно важен, если:

- работа идет через Modbus gateway
- за одним IP скрыто несколько RTU-устройств
- нужно эмулировать реальный PLC / RTU / slave

### `ok: bool | None`

Признак успешного чтения блока без `device error`.

Смысл:

- `True` = успешный ответ без `isError()`
- `False` = `device error` или `transport error`
- `None` = поле еще не было осмысленно заполнено или блок не использовался

В текущей архитектуре `ok` не равен доступности канала. Для канала смотри `connection_state`.

### `registers: list[int]`

Сырые Modbus регистры, пришедшие в ответе.

Это raw data, из которых потом можно собирать:

- telemetry values
- counters
- alarms
- status words
- bit flags
- analog signals

В проекте сейчас регистры сохраняются даже при `device error`, если библиотека вернула payload. Это полезно для low-level диагностики и анализа нестандартного поведения устройства.

### `current_error_info: ErrorInfo | None`

Структурированное описание ошибки конкретного блока чтения.

Если `None`, значит для этого блока явная ошибка не зафиксирована.

Если не `None`, можно понять:

- это transport проблема или device problem
- есть ли Modbus exception code
- какой текст ошибки попал в диагностический результат

### `duration_ms: float | None`

Длительность чтения конкретного блока в миллисекундах.

Нужно для:

- диагностики производительности
- поиска лагов сети
- оценки времени ответа PLC
- наблюдения деградации связи

### `ts_block_end: float | None`

Unix timestamp в секундах, когда завершилось чтение этого блока.

Полезно, если:

- блоки читаются последовательно
- нужно видеть момент завершения каждого запроса отдельно
- данные потом будут сохраняться в time-series storage

## Поля `ErrorInfo`

### `message: str`

Человекочитаемое описание проблемы.

Используется для:

- логирования
- быстрой отладки
- вывода в диагностику

### `kind: KindState | None`

Тип ошибки.

Значения:

- `DEVICE` = Modbus exception от устройства
- `TRANSPORT` = ошибка сети, TCP, timeout, reconnect, библиотечного клиента

### `exception_code: int | None`

Modbus exception code, если устройство реально ответило ошибкой.

Примеры:

- `ILLEGAL FUNCTION`
- `ILLEGAL DATA ADDRESS`
- `ILLEGAL DATA VALUE`
- `SERVER DEVICE FAILURE`

Это важно для диагностики register map, PLC logic, gateway mapping и интеграции Modbus TCP / RTU.

### `exc_type: str | None`

Дополнительный тип исключения для transport-проблем.

Сейчас используется как расширение на будущее.

## Локальный Modbus simulator

Симулятор нужен для разработки без PLC, шлюза и другого реального оборудования.

Он умеет:

- поднимать Modbus TCP сервер
- отдавать `FC04` и `FC03`
- настраивать адреса и значения через JSON
- автоматически менять значения по таймеру

### Быстрый старт симулятора

Запуск со встроенным конфигом:

```powershell
uv run python -m pstg.simulator.server
```

По умолчанию:

- host: `127.0.0.1`
- port: `1502`
- device_id: `1`
- FC04 адрес `0`: `[101, 102, 103, 104]`, автообновление раз в `1` секунду
- FC03 адрес `0`: `[201, 202, 203, 204]`, автообновление раз в `2` секунды

### Запуск симулятора с конфигом

Пример файла: [simulator.example.json](C:\repos-win\source\pstg\simulator.example.json)

```powershell
uv run python -m pstg.simulator.server --config simulator.example.json
```

### Переопределение параметров из CLI

```powershell
uv run python -m pstg.simulator.server --config simulator.example.json --host 0.0.0.0 --port 1503 --device-id 2
```

### Формат конфига симулятора

```json
{
  "host": "127.0.0.1",
  "port": 1502,
  "device_id": 1,
  "input_registers": [
    { "address": 0, "values": [101, 102, 103, 104], "interval_s": 1.0, "step": 1 },
    { "address": 10, "values": [501, 502] }
  ],
  "holding_registers": [
    { "address": 0, "values": [201, 202, 203, 204] },
    { "address": 20, "values": [901, 902, 903], "interval_s": 2.0, "step": 10 }
  ]
}
```

## Поля конфига симулятора

### `host`

IP-адрес, на котором поднимается локальный Modbus TCP server.

Для локальной разработки обычно:

- `127.0.0.1`

Для доступа с другой машины в сети:

- `0.0.0.0`

### `port`

TCP порт Modbus simulator.

Для реального Modbus TCP часто используют `502`, но для локальной разработки удобнее безопасный пользовательский порт, например `1502`.

### `device_id`

Unit ID / Slave ID, который должен совпадать с тем, что использует клиент `pstg`.

### `input_registers`

Список блоков для `FC04`.

Используется для эмуляции:

- датчиков
- аналоговых сигналов
- измерений
- технологических параметров

### `holding_registers`

Список блоков для `FC03`.

Подходит для эмуляции:

- внутренних регистров PLC
- параметров конфигурации
- fallback-данных
- совместимости с нестандартными Modbus-устройствами

### Что означает конфиг симулятора

- `address` = стартовый адрес блока
- `values` = значения, которые сервер будет отдавать
- `interval_s` = необязательный период автообновления
- `step` = необязательный шаг изменения каждого значения

### `address`

Стартовый адрес регистрационного блока в Modbus карте.

Если блок имеет:

- `address = 10`
- `values = [501, 502]`

то будут заполнены регистры `10` и `11`.

### `values`

Начальные значения регистров для блока.

Это сырые `16-bit` значения, которые потом клиент может:

- читать как есть
- декодировать в `int16`, `uint16`, `int32`, `float32`
- интерпретировать как status words и bit fields

### `interval_s`

Необязательный интервал автообновления значений в секундах.

Если поле отсутствует, значения блока остаются статичными.

### `step`

Необязательный шаг, на который изменяется каждое значение блока при каждом срабатывании таймера.

Пример:

```json
{
  "address": 0,
  "values": [100, 200],
  "interval_s": 1.0,
  "step": 5
}
```

Поведение:

- старт: `[100, 200]`
- через 1 секунду: `[105, 205]`
- через 2 секунды: `[110, 210]`

### Как подключить collector к симулятору

Убедись, что в collector настроено:

- host: `127.0.0.1`
- port: `1502`
- `device_id = 1`

Затем:

1. Запусти симулятор
2. Запусти collector
3. Смотри логи сервера и клиента

### Типовые сценарии разработки

#### 1. Успешное чтение FC04

Заполни `input_registers` и проверь, что `collector` читает значения через `FC04`.

#### 2. Fallback на FC03

Сделай диапазон `FC04` невалидным, а нужные данные положи в `holding_registers`.

#### 3. Проверка карты адресов

Добавь несколько блоков с разными адресами и проверь, что код читает нужный диапазон.

#### 4. Живые изменяющиеся данные

Добавь `interval_s` и `step`, чтобы видеть, как значения меняются без перезапуска сервера.

## Тесты

Запуск всех тестов:

```powershell
.\\.venv\\Scripts\\python.exe -m pytest tests -q
```

Или:

```powershell
uv run pytest tests -q
```

Что уже покрыто:

- `read_block`
- fallback `FC04 -> FC03`
- reconnect-сценарий
- чтение через реальный тестовый Modbus server
- dev simulator
- автообновление регистров по таймеру

## Ограничения на текущем этапе

- конфиг collector пока hardcoded
- reload конфига симулятора на лету не реализован
- coils и discrete inputs пока не настраиваются через JSON

## Ближайшие улучшения

- вынести конфиг collector в env или JSON/YAML
- добавить decode-слой
- расширить simulator
- улучшить reconnect и диагностику

# Pump Station Telemetry Gateway

`PSTG` это `MVP`-проект асинхронного `Modbus TCP` polling-сервиса для сбора телеметрии, диагностики связи и локального мониторинга станций.

Проект разрабатывался специалистом **ООО "ЧЗМЭК"** для личного использования: как рабочий инструмент, который упрощает разработку, отладку и сопровождение мониторинга станций без постоянной зависимости от "железного" оборудования, PLC, RTU, Modbus gateway и стендов.

Проект ориентирован на практические задачи:

- `SCADA`
- `industrial automation`
- `industrial IoT`
- `telemetry`
- `monitoring`
- `diagnostics`
- `pump station monitoring`
- `Modbus TCP polling`
- `PLC integration`
- `RTU / gateway integration`
- `time-series data collection`
- `register map validation`
- `industrial telemetry`
- `Modbus simulator`
- `station monitoring`

## Быстрый старт

Если нужно быстро понять, что проект живой и работает, делай так:

1. Установи зависимости:

```powershell
uv sync
uv pip install -e .
```

2. Запусти локальный Modbus simulator:

```powershell
uv run python -m pstg.simulator.server
```

3. В другом окне терминала запусти collector:

```powershell
uv run python -m pstg.app.collector
```

4. Проверь логи:

- в логах simulator должны идти строки `Updated fc...`
- в логах collector должны появляться результаты polling

Это самый быстрый способ проверить:

- что сервер поднялся
- что клиент подключается
- что регистры читаются
- что значения меняются во времени

## Небольшая история проекта

Этот проект писался не как "витринный pet project", а как рабочий инженерный инструмент.

Сначала задача была очень практичной:

- нужно читать данные по `Modbus TCP`
- нужно тестировать это без постоянного доступа к оборудованию
- нужно быстро различать ошибку устройства и проблему связи
- нужно ускорить разработку мониторинга станций

Потом вокруг этого постепенно выросли:

- понятные domain-модели
- fallback-логика
- reconnect
- simulator
- тесты

Поэтому `PSTG` сейчас это аккуратный `MVP`, который уже полезен сам по себе и при этом оставляет хороший фундамент для следующих итераций.

## Оглавление

- [Быстрый старт](#быстрый-старт)
- [Небольшая история проекта](#небольшая-история-проекта)
- [Статус проекта](#статус-проекта)
- [Зачем появился этот проект](#зачем-появился-этот-проект)
- [Что делает проект сейчас](#что-делает-проект-сейчас)
- [Архитектура проекта](#архитектура-проекта)
- [Требования](#требования)
- [Установка](#установка)
- [Запуск collector](#запуск-collector)
- [Текущая конфигурация collector](#текущая-конфигурация-collector)
- [Контракт polling](#контракт-polling)
- [Подробное описание `PollResult`](#подробное-описание-pollresult)
- [Подробное описание `RawBlockResult`](#подробное-описание-rawblockresult)
- [Подробное описание `ErrorInfo`](#подробное-описание-errorinfo)
- [Локальный Modbus simulator](#локальный-modbus-simulator)
- [Подробное описание конфига симулятора](#подробное-описание-конфига-симулятора)
- [Как подключить collector к симулятору](#как-подключить-collector-к-симулятору)
- [Как быстро проверить, что все работает](#как-быстро-проверить-что-все-работает)
- [Тесты](#тесты)
- [Типовые сценарии использования](#типовые-сценарии-использования)
- [FAQ / Частые проблемы](#faq--частые-проблемы)
- [Ограничения текущего MVP](#ограничения-текущего-mvp)
- [Что можно развивать дальше](#что-можно-развивать-дальше)

## Статус проекта

Это именно **MVP**, а не завершенный production-ready продукт.

Сейчас в проекте уже есть:

- асинхронный polling `FC04`
- fallback на `FC03`
- структурированный результат чтения
- разделение ошибок на `DEVICE` и `TRANSPORT`
- reconnect-логика
- локальный `Modbus TCP simulator`
- тесты нескольких уровней: unit, scenario, integration

Пока еще нет:

- полноценного decode-слоя
- внешнего конфига collector
- сохранения в БД
- REST API
- reload конфигурации на лету

## Зачем появился этот проект

В реальной работе с промышленной автоматизацией почти всегда есть одни и те же неудобства:

- оборудование не всегда доступно
- PLC или gateway заняты
- стенд ограничен по времени
- карта регистров меняется по ходу интеграции
- нужно быстро проверить гипотезу, не трогая реальный объект
- нужно понимать, что именно происходит: нет связи, ошибка адреса, ошибка функции или просто пустой диапазон

`PSTG` появился как попытка сделать практичный инструмент, который можно:

- быстро запустить
- быстро изменить
- быстро проверить
- использовать в разработке, диагностике и дальнейшем развитии мониторинга станций

В этом смысле проект ближе к инженерному рабочему инструменту, чем к академической демонстрации.

## Что делает проект сейчас

Текущая реализация делает следующее:

1. Подключается к устройству по `Modbus TCP`
2. Читает `Input Registers` через `FC04`
3. Если устройство отвечает `device error`, делает fallback на `FC03`
4. Возвращает результат цикла чтения в виде `PollResult`
5. Отдельно хранит:
- состояние канала
- результат по каждому блоку чтения
- сырые регистры
- тип ошибки
- длительность чтения

Это уже позволяет:

- строить telemetry collector
- отлаживать register map
- наблюдать поведение канала связи
- тестировать fallback-логику
- писать дальнейший decode и monitoring-слой

## Архитектура проекта

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

### `app`

Слой orchestration.

Здесь находится:

- запуск collector
- сценарий опроса
- reconnect
- fallback `FC04 -> FC03`

### `drivers`

Слой работы с Modbus и transport-логикой.

Здесь находится:

- открытие TCP соединения
- чтение конкретных function code
- общая обвязка чтения блока

### `domain`

Слой доменных структур.

Здесь находятся dataclass и enum, которые описывают:

- результат polling
- результат чтения блока
- типы ошибок
- состояние соединения

### `simulator`

Локальный `Modbus TCP server` для разработки без PLC.

Он нужен, чтобы:

- писать код без реального оборудования
- проверять адреса и register map
- тестировать reconnect
- смотреть, как collector работает на меняющихся данных

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
- `DOWN`, если ни один блок не ответил и были только transport-ошибки

### `RawBlockResult.ok`

- `True`, если чтение успешно и ответ без `isError()`
- `False`, если был `device error` или `transport error`

### Ошибки

- `KindState.DEVICE` = устройство ответило Modbus exception
- `KindState.TRANSPORT` = ошибка сети, timeout, TCP, reconnect или сбой клиента

## Подробное описание `PollResult`

`PollResult` описывает **один полный цикл polling**.

Это не просто "пакет данных", а снимок состояния взаимодействия с устройством на конкретном такте опроса.

### Поля `PollResult`

#### `run_id: str`

Идентификатор запуска сервиса.

Сейчас поле заготовлено под дальнейшее развитие. Оно пригодится, когда понадобится:

- разделять несколько запусков collector
- связывать polling-сессии с логами
- хранить telemetry batches по `run_id`

#### `poll_seq: int`

Порядковый номер цикла опроса.

Полезен для:

- диагностики пропусков циклов
- анализа drift
- проверки стабильности polling loop
- последующего хранения time-series с номером итерации

#### `ts_poll_start: float`

Unix timestamp в секундах, когда начался цикл опроса.

Нужен для:

- временной привязки данных
- корреляции с логами PLC
- анализа задержек сети и устройства
- последующей записи в monitoring и historian системы

#### `ts_poll_end: float`

Unix timestamp в секундах, когда закончился цикл опроса.

Позволяет:

- измерять длительность полного цикла
- понимать, когда данные реально были получены
- сравнивать expected polling interval и фактическое поведение

#### `connection_state: ConnectionState | None`

Итоговое состояние канала связи по результату цикла.

Важно: это **не** признак валидности полезных данных, а именно признак того, жив ли канал общения с устройством.

Смысл:

- `UP` = устройство дало хотя бы один Modbus-ответ
- `DOWN` = ответа не было, были только transport-проблемы

#### `blocks: list[RawBlockResult]`

Список результатов по отдельным блокам чтения внутри одного цикла.

Обычно в текущей версии:

- первый блок: `FC04`
- второй блок: `FC03`

Это дает прозрачную диагностику:

- что было попыткой основного чтения
- был ли fallback
- какой блок вернул ошибку
- на каком function code реально пришел ответ

## Подробное описание `RawBlockResult`

`RawBlockResult` описывает **одну конкретную попытку чтения** одним Modbus function code.

Это low-level результат, который полезен:

- для диагностики
- для наблюдения за каналом связи
- для анализа register map
- для построения decode-слоя

### Поля `RawBlockResult`

#### `fc: int`

Номер Modbus function code.

Типичные значения:

- `4` = `Read Input Registers`
- `3` = `Read Holding Registers`

Поле нужно для:

- анализа fallback
- логирования
- отладки реального поведения PLC / RTU / gateway

#### `addr: int`

Стартовый Modbus адрес чтения, то есть offset.

Если:

- `addr = 0`
- `count = 12`

то чтение началось с адреса `0` и включало диапазон до `11`.

Это одно из самых полезных полей при отладке `register map`, `address map`, `Modbus addressing`, интеграции PLC и gateway.

#### `count: int`

Количество регистров, которое было запрошено подряд.

Это важно, потому что одно прикладное значение может занимать:

- 1 регистр
- 2 регистра
- 4 регистра

Например, когда позже появится decode:

- `uint16`
- `int16`
- `uint32`
- `int32`
- `float32`
- status words
- bit flags

#### `unit_id: int`

Modbus Unit ID / Slave ID.

Часто в Modbus TCP это `1`, но поле особенно важно, если:

- работа идет через gateway
- за одним IP скрыто несколько устройств
- эмулируется реальная схема Modbus TCP -> Modbus RTU

#### `ok: bool | None`

Флаг успешности именно этого блока чтения.

Смысл:

- `True` = ответ успешный, без `isError()`
- `False` = был `device error` или `transport error`
- `None` = блок фактически не использовался или еще не осмысленно заполнен

Важно: `ok` не равен состоянию канала. Канал оценивается через `PollResult.connection_state`.

#### `registers: list[int]`

Сырые значения Modbus регистров.

Это raw data, из которых потом можно строить:

- telemetry values
- counters
- analog signals
- digital state words
- alarm flags
- status bit masks
- engineering values после decode

В текущем проекте регистры сохраняются даже при `device error`, если библиотека вернула payload. Это сделано сознательно: для low-level диагностики и анализа нестандартного поведения Modbus-устройств.

#### `current_error_info: ErrorInfo | None`

Структурированная ошибка конкретного блока чтения.

Если поле `None`, значит для этого блока явная ошибка не зафиксирована.

Если поле заполнено, можно понять:

- ошибка transport или device
- есть ли Modbus exception code
- какой текст ошибки попал в результат

#### `duration_ms: float | None`

Длительность чтения этого блока в миллисекундах.

Полезно для:

- диагностики производительности
- оценки времени ответа PLC
- поиска lag и timeout
- анализа degradation сети или gateway

#### `ts_block_end: float | None`

Unix timestamp завершения чтения этого блока.

Это полезно, если:

- чтения идут последовательно
- нужно видеть момент завершения каждого Modbus request
- потом будет time-series storage или audit trail

## Подробное описание `ErrorInfo`

`ErrorInfo` это компактная структура для описания причины ошибки.

### Поля `ErrorInfo`

#### `message: str`

Человекочитаемое описание ошибки.

Нужно для:

- логирования
- диагностики
- быстрой инженерной отладки

#### `kind: KindState | None`

Тип ошибки.

Значения:

- `DEVICE` = устройство ответило Modbus exception
- `TRANSPORT` = ошибка сети, TCP, timeout, reconnect или сбой клиента

#### `exception_code: int | None`

Modbus exception code, если устройство ответило ошибкой.

Типовые примеры:

- `ILLEGAL FUNCTION`
- `ILLEGAL DATA ADDRESS`
- `ILLEGAL DATA VALUE`
- `SERVER DEVICE FAILURE`
- `GATEWAY TARGET DEVICE FAILED TO RESPOND`

Это одно из ключевых полей для интеграции с реальным оборудованием и отладки карт регистров.

#### `exc_type: str | None`

Дополнительный тип transport-исключения.

Сейчас это поле зарезервировано под дальнейшее развитие и более подробную диагностику.

## Локальный Modbus simulator

Симулятор нужен для разработки без PLC, RTU, gateway и другого оборудования.

Он умеет:

- поднимать локальный `Modbus TCP server`
- отдавать `FC04` и `FC03`
- настраивать адреса регистров через JSON
- автоматически менять значения по таймеру

Это делает проект пригодным для:

- локальной разработки
- проверки гипотез
- тестирования polling logic
- отладки register map
- проверки telemetry pipeline без стенда

### Быстрый старт симулятора

Запуск со встроенным конфигом:

```powershell
uv run python -m pstg.simulator.server
```

Значения по умолчанию:

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

## Подробное описание конфига симулятора

### `host`

IP-адрес, на котором стартует локальный Modbus server.

Обычно:

- `127.0.0.1` для локальной разработки
- `0.0.0.0` если надо подключаться с другой машины

### `port`

TCP порт сервера.

Для локальной разработки удобно использовать не `502`, а безопасный пользовательский порт, например `1502`.

### `device_id`

Unit ID / Slave ID, который должен совпадать с настройкой клиента.

### `input_registers`

Список блоков для `FC04`.

Подходит для эмуляции:

- аналоговых измерений
- показаний датчиков
- телеметрии
- числовых значений процесса

### `holding_registers`

Список блоков для `FC03`.

Подходит для эмуляции:

- внутренних регистров PLC
- конфигурационных параметров
- fallback-данных
- нестандартных устройств, которые не отдают данные в `FC04`

### Формат JSON

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

### Поля блока регистров

#### `address`

Стартовый адрес блока.

Если:

- `address = 10`
- `values = [501, 502]`

то будут заполнены адреса `10` и `11`.

#### `values`

Начальные значения регистров.

Это raw `16-bit` значения, которые потом клиент сможет:

- читать как есть
- декодировать
- интерпретировать как telemetry, status, alarms, flags

#### `interval_s`

Необязательный интервал автообновления блока в секундах.

Если поле не задано, блок остается статичным.

#### `step`

Необязательный шаг изменения значений.

При каждом срабатывании таймера каждое значение увеличивается на `step`.

### Режим автообновления

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

Это полезно для:

- проверки трендов
- проверки того, что polling видит изменение данных
- разработки decode-слоя
- тестирования time-series логики

## Как подключить collector к симулятору

Убедись, что в collector настроено:

- host: `127.0.0.1`
- port: `1502`
- `device_id = 1`

После этого:

1. Запусти симулятор
2. Запусти collector
3. Смотри логи сервера и клиента

## Как быстро проверить, что все работает

Ниже самый практичный сценарий быстрой проверки, без PLC и без стенда.

### Шаг 1. Установить зависимости

Из корня проекта:

```powershell
uv sync
uv pip install -e .
```

### Шаг 2. Проверить настройки collector

Убедись, что в collector стоят:

- host: `127.0.0.1`
- port: `1502`
- `device_id = 1`

Файлы:

- [modbus_corfig.py](C:\repos-win\source\pstg\src\pstg\app\modbus_corfig.py)
- [read_config.py](C:\repos-win\source\pstg\src\pstg\app\read_config.py)

### Шаг 3. Запустить simulator

```powershell
uv run python -m pstg.simulator.server
```

Что должно появиться в логах:

- сервер стартовал
- включено автообновление хотя бы одного блока
- идут строки `Updated fc...`

Типичный пример:

```text
Starting Modbus simulator on 127.0.0.1:1502 device_id=1
Auto-update enabled for fc4 address=0 interval_s=1.0 step=1
Auto-update tasks started: 2
Updated fc4 address=0 values=[102, 103, 104, 105]
```

### Шаг 4. Запустить collector

В другом окне терминала:

```powershell
uv run python -m pstg.app.collector
```

### Шаг 5. Проверить, что есть связь

В логах collector должны появиться:

- попытка подключения
- успешный connect
- результаты polling

Если все в порядке, ты увидишь:

- `connection_state = UP`
- блок `FC04` с регистрами
- новые значения на следующих циклах

### Шаг 6. Проверить, что значения реально меняются

Смотри одновременно на:

1. логи simulator
2. логи collector

Если simulator пишет:

```text
Updated fc4 address=0 values=[103, 104, 105, 106]
Updated fc4 address=0 values=[104, 105, 106, 107]
```

то в collector через несколько циклов тоже должны появляться новые значения.

### Шаг 7. Проверить fallback на `FC03`

Для этого можно:

1. изменить конфиг simulator так, чтобы нужный диапазон `FC04` стал невалидным
2. положить рабочие данные в `holding_registers`
3. перезапустить simulator
4. снова запустить collector

Тогда можно увидеть:

- `device error` на `FC04`
- fallback на `FC03`
- итоговый `connection_state = UP`

### Шаг 8. Проверить тесты

```powershell
.\\.venv\\Scripts\\python.exe -m pytest tests -q
```

или

```powershell
uv run pytest tests -q
```

Если тесты проходят, значит текущий `MVP` в рабочем состоянии:

- unit level
- scenario level
- integration level
- simulator level

## Тесты

В проекте уже есть тесты нескольких уровней. Это важно: они проверяют не только отдельные функции, но и текущее поведение проекта как telemetry MVP.

### Unit tests

Проверяют изолированную логику без реального Modbus server.

Что покрыто:

- успешный `read_block`
- `device error` в `read_block`

Файлы:

- [test_read_block_success.py](C:\repos-win\source\pstg\tests\test_read_block_success.py)
- [test_read_block_device_error.py](C:\repos-win\source\pstg\tests\test_read_block_device_error.py)

### Scenario tests

Проверяют один сценарий orchestration через заглушки и monkeypatch.

Что покрыто:

- fallback `FC04 -> FC03`
- reconnect после `DOWN`

Файлы:

- [test_poll_device_fallback.py](C:\repos-win\source\pstg\tests\test_poll_device_fallback.py)
- [test_poll_forever_reconnect.py](C:\repos-win\source\pstg\tests\test_poll_forever_reconnect.py)

### Integration tests с реальным Modbus server

Проверяют проект на настоящем `pymodbus.server.ModbusTcpServer`.

Что покрыто:

- чтение `FC04`
- `poll_device` на успешном чтении
- `poll_device` на `device error`

Файлы:

- [test_real_server_fc04_read.py](C:\repos-win\source\pstg\tests\test_real_server_fc04_read.py)
- [test_real_server_poll_device_success.py](C:\repos-win\source\pstg\tests\test_real_server_poll_device_success.py)
- [test_real_server_poll_device_device_error.py](C:\repos-win\source\pstg\tests\test_real_server_poll_device_device_error.py)

### Integration tests для simulator

Проверяют локальный development simulator.

Что покрыто:

- загрузка конфига
- запуск dev server
- чтение из simulator
- автообновление регистров по таймеру

Файлы:

- [test_simulator_config.py](C:\repos-win\source\pstg\tests\test_simulator_config.py)
- [test_simulator_server_runtime.py](C:\repos-win\source\pstg\tests\test_simulator_server_runtime.py)
- [test_simulator_auto_update.py](C:\repos-win\source\pstg\tests\test_simulator_auto_update.py)

### Запуск тестов

Полный запуск:

```powershell
.\\.venv\\Scripts\\python.exe -m pytest tests -q
```

или

```powershell
uv run pytest tests -q
```

## Типовые сценарии использования

### 1. Разработка без реального PLC

Поднимается simulator, collector подключается к нему, и можно спокойно писать код опроса, reconnect и decode.

### 2. Проверка карты регистров

Через simulator удобно проверять:

- адреса
- диапазоны чтения
- длину блока
- fallback

### 3. Подготовка telemetry / monitoring логики

Автоизменяемые регистры полезны, чтобы видеть живой поток значений и проверять дальнейшую работу time-series слоя.

### 4. Диагностика проблем связи

Даже на текущем `MVP` уровне проект уже полезен для инженерной диагностики:

- устройство отвечает или нет
- это `device error` или `transport error`
- работает ли fallback
- стабильна ли связь

## FAQ / Частые проблемы

### Симулятор запущен, но collector не подключается

Проверь, что совпадают:

- `host`
- `port`
- `device_id`

Чаще всего проблема в том, что:

- simulator поднят на `1502`
- а collector смотрит в другой порт

Или:

- simulator запущен с одним `device_id`
- а collector читает другой

Проверь файлы:

- [modbus_corfig.py](C:\repos-win\source\pstg\src\pstg\app\modbus_corfig.py)
- [read_config.py](C:\repos-win\source\pstg\src\pstg\app\read_config.py)
- [simulator.example.json](C:\repos-win\source\pstg\simulator.example.json)

### Симулятор запущен, но значения "не меняются"

Проверь, есть ли в конфиге блока:

- `interval_s`
- `step`

Если этих полей нет, блок будет статичным.

Также смотри логи сервера. При включенном автообновлении должны быть строки вида:

```text
Auto-update enabled for fc4 address=0 interval_s=1.0 step=1
Updated fc4 address=0 values=[...]
```

Если запускаешь simulator без `--config`, используется встроенный дефолтный конфиг, в котором автообновление сейчас уже включено.

### Значения меняются, но в collector это плохо заметно

Обычно причина в том, что:

- читается слишком большой диапазон регистров
- меняется только часть блока
- шаг изменения слишком маленький

Например:

- collector читает `12` регистров
- а в simulator меняются только первые `4`

В таком случае визуально может казаться, что "ничего не происходит".

Для явной проверки:

1. временно уменьши `READ_DATA_COUNT`
2. увеличь `step`
3. смотри не только клиентские логи, но и серверные

### Почему `connection_state = UP`, если `ok = False`

Это ожидаемое поведение по текущему контракту.

Смысл такой:

- `connection_state = UP` означает, что устройство ответило
- `ok = False` означает, что этот ответ был неуспешным для полезных данных

Пример:

- пришел `Modbus exception`
- канал жив
- ответ есть
- но данные невалидны

Поэтому:

- `connection_state = UP`
- `ok = False`
- `current_error_info.kind = DEVICE`

### Почему fallback на `FC03` не всегда выполняется

Fallback выполняется только если основной `FC04` вернул `DEVICE` error.

Если `FC04`:

- успешно вернул данные

то fallback не нужен.

Если `FC04`:

- не дал ответа и произошел `TRANSPORT` error

то это уже не "ошибка содержимого", а проблема связи.

### Почему регистры сохраняются даже при `device error`

Это сделано специально для low-level диагностики.

Некоторые устройства или библиотеки могут вернуть полезный payload даже в ошибочном ответе. Для дальнейшего анализа register map, нестандартного поведения PLC или gateway это бывает полезно.

Но использовать такие данные в прикладной логике нужно осторожно.

### Почему тесты проходят с предупреждением `PytestCacheWarning`

Причина не в тестах, а в правах доступа к `.pytest_cache`.

Это означает:

- `pytest` не смог записать cache
- сами тесты при этом могут быть полностью корректными

Если хочешь убрать предупреждение правильно, надо восстановить права записи для текущего пользователя в корень проекта и `.pytest_cache`.

### Почему в логах видно reconnect и у клиента, и у приложения

Это нормально.

Есть два уровня логики:

1. reconnect внутри `pymodbus` клиента
2. reconnect на уровне самого `PSTG`

Это не дублирование ради дублирования, а разные уровни защиты:

- библиотека пытается пережить краткий сбой
- приложение умеет пересоздать сессию целиком

### С чего лучше начинать дальнейшее развитие проекта

Самый практичный порядок обычно такой:

1. вынести конфиг collector во внешний файл или env
2. добавить decode-слой
3. определить, куда сохранять telemetry
4. добавить API или экспорт данных
5. расширять simulator под реальные сценарии

## Ограничения текущего MVP

- конфиг collector пока hardcoded
- нет полноценного decode-слоя
- нет хранения в базе
- нет REST API
- нет reload конфига симулятора на лету
- coils и discrete inputs пока не настраиваются через JSON

## Что можно развивать дальше

- внешний конфиг для collector
- decode `uint16/int16/int32/float32`
- запись в time-series storage
- REST API
- расширение simulator
- richer diagnostics и audit trail

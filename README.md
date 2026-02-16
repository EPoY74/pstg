# Pump Station Telemetry Gateway(Industrial и Water & Wastewater)

Ветки разработки:<br />
https://github.com/EPoY74/pstg/tree/wip/pstg-probe - считываю данные с PLC. Тестирование считывания.
https://github.com/EPoY74/pstg/tree/wip/modbus-async-core - разработка Modbus Poller.


### [upd.:20260216]

# PSTG — Async Modbus TCP Telemetry Gateway (Python, pymodbus, uv)

Асинхронный (async) опросчик Modbus TCP для телеметрии (telemetry) насосной станции: читает регистры **FC04 (Input Registers)** и при ошибке делает fallback на **FC03 (Holding Registers)**. На каждый цикл формирует структурированный результат `PollResult` с детализацией по блокам чтения.

## Features
- **Async Modbus TCP polling** через `pymodbus.client.AsyncModbusTcpClient`
- Чтение регистров:
  - primary: **FC04** (Input Registers)
  - fallback: **FC03** (Holding Registers)
- Метрики:
  - `duration_ms` (замер `time.perf_counter()`)
  - `ts_poll_start / ts_poll_end` (epoch seconds через `time.time()`)
- Ошибки:
  - Modbus exception code (если пришёл от устройства)
  - transport/runtime ошибки (если упало на стороне клиента/сети)

## Project layout
```
src/
  pstg/
    app/
      collector.py                 # entrypoint (точка входа)
      modbus_corfig.py             # get_modbus_config()
      read_config.py               # get_device_read_settings()
    drivers/
      open_connection_modbus_tcp.py
      read_fc03_holding_register.py
      read_fc04_input_regoster.py
    domain/
      modbus_config.py
      modbus_device_read_settings.py
      poll_result.py
      raw_block_result.py
      error_info.py
      connection_state.py
      kind_state.py
```

## Requirements
- Python 3.10+
- `uv`
- `pymodbus`

## Install `uv` (global)

### macOS / Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Windows (PowerShell)
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Проверка:
```bash
uv --version
```

## Setup project environment (required)
> ВАЖНО: без этих шагов запуск “как модуль” (`python -m ...`) из корня проекта может не работать, потому что пакет `pstg` не будет установлен/виден в окружении.

1) Синхронизировать окружение проекта (создаст `.venv`, поставит зависимости):
```bash
uv sync
```

2) Установить текущий проект как **editable** пакет (чтобы `pstg` импортировался из корня репозитория):
```bash
uv pip install -e .
```

## Run
Запуск из корня репозитория:
```bash
uv run python -m pstg.app.collector
```

Остановка:
- `Ctrl + C` (обрабатывается `KeyboardInterrupt`, соединение закрывается)

## Configuration (currently hardcoded)

### Modbus TCP connection
Файл: `pstg/app/modbus_corfig.py`
- `DEVICE_IP = "10.0.6.10"`
- `DEVICE_PORT = 506`
- `DEVICE_POLL_INTERVAL_S = 2`

### Read settings
Файл: `pstg/app/read_config.py`
- `DEVICE_ID = 1` (Unit ID)
- `DATA_OFFSET = 0` (offset / стартовый адрес)
- `READ_DATA_COUNT = 12` (сколько регистров читать)

## What the poll returns
Каждый цикл опроса возвращает `PollResult`:
- `connection_state`: `UP`, если успешен хотя бы один блок (FC04 или FC03), иначе `DOWN`
- `ts_poll_start`, `ts_poll_end`: epoch seconds
- `blocks`: список из 2 блоков `RawBlockResult` (FC04 + FC03)

`RawBlockResult` содержит:
- `fc` (3 или 4), `unit_id`, `addr`, `count`
- `ok`, `registers`
- `duration_ms`, `ts_block_end`
- `error` (если была ошибка)

## Notes
- Порт Modbus TCP обычно 502, но здесь используется **506** (это допустимо для конкретного стенда/шлюза/ПЛК).
- В коде есть TODO: сделать “ровный” период опроса без дрейфа (учитывать длительность чтения и спать остаток).

<br />

### [founded:20260209]

Pump Station Telemetry Gateway — сервис/демон для сбора телеметрии насосных станций в промышленной автоматизации (OT/SCADA) и коммунальной инфраструктуре: получает значения и состояния через подключаемые драйверы (например, Modbus RTU/TCP через RTU↔Ethernet шлюзы или эмулятор), приводит сигналы к каноническому формату и сохраняет их в SQL-хранилище как временные ряды. Проект учитывает нестабильную связь и недоступность оборудования, поэтому использует плагинную архитектуру драйверов, симулятор для разработки и контрактные тесты формата данных.

Сервис предоставляет REST API для интеграций и дашбордов: выборки time-series и простые тренды, события (events), аварии/алармы (alarms) и аудит действий (audit log). Визуализацию можно вынести в отдельный веб-дашборд или подключить внешние инструменты мониторинга и аналитики (например, Grafana), а CLI применяется как админ-инструмент для миграций и обслуживания (migrate/seed/health/simulate/import/export).

Разработка ведётся итеративно: сначала MVP “сбор → хранение → API → тренды”, затем правила алармов, журналирование, роли и права доступа, команды управления и сценарии отказоустойчивости; каждую неделю — небольшой вертикальный релиз с миграциями и тестами.

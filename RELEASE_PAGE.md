# PSTG MVP

Русская версия. English version: [RELEASE_PAGE.en.md](RELEASE_PAGE.en.md)

Связанные документы:
- [README.md](README.md)
- [RELEASE_NOTES.md](RELEASE_NOTES.md)
- [CHANGELOG.md](CHANGELOG.md)
- [LICENSE](LICENSE)
- [NOTICE](NOTICE)

`PSTG` (`Pump Station Telemetry Gateway`) — это практический `MVP` для `Modbus TCP polling`, локальной telemetry-разработки и диагностики связи без обязательного доступа к реальному `PLC`, `RTU` или `Modbus gateway`.

Проект разрабатывался специалистом сервисного отдела **ООО "ЧЗМЭК"** (`ООО "Челябинский завод мобильных энергоустановок и конструкций"`) для личного использования как рабочий инструмент, который упрощает развитие мониторинга станций, отладку, проверку карт регистров и ежедневную инженерную работу.

## Ключевое

- async `Modbus TCP` collector
- fallback `FC04 -> FC03`
- явное разделение `device error` и `transport error`
- reconnect-логика
- локальный `Modbus simulator`
- настраиваемая карта регистров через JSON
- автообновление регистров по таймеру
- unit, scenario и integration tests
- расширенная документация с quick start, FAQ и troubleshooting

## Почему этот релиз важен

Этот релиз позволяет:

- разрабатывать и отлаживать `Modbus TCP` telemetry-логику без физического оборудования
- валидировать `register map` и `address map`
- проверять fallback и reconnect-сценарии
- наблюдать изменяющиеся значения для будущих time-series и monitoring задач
- быстрее развивать tooling для мониторинга станций

## Что вошло

- асинхронный collector для `Modbus TCP`
- структурированные модели результатов: `PollResult`, `RawBlockResult`, `ErrorInfo`
- fallback с `FC04` на `FC03`
- reconnect на уровне приложения
- локальный development simulator
- формат simulator config и пример JSON
- режим автоизменения регистров
- тесты от unit уровня до integration уровня
- расширенная документация

## Текущие рамки

Это все еще `MVP`, а не финальная production-ready система.

Уже есть:

- polling
- fallback
- reconnect
- simulator
- тесты
- документация

Дальше планируются:

- внешний конфиг collector
- decode-слой
- database или time-series storage
- REST API
- более богатые simulator-сценарии

## Быстрый старт

Запуск simulator:

```powershell
uv run python -m pstg.simulator.server
```

Запуск collector:

```powershell
uv run python -m pstg.app.collector
```

## Лицензия

Проект распространяется под `Apache License 2.0`.

При использовании и распространении нужно сохранять [LICENSE](LICENSE) и [NOTICE](NOTICE), включая упоминание проекта `PSTG` и происхождения разработки.

## Фокус проекта

Проект особенно релевантен для:

- `SCADA`
- `industrial automation`
- `industrial IoT`
- `telemetry`
- `monitoring`
- `pump station monitoring`
- `Modbus TCP`
- `PLC integration`
- `RTU integration`
- `diagnostics`

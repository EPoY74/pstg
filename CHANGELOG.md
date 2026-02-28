# Changelog

Русская версия. English version: [CHANGELOG.en.md](CHANGELOG.en.md)

Связанные документы:
- [README.md](README.md)
- [RELEASE_NOTES.md](RELEASE_NOTES.md)
- [RELEASE_PAGE.md](RELEASE_PAGE.md)
- [LICENSE](LICENSE)
- [NOTICE](NOTICE)

Все заметные изменения проекта собираются здесь.

## [0.1.0] - 2026-02-28

### Добавлено

- асинхронный `Modbus TCP` collector
- fallback `FC04 -> FC03`
- структурированные модели результатов: `PollResult`, `RawBlockResult`, `ErrorInfo`
- разделение `DEVICE` и `TRANSPORT` ошибок
- reconnect-логика в collector
- локальный development `Modbus simulator`
- JSON-конфиг для simulator
- режим автообновления регистров по таймеру
- unit, scenario, integration и simulator tests
- расширенная документация и FAQ
- английские версии релизных документов
- лицензионные файлы `LICENSE` и `NOTICE`

### Изменено

- упрощена orchestration-логика в `collector.py`
- общая логика чтения блока вынесена в `read_block.py`
- поведение `connection_state` приведено к контракту polling
- улучшено поведение fallback при `device error`
- синхронизированы `README`, `release notes` и `release page`

### Примечания

- текущий релиз — это `MVP`
- проект разрабатывался как практический инженерный инструмент для мониторинга станций и `Modbus TCP` telemetry специалистом сервисного отдела ООО "ЧЗМЭК" (ООО «Челябинский завод мобильных энергоустановок и конструкций»)
- текущая реализация подходит для разработки, диагностики и дальнейших итераций без постоянной зависимости от физического оборудования
- условия использования и обязательное сохранение упоминания описаны в [LICENSE](LICENSE) и [NOTICE](NOTICE)

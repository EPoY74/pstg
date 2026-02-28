# Release Notes

Русская версия. English version: [RELEASE_NOTES.en.md](RELEASE_NOTES.en.md)

Связанные документы:
- [README.md](README.md)
- [CHANGELOG.md](CHANGELOG.md)
- [RELEASE_PAGE.md](RELEASE_PAGE.md)
- [LICENSE](LICENSE)
- [NOTICE](NOTICE)

## PSTG MVP

`PSTG` (`Pump Station Telemetry Gateway`) на текущем этапе представляет собой рабочий `MVP` для `Modbus TCP polling`, локальной `telemetry`-разработки и диагностики связи без обязательного доступа к реальному `PLC`, `RTU` или `Modbus gateway`.

Проект разрабатывался для собственных нужд специалистом сервисного отдела **ООО "ЧЗМЭК"** (`ООО "Челябинский завод мобильных энергоустановок и конструкций"`) как практический инструмент для ускорения мониторинга станций, проверки карт регистров, локальной отладки и дальнейшего развития telemetry-логики.

Проект ориентирован на практические инженерные задачи:

- `SCADA`
- `industrial automation`
- `industrial IoT`
- `pump station monitoring`
- `station telemetry`
- `Modbus TCP integration`
- `register map validation`
- `monitoring and diagnostics`

## Основные результаты релиза

В этом релизе собран рабочий базовый контур:

- async `Modbus TCP` collector
- fallback `FC04 -> FC03`
- разделение `device error` и `transport error`
- reconnect-логика
- локальный `Modbus simulator`
- автоизменение регистров по таймеру
- набор тестов от unit до integration
- расширенная документация

## Что появилось

### 1. Collector

Реализован асинхронный polling `Modbus TCP` устройства.

Текущая логика:

- сначала читается `FC04`
- при `device error` выполняется fallback на `FC03`
- результат возвращается как `PollResult`
- `connection_state = UP`, если хотя бы один блок дал Modbus-ответ
- `connection_state = DOWN`, если ни один блок не ответил и были только transport-ошибки

### 2. Контракт результата

Введены структурированные модели:

- `PollResult`
- `RawBlockResult`
- `ErrorInfo`

Это упрощает:

- диагностику
- дальнейший decode
- логирование
- интеграцию с monitoring и time-series системами

### 3. Разделение типов ошибок

Ошибки разделены на:

- `KindState.DEVICE`
- `KindState.TRANSPORT`

Это важно для реальной интеграции с `PLC`, `RTU`, `Modbus gateway` и `register map`.

### 4. Reconnect

Добавлена reconnect-логика на уровне приложения.

Теперь проект умеет:

- переоткрывать сессию
- продолжать polling после проблем связи
- отделять временный transport fail от живого Modbus-ответа с ошибкой устройства

### 5. Локальный Modbus simulator

Добавлен development simulator, который позволяет работать без физического оборудования.

Возможности:

- запуск локального `Modbus TCP server`
- настройка адресов и значений через JSON
- эмуляция `FC04` и `FC03`
- автоизменение регистров по таймеру

### 6. Тесты

Добавлено покрытие нескольких уровней:

- `unit tests`
- `scenario tests`
- `integration tests`
- тесты simulator

Проверяется:

- успешное чтение
- `device error`
- fallback `FC04 -> FC03`
- reconnect
- работа через реальный test `Modbus server`
- runtime работа simulator
- автообновление регистров

### 7. Документация

Обновлены материалы проекта:

- `README.md` — основная документация и быстрый старт
- `CHANGELOG.md` — история изменений
- `RELEASE_PAGE.md` — текст для страницы релиза
- английские версии документов для публикации и внешнего использования

## Практическая ценность релиза

Этот релиз позволяет:

- разрабатывать collector без реального `PLC`
- проверять `Modbus TCP` логику локально
- тестировать fallback и reconnect
- валидировать `register map`
- наблюдать изменяющиеся telemetry-значения без стенда

Для инженерной разработки и мониторинга станций это уже полезный рабочий минимум.

## Ограничения

Текущий релиз — это `MVP`, поэтому пока отсутствуют:

- внешний конфиг collector
- полноценный decode-слой
- запись в БД
- REST API
- reload simulator config на лету

## Лицензия и упоминание

Проект распространяется под лицензией `Apache License 2.0`.

При использовании, распространении или создании производных материалов необходимо:

- сохранять файл [LICENSE](LICENSE)
- сохранять файл [NOTICE](NOTICE)
- не удалять упоминание проекта `PSTG` и автора происхождения из `NOTICE`

## Следующий логичный шаг

После этого релиза разумно развивать проект в сторону:

- внешнего конфига collector
- decode-слоя
- time-series storage
- REST API
- расширения simulator

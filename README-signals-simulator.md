# PSTG Combined Signals Simulator

Этот сценарий поднимает один Modbus TCP сервер, который одновременно отдает:

- `FC04` регистры
- `FC03` регистры
- выходные сигналы в `FC03`
- изменение значений по времени

## Быстрый запуск

Встроенный сценарий:

```powershell
uv run python -m pstg.simulator.signals_server
```

Через JSON-конфиг:

```powershell
uv run python -m pstg.simulator.server --config simulator.signals.example.json
```

## Что лежит по умолчанию

- `FC04` address `0`: `[101, 102, 103, 104]`, шаг `+1` раз в `1s`
- `FC03` address `0`: `[201, 202, 203, 204]`, шаг `+10` раз в `2s`
- `PT1` address `56`: `1.5`, шаг `+0.1` раз в `1s`
- `PT2` address `58`: `2.5`, шаг `+0.2` раз в `1s`
- `PT3` address `60`: `3.5`, шаг `+0.3` раз в `1s`
- `FlowPerHour` address `64`: `120.25`, шаг `+1.5` раз в `1s`
- `FlowAmount` address `66`: `456.75`, шаг `+5.0` раз в `1s`

## Формат `f32` блока

Для float-сигналов в `holding_registers` используются поля:

```json
{
  "address": 56,
  "values": [0, 16320],
  "interval_s": 1.0,
  "encoding": "f32",
  "float_step": 0.1
}
```

Где:

- `values` это стартовые Modbus-регистры для `float32`
- `encoding: "f32"` включает обновление как float, а не как сырые `u16`
- `float_step` задает приращение самого float-значения

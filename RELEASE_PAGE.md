# PSTG MVP

`PSTG` (`Pump Station Telemetry Gateway`) is a practical `MVP` for `Modbus TCP polling`, local telemetry development and communication diagnostics without mandatory access to real `PLC`, `RTU` or `Modbus gateway` hardware.

The project was developed by a specialist from **ООО "ЧЗМЭК" (ООО «Челябинский завод мобильных энергоустановок и конструкций»)** for personal use as a working tool to simplify station monitoring development, debugging and day-to-day engineering work.

## Highlights

- async `Modbus TCP` collector
- fallback `FC04 -> FC03`
- explicit separation of `device error` and `transport error`
- reconnect logic
- local `Modbus simulator`
- configurable register map through JSON
- timed auto-update of simulator registers
- unit, scenario and integration tests
- extended documentation with quick start, FAQ and troubleshooting guidance

## Why this release matters

This release makes it possible to:

- develop and debug Modbus telemetry logic without physical hardware
- validate `register map` and `address map`
- test fallback behavior and reconnect scenarios
- observe changing values over time for future time-series and monitoring work
- move faster when building station monitoring tooling

## Included changes

- added asynchronous collector for `Modbus TCP`
- added structured result models: `PollResult`, `RawBlockResult`, `ErrorInfo`
- added fallback from `FC04` to `FC03`
- added reconnect logic at application level
- added local development simulator
- added simulator config file format and example
- added timed register auto-update mode
- added tests from unit level to integration level
- expanded project documentation

## Current scope

This is still an `MVP`, not a production-ready final system.

Already included:

- polling
- fallback
- reconnect
- simulator
- tests
- documentation

Planned next:

- external collector configuration
- decode layer
- database or time-series storage
- REST API
- richer simulator scenarios

## Quick start

Run simulator:

```powershell
uv run python -m pstg.simulator.server
```

Run collector:

```powershell
uv run python -m pstg.app.collector
```

## Project focus

Relevant areas:

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

# PSTG MVP

English version. Russian version: [RELEASE_PAGE.md](RELEASE_PAGE.md)

Related documents:
- [README.en.md](README.en.md)
- [RELEASE_NOTES.en.md](RELEASE_NOTES.en.md)
- [CHANGELOG.en.md](CHANGELOG.en.md)
- [LICENSE](LICENSE)
- [NOTICE](NOTICE)

`PSTG` (`Pump Station Telemetry Gateway`) is a practical `MVP` for `Modbus TCP polling`, local telemetry development and communication diagnostics without mandatory access to real `PLC`, `RTU` or `Modbus gateway` hardware.

The project was developed by a specialist from the service department of **OOO "CHZMEK"** (`Chelyabinsk Plant of Mobile Power Units and Structures`) for personal use as a working tool to simplify station monitoring development, debugging, register map validation and day-to-day engineering work.

## Highlights

- async `Modbus TCP` collector
- fallback `FC04 -> FC03`
- explicit separation of `device error` and `transport error`
- reconnect logic
- local `Modbus simulator`
- configurable register map through JSON
- timed auto-update of simulator registers
- unit, scenario and integration tests
- expanded documentation with quick start, FAQ and troubleshooting guidance

## Why This Release Matters

This release makes it possible to:

- develop and debug `Modbus TCP` telemetry logic without physical hardware
- validate `register map` and `address map`
- test fallback behavior and reconnect scenarios
- observe changing values over time for future time-series and monitoring work
- move faster when building station monitoring tooling

## Included Changes

- asynchronous collector for `Modbus TCP`
- structured result models: `PollResult`, `RawBlockResult`, `ErrorInfo`
- fallback from `FC04` to `FC03`
- reconnect logic at application level
- local development simulator
- simulator config format and example
- timed register auto-update mode
- tests from unit level to integration level
- expanded documentation

## Current Scope

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

## Quick Start

Run the simulator:

```powershell
uv run python -m pstg.simulator.server
```

Run the collector:

```powershell
uv run python -m pstg.app.collector
```

## License

The project is distributed under the `Apache License 2.0`.

When using or redistributing the project, preserve [LICENSE](LICENSE) and [NOTICE](NOTICE).

## Project Focus

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

# Pump Station Telemetry Gateway

English version. Russian version: [README.md](README.md)

Related documents:
- [RELEASE_NOTES.en.md](RELEASE_NOTES.en.md)
- [CHANGELOG.en.md](CHANGELOG.en.md)
- [RELEASE_PAGE.en.md](RELEASE_PAGE.en.md)
- [LICENSE](LICENSE)
- [NOTICE](NOTICE)

`PSTG` is an `MVP` asynchronous `Modbus TCP` polling service for telemetry collection, communication diagnostics and local station monitoring.

The project was developed by a specialist from the service department of **OOO "CHZMEK"** (`Chelyabinsk Plant of Mobile Power Units and Structures`) for personal use as a working tool to simplify station monitoring development, debugging and day-to-day engineering work without a constant dependency on physical hardware, `PLC`, `RTU`, `Modbus gateway` devices or test benches.

The project is focused on practical engineering tasks:

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

## Quick Start

1. Install dependencies:

```powershell
uv sync
uv pip install -e .
```

2. Start the local Modbus simulator:

```powershell
uv run python -m pstg.simulator.server
```

3. In another terminal, start the collector:

```powershell
uv run python -m pstg.app.collector
```

4. Check the logs:

- simulator logs should contain `Updated fc...`
- collector logs should show polling results

## Project Story

This project was written as a practical engineering tool, not as a showcase pet project.

The initial goal was straightforward:

- read data over `Modbus TCP`
- test the logic without constant access to hardware
- quickly distinguish a device problem from a transport problem
- speed up station monitoring development

From that base, the project grew around a few necessary pieces:

- clear domain models
- fallback logic
- reconnect
- simulator
- tests

That is why `PSTG` is currently a compact but useful `MVP` with a clean foundation for future iterations.

## Release Documents

The current synchronized document set for version `0.1.0` (`2026-02-28`) includes:

- `README.md` / `README.en.md`
- `RELEASE_NOTES.md` / `RELEASE_NOTES.en.md`
- `CHANGELOG.md` / `CHANGELOG.en.md`
- `RELEASE_PAGE.md` / `RELEASE_PAGE.en.md`

## Project Status

This is an `MVP`, not a production-ready final product.

Already included:

- asynchronous `FC04` polling
- fallback to `FC03`
- structured polling result models
- separation of `DEVICE` and `TRANSPORT` errors
- reconnect logic
- local `Modbus TCP simulator`
- multi-level tests: unit, scenario and integration

Not included yet:

- full decode layer
- external collector config
- database persistence
- REST API
- live config reload

## Licensing

The project is distributed under the `Apache License 2.0`.

When using or redistributing the project, you must preserve:

- [LICENSE](LICENSE)
- [NOTICE](NOTICE)

The `NOTICE` file preserves attribution to `PSTG` and the origin of the project.

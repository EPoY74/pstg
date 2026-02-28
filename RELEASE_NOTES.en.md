# Release Notes

English version. Russian version: [RELEASE_NOTES.md](RELEASE_NOTES.md)

Related documents:
- [README.en.md](README.en.md)
- [CHANGELOG.en.md](CHANGELOG.en.md)
- [RELEASE_PAGE.en.md](RELEASE_PAGE.en.md)
- [LICENSE](LICENSE)
- [NOTICE](NOTICE)

## PSTG MVP

`PSTG` (`Pump Station Telemetry Gateway`) is currently a working `MVP` for `Modbus TCP polling`, local telemetry development and communication diagnostics without mandatory access to real `PLC`, `RTU` or `Modbus gateway` hardware.

The project was developed for personal internal use by a specialist from the service department of **OOO "CHZMEK"** (`Chelyabinsk Plant of Mobile Power Units and Structures`) as a practical tool for station monitoring, local debugging, register map validation and further telemetry development.

The project targets practical engineering tasks:

- `SCADA`
- `industrial automation`
- `industrial IoT`
- `pump station monitoring`
- `station telemetry`
- `Modbus TCP integration`
- `register map validation`
- `monitoring and diagnostics`

## Main Release Results

This release delivers a working baseline:

- async `Modbus TCP collector`
- fallback `FC04 -> FC03`
- explicit split between `device error` and `transport error`
- reconnect logic
- local `Modbus simulator`
- timed register auto-update
- tests from unit to integration level
- expanded documentation

## What Was Added

### 1. Collector

An asynchronous `Modbus TCP` polling flow is implemented.

Current behavior:

- `FC04` is read first
- `FC03` is used as a fallback on `device error`
- the result is returned as `PollResult`
- `connection_state = UP` when at least one block returns a Modbus response
- `connection_state = DOWN` when no block responds and only transport failures occur

### 2. Result Contract

Structured models were introduced:

- `PollResult`
- `RawBlockResult`
- `ErrorInfo`

This simplifies:

- diagnostics
- further decode work
- logging
- integration with monitoring and time-series systems

### 3. Error Separation

Errors are split into:

- `KindState.DEVICE`
- `KindState.TRANSPORT`

This matters for real integration with `PLC`, `RTU`, `Modbus gateway` devices and evolving `register map` definitions.

### 4. Reconnect

Reconnect logic was added at application level.

The project can now:

- reopen a session
- continue polling after communication problems
- distinguish a temporary transport failure from a valid Modbus response carrying a device exception

### 5. Local Modbus Simulator

A development simulator was added to support work without physical hardware.

Capabilities:

- run a local `Modbus TCP server`
- configure addresses and values through JSON
- emulate `FC04` and `FC03`
- auto-update registers on a timer

### 6. Tests

Multi-level coverage was added:

- `unit tests`
- `scenario tests`
- `integration tests`
- simulator tests

Covered behavior:

- successful reads
- `device error`
- fallback `FC04 -> FC03`
- reconnect
- operation against a real test `Modbus server`
- simulator runtime behavior
- register auto-update

### 7. Documentation

Project materials were expanded:

- `README.en.md` for the main documentation and quick start
- `CHANGELOG.en.md` for version history
- `RELEASE_PAGE.en.md` for release publication
- Russian counterparts for internal and primary project documentation

## Practical Value

This release makes it possible to:

- develop the collector without a real `PLC`
- validate `Modbus TCP` logic locally
- test fallback and reconnect behavior
- validate a `register map`
- observe changing telemetry values without a bench setup

For engineering work around station monitoring, this is already a useful baseline.

## Limitations

This release is still an `MVP`, so the following are not yet included:

- external collector config
- full decode layer
- database persistence
- REST API
- live simulator config reload

## License and Attribution

The project is distributed under the `Apache License 2.0`.

When using, redistributing or deriving from the project, you must preserve:

- [LICENSE](LICENSE)
- [NOTICE](NOTICE)

## Next Logical Steps

The next sensible directions are:

- external collector configuration
- decode layer
- time-series storage
- REST API
- richer simulator scenarios

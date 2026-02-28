# Changelog

Все заметные изменения проекта будут собираться здесь.

## [0.1.0] - 2026-02-28

### Added

- asynchronous `Modbus TCP` collector
- fallback `FC04 -> FC03`
- structured polling result models: `PollResult`, `RawBlockResult`, `ErrorInfo`
- separation of `DEVICE` and `TRANSPORT` errors
- reconnect logic in collector
- local development `Modbus simulator`
- JSON config for simulator
- timed auto-update for simulator registers
- unit, scenario, integration and simulator tests
- expanded project documentation and FAQ

### Changed

- simplified polling orchestration in `collector.py`
- extracted shared block read flow into `read_block.py`
- aligned `connection_state` behavior with the polling contract
- improved fallback behavior for `device error`

### Notes

- this release is an `MVP`
- the project was developed as a practical engineering tool for station monitoring and Modbus telemetry work
- current implementation is suitable for development, diagnostics and further iteration without permanent dependency on physical hardware


## Release documents

- `README.md` contains the main technical documentation, quick start, FAQ and simulator guide
- `RELEASE_NOTES.md` contains the detailed release summary
- `RELEASE_PAGE.md` contains the ready-to-publish release page text

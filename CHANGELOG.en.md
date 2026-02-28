# Changelog

English version. Russian version: [CHANGELOG.md](CHANGELOG.md)

Related documents:
- [README.en.md](README.en.md)
- [RELEASE_NOTES.en.md](RELEASE_NOTES.en.md)
- [RELEASE_PAGE.en.md](RELEASE_PAGE.en.md)
- [LICENSE](LICENSE)
- [NOTICE](NOTICE)

All notable project changes are collected here.

## [0.1.0] - 2026-02-28

### Added

- asynchronous `Modbus TCP` collector
- fallback `FC04 -> FC03`
- structured result models: `PollResult`, `RawBlockResult`, `ErrorInfo`
- explicit separation of `DEVICE` and `TRANSPORT` errors
- reconnect logic in the collector
- local development `Modbus simulator`
- JSON configuration for the simulator
- timed register auto-update mode
- unit, scenario, integration and simulator tests
- expanded documentation and FAQ
- English release documents
- licensing files `LICENSE` and `NOTICE`

### Changed

- simplified orchestration logic in `collector.py`
- extracted shared block read flow into `read_block.py`
- aligned `connection_state` behavior with the polling contract
- improved fallback behavior for `device error`
- synchronized `README`, release notes and release page documents

### Notes

- this release is an `MVP`
- the project was developed as a practical engineering tool for station monitoring and `Modbus TCP` telemetry
- the current implementation is suitable for development, diagnostics and further iteration without permanent dependency on physical hardware
- usage conditions and attribution requirements are described in [LICENSE](LICENSE) and [NOTICE](NOTICE)

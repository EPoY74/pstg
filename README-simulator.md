# PSTG Modbus Simulator

This simulator lets you run and improve `pstg` without real PLC or gateway hardware.

It starts a Modbus TCP server with configurable:

- `host`
- `port`
- `device_id`
- `input_registers` for FC04
- `holding_registers` for FC03

## Why it is useful

Use it when you want to:

- develop `pstg` without physical equipment
- test address maps
- check fallback `FC04 -> FC03`
- debug reconnect logic
- prepare new polling code safely

## Requirements

- Python 3.12+
- project dependencies installed

From the repository root:

```powershell
uv sync
uv pip install -e .
```

## Quick start

Run with built-in default registers:

```powershell
uv run python -m pstg.simulator.server
```

Default values:

- host: `127.0.0.1`
- port: `1502`
- device_id: `1`
- FC04 registers at address `0`: `[101, 102, 103, 104]`
- FC03 registers at address `0`: `[201, 202, 203, 204]`

## Run with config file

Example config file: [simulator.example.json](C:\repos-win\source\pstg\simulator.example.json)

Run:

```powershell
uv run python -m pstg.simulator.server --config simulator.example.json
```

## Override config from CLI

You can override network settings without changing JSON:

```powershell
uv run python -m pstg.simulator.server --config simulator.example.json --host 0.0.0.0 --port 1503 --device-id 2
```

## Config format

Example:

```json
{
  "host": "127.0.0.1",
  "port": 1502,
  "device_id": 1,
  "input_registers": [
    { "address": 0, "values": [101, 102, 103, 104] },
    { "address": 10, "values": [501, 502] }
  ],
  "holding_registers": [
    { "address": 0, "values": [201, 202, 203, 204] },
    { "address": 20, "values": [901, 902, 903] }
  ]
}
```

Meaning:

- each block writes several values starting from `address`
- `input_registers` are used by FC04
- `holding_registers` are used by FC03

## Connect PSTG to simulator

Point your collector config to:

- host: `127.0.0.1`
- port: `1502`
- device_id: `1`

Then run your collector:

```powershell
uv run python -m pstg.app.collector
```

## Typical dev scenarios

### 1. Happy path for FC04

Set values in `input_registers` and let `pstg` read them through FC04.

### 2. Fallback to FC03

Leave FC04 addresses invalid for the poll range, but configure valid values in FC03.
This helps you test fallback behavior.

### 3. Address map experiments

Add several blocks with different start addresses and verify that your code reads the expected range.

## Current limitations

- values are static after startup
- config reload is not implemented
- coils and discrete inputs are allocated but not configured from JSON

This is enough for current PSTG development, tests, and further refactoring.

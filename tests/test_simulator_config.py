from pathlib import Path

from pstg.simulator.config import load_simulator_config


def test_load_simulator_config_reads_register_blocks() -> None:
    config_path = Path("tests") / "_simulator_config_test.json"
    config_path.write_text(
        (
            "{\n"
            '  "host": "127.0.0.1",\n'
            '  "port": 1502,\n'
            '  "device_id": 3,\n'
            '  "input_registers": [\n'
            '    { "address": 0, "values": [10, 20], "interval_s": 1.5, "step": 2, "encoding": "raw" }\n'
            "  ],\n"
            '  "holding_registers": [\n'
            '    { "address": 5, "values": [30, 40, 50], "encoding": "f32", "float_step": 0.5 }\n'
            "  ]\n"
            "}\n"
        ),
        encoding="utf-8",
    )

    try:
        config = load_simulator_config(config_path)
    finally:
        config_path.unlink(missing_ok=True)

    assert config.host == "127.0.0.1"
    assert config.port == 1502
    assert config.device_id == 3
    assert config.input_registers is not None
    assert config.input_registers[0].address == 0
    assert config.input_registers[0].values == [10, 20]
    assert config.input_registers[0].interval_s == 1.5
    assert config.input_registers[0].step == 2
    assert config.input_registers[0].encoding == "raw"
    assert config.holding_registers is not None
    assert config.holding_registers[0].address == 5
    assert config.holding_registers[0].values == [30, 40, 50]
    assert config.holding_registers[0].encoding == "f32"
    assert config.holding_registers[0].float_step == 0.5

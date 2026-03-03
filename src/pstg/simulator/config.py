import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal


@dataclass(slots=True)
class RegisterBlockConfig:
    address: int
    values: list[int]
    interval_s: float | None = None
    step: int = 1
    encoding: Literal["raw", "f32"] = "raw"
    float_step: float | None = None


@dataclass(slots=True)
class SimulatorConfig:
    host: str = "127.0.0.1"
    port: int = 1502
    device_id: int = 1
    input_registers: list[RegisterBlockConfig] | None = None
    holding_registers: list[RegisterBlockConfig] | None = None


def _parse_register_blocks(raw_blocks: list[dict] | None) -> list[RegisterBlockConfig]:
    if not raw_blocks:
        return []

    blocks: list[RegisterBlockConfig] = []
    for block in raw_blocks:
        address = int(block["address"])
        values = [int(value) for value in block["values"]]
        interval_s = block.get("interval_s")
        step = int(block.get("step", 1))
        blocks.append(
            RegisterBlockConfig(
                address=address,
                values=values,
                interval_s=float(interval_s) if interval_s is not None else None,
                step=step,
                encoding=block.get("encoding", "raw"),
                float_step=(
                    float(block["float_step"])
                    if block.get("float_step") is not None
                    else None
                ),
            )
        )
    return blocks


def default_simulator_config() -> SimulatorConfig:
    return SimulatorConfig(
        input_registers=[
            RegisterBlockConfig(
                address=0,
                values=[101, 102, 103, 104],
                interval_s=1.0,
                step=1,
            ),
        ],
        holding_registers=[
            RegisterBlockConfig(
                address=0,
                values=[201, 202, 203, 204],
                interval_s=2.0,
                step=10,
            ),
        ],
    )


def load_simulator_config(config_path: str | Path | None) -> SimulatorConfig:
    if config_path is None:
        return default_simulator_config()

    path = Path(config_path)
    raw_data = json.loads(path.read_text(encoding="utf-8"))

    return SimulatorConfig(
        host=raw_data.get("host", "127.0.0.1"),
        port=int(raw_data.get("port", 1502)),
        device_id=int(raw_data.get("device_id", 1)),
        input_registers=_parse_register_blocks(raw_data.get("input_registers")),
        holding_registers=_parse_register_blocks(raw_data.get("holding_registers")),
    )

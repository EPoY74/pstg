from dataclasses import dataclass


@dataclass
class ModbusConfig:
    host: str
    port: int
    poll_interval_s: int

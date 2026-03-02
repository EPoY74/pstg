import argparse
import logging

from pymodbus.client import AsyncModbusTcpClient

from pstg.app.read_signal_config import get_signals_config
from pstg.domain.signal_spec import SignalSpec
from pstg.simulator.config import RegisterBlockConfig, SimulatorConfig
from pstg.simulator.server import init_logging, run_server

logger = logging.getLogger(__name__)


DEFAULT_SIGNAL_VALUES: dict[str, float] = {
    "PT1": 1.5,
    "PT2": 2.5,
    "PT3": 3.5,
    "FlowPerHour": 120.25,
    "FlowAmount": 456.75,
}


def _encode_signal_value(signal: SignalSpec, value: float) -> list[int]:
    if signal.dtype != "f32":
        raise ValueError(f"Unsupported signal dtype: {signal.dtype}")

    return AsyncModbusTcpClient.convert_to_registers(
        value,
        AsyncModbusTcpClient.DATATYPE.FLOAT32,
        word_order=signal.word_order.lower(),
    )


def build_signals_server_config(
    signal_values: dict[str, float] | None = None,
    *,
    host: str = "127.0.0.1",
    port: int = 1505,
    device_id: int = 1,
) -> SimulatorConfig:
    configured_values = DEFAULT_SIGNAL_VALUES | (signal_values or {})
    signals_config = get_signals_config()

    holding_registers = [
        RegisterBlockConfig(
            address=signal.addr,
            values=_encode_signal_value(
                signal,
                configured_values[signal.signal_name],
            ),
        )
        for signal in signals_config.signals_map
    ]

    return SimulatorConfig(
        host=host,
        port=port,
        device_id=device_id,
        input_registers=[],
        holding_registers=holding_registers,
    )


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run Modbus TCP server with output signal values for PSTG",
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=1505)
    parser.add_argument("--device-id", type=int, default=1)
    return parser


def main() -> None:
    init_logging()

    args = build_argument_parser().parse_args()
    config = build_signals_server_config(
        host=args.host,
        port=args.port,
        device_id=args.device_id,
    )

    logger.info("Starting signal server on %s:%s device_id=%s", args.host, args.port, args.device_id)
    logger.info("Output signals: %s", DEFAULT_SIGNAL_VALUES)
    try:
        import asyncio

        asyncio.run(run_server(config))
    except KeyboardInterrupt:
        logger.info("Signal server stopped by user")


if __name__ == "__main__":
    main()

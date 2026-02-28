"""
Рабочий локальный Modbus TCP simulator, на котором можно:

- поднять ModbusTcpServer
- остановить его
- записать input registers
- записать holding registers
"""

import argparse
import asyncio
import logging
from contextlib import suppress

from pymodbus.datastore import (
    ModbusDeviceContext,
    ModbusSequentialDataBlock,
    ModbusServerContext,
)
from pymodbus.server import ModbusTcpServer

from pstg.simulator.config import (
    RegisterBlockConfig,
    SimulatorConfig,
    load_simulator_config,
)

logger = logging.getLogger(__name__)


def init_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def build_server_context(config: SimulatorConfig) -> ModbusServerContext:
    di = ModbusSequentialDataBlock(0, [False] * 1000)
    co = ModbusSequentialDataBlock(0, [False] * 1000)
    ir = ModbusSequentialDataBlock(0, [0] * 1000)
    hr = ModbusSequentialDataBlock(0, [0] * 1000)

    device_context = ModbusDeviceContext(di=di, co=co, ir=ir, hr=hr)

    for block in config.input_registers or []:
        device_context.setValues(4, block.address, block.values)

    for block in config.holding_registers or []:
        device_context.setValues(3, block.address, block.values)

    return ModbusServerContext(
        devices={config.device_id: device_context}, single=False
    )


class DevModbusServer:
    def __init__(self, config: SimulatorConfig) -> None:
        self.config = config
        self.context = build_server_context(config)
        self.device_context = self.context[config.device_id]
        self.server = ModbusTcpServer(
            self.context,
            address=(config.host, config.port),
        )
        self._task: asyncio.Task | None = None
        self._update_tasks: list[asyncio.Task] = []

    async def start(self) -> None:
        logger.info(
            "Starting Modbus simulator on %s:%s device_id=%s",
            self.config.host,
            self.config.port,
            self.config.device_id,
        )
        self._task = asyncio.create_task(self.server.serve_forever())
        self._start_auto_updates()
        logger.info("Auto-update tasks started: %s", len(self._update_tasks))

    async def stop(self) -> None:
        logger.info("Stopping Modbus simulator")
        await self.server.shutdown()
        for task in self._update_tasks:
            task.cancel()
        for task in self._update_tasks:
            with suppress(asyncio.CancelledError):
                await task
        if self._task is not None:
            self._task.cancel()
            with suppress(asyncio.CancelledError):
                await self._task

    def _start_auto_updates(self) -> None:
        self._schedule_updates(4, self.config.input_registers or [])
        self._schedule_updates(3, self.config.holding_registers or [])

    def _schedule_updates(
        self,
        function_code: int,
        blocks: list[RegisterBlockConfig],
    ) -> None:
        for block in blocks:
            if block.interval_s is None:
                continue

            logger.info(
                "Auto-update enabled for fc%s address=%s interval_s=%s step=%s",
                function_code,
                block.address,
                block.interval_s,
                block.step,
            )
            task = asyncio.create_task(
                self._auto_update_block(function_code, block),
            )
            self._update_tasks.append(task)

    async def _auto_update_block(
        self,
        function_code: int,
        block: RegisterBlockConfig,
    ) -> None:
        assert block.interval_s is not None

        current_values = list(block.values)
        while True:
            await asyncio.sleep(block.interval_s)
            current_values = [value + block.step for value in current_values]
            self.device_context.setValues(
                function_code, block.address, current_values
            )
            logger.info(
                "Updated fc%s address=%s values=%s",
                function_code,
                block.address,
                current_values,
            )


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run development Modbus TCP server for PSTG",
    )
    parser.add_argument(
        "--config",
        help="Path to JSON config file. "
        + "If omitted, built-in defaults are used.",
    )
    parser.add_argument("--host", help="Override host from config")
    parser.add_argument("--port", type=int, help="Override port from config")
    parser.add_argument(
        "--device-id", type=int, help="Override device_id from config"
    )
    return parser


async def run_server(config: SimulatorConfig) -> None:
    server = DevModbusServer(config)
    await server.start()

    try:
        while True:
            await asyncio.sleep(3600)
    finally:
        await server.stop()


def main() -> None:
    init_logging()

    parser = build_argument_parser()
    args = parser.parse_args()

    config = load_simulator_config(args.config)
    if args.host:
        config.host = args.host
    if args.port is not None:
        config.port = args.port
    if args.device_id is not None:
        config.device_id = args.device_id

    logger.info("Input register blocks: %s", config.input_registers)
    logger.info("Holding register blocks: %s", config.holding_registers)

    try:
        asyncio.run(run_server(config))
    except KeyboardInterrupt:
        logger.info("Simulator stopped by user")


if __name__ == "__main__":
    main()

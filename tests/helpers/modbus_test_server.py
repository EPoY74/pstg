"""
Что умеет:
- поднять реальный ModbusTcpServer
- остановить его
- записать input registers
- записать holding registers
Returns:
    _type_: _description_
"""

import asyncio
import socket
from contextlib import suppress

from pymodbus.datastore import (
    ModbusDeviceContext,
    ModbusSequentialDataBlock,
    ModbusServerContext,
)
from pymodbus.server import ModbusTcpServer


def _get_free_port() -> int:
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


class ModbusTestServer:
    def __init__(self, host: str = "127.0.0.1", device_id: int = 1) -> None:
        self.host = host
        self.port = _get_free_port()
        self.device_id = device_id

        di = ModbusSequentialDataBlock(0, [False] * 100)
        co = ModbusSequentialDataBlock(0, [False] * 100)
        ir = ModbusSequentialDataBlock(0, [0] * 100)
        hr = ModbusSequentialDataBlock(0, [0] * 100)

        self.device_context = ModbusDeviceContext(di=di, co=co, ir=ir, hr=hr)
        self.server_context = ModbusServerContext(
            devices={self.device_id: self.device_context},
            single=False,
        )

        self.server = ModbusTcpServer(
            self.server_context,
            address=(self.host, self.port),
        )
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        self._task = asyncio.create_task(self.server.serve_forever())
        await asyncio.sleep(0.05)

    async def stop(self) -> None:
        await self.server.shutdown()
        if self._task is not None:
            self._task.cancel()
            with suppress(asyncio.CancelledError):
                await self._task

    def set_input_registers(self, address: int, values: list[int]) -> None:
        self.device_context.setValues(4, address, values)

    def set_holding_registers(self, address: int, values: list[int]) -> None:
        self.device_context.setValues(3, address, values)

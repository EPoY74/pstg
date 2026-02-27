# tests/conftest.py
import asyncio
import socket
import pytest

from pymodbus.server import ModbusTcpServer
from tests.helpers.mock_modbus_server import build_context


def get_free_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


@pytest.fixture
async def modbus_server():
    context = build_context()
    port = get_free_port()

    server = ModbusTcpServer(context, address=("127.0.0.1", port))

    task = asyncio.create_task(server.serve_forever())

    # маленькая пауза, чтобы сервер успел подняться
    await asyncio.sleep(0.05)

    try:
        yield {"host": "127.0.0.1", "port": port, "context": context}
    finally:
        await server.shutdown()
        task.cancel()

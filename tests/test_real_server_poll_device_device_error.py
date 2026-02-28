import asyncio

from pstg.app.collector import poll_device
from pstg.domain.connection_state import ConnectionState
from pstg.domain.kind_state import KindState
from pstg.domain.modbus_device_read_settings import ModbusDeviceReadSettings
from pstg.drivers.open_connection_modbus_tcp import open_connection_modbus_tcp
from tests.helpers.modbus_test_server import ModbusTestServer


def test_poll_device_returns_up_when_server_replies_with_device_error() -> None:
    async def scenario() -> None:
        server = ModbusTestServer()
        await server.start()

        client = None
        try:
            client = await open_connection_modbus_tcp(server.host, server.port)
            result = await poll_device(
                client,
                ModbusDeviceReadSettings(
                    device_id=server.device_id,
                    offset=150,
                    read_count=2,
                ),
            )

            assert result.connection_state == ConnectionState.UP
            assert len(result.blocks) == 2
            assert result.blocks[0].ok is False
            assert result.blocks[0].current_error_info is not None
            assert result.blocks[0].current_error_info.kind == KindState.DEVICE
            assert result.blocks[1].ok is False
            assert result.blocks[1].current_error_info is not None
            assert result.blocks[1].current_error_info.kind == KindState.DEVICE
        finally:
            if client is not None:
                client.close()
            await server.stop()

    asyncio.run(scenario())

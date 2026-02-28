"""
Проверяет:
 - connection_state == UP
 - данные попадают в блок FC04
 - fallback не используется
"""

import asyncio

from pstg.app.collector import poll_device
from pstg.domain.connection_state import ConnectionState
from pstg.domain.modbus_device_read_settings import ModbusDeviceReadSettings
from pstg.drivers.open_connection_modbus_tcp import open_connection_modbus_tcp
from tests.helpers.modbus_test_server import ModbusTestServer


def test_poll_device_returns_up_for_successful_fc04_read() -> None:
    async def scenario() -> None:
        server = ModbusTestServer()
        server.set_input_registers(0, [1, 2, 3, 4])
        await server.start()

        client = None
        try:
            client = await open_connection_modbus_tcp(server.host, server.port)
            result = await poll_device(
                client,
                ModbusDeviceReadSettings(
                    device_id=server.device_id,
                    offset=0,
                    read_count=4,
                ),
            )

            assert result.connection_state == ConnectionState.UP
            assert len(result.blocks) == 2
            assert result.blocks[0].ok is True
            assert result.blocks[0].fc == 4
            assert result.blocks[0].registers == [1, 2, 3, 4]
            assert result.blocks[1].ok is None
        finally:
            if client is not None:
                client.close()
            await server.stop()

    asyncio.run(scenario())

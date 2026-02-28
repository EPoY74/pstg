import asyncio

from pstg.drivers.open_connection_modbus_tcp import open_connection_modbus_tcp
from pstg.drivers.read_fc04_input_regoster import read_fc04_input_register
from tests.helpers.modbus_test_server import ModbusTestServer


def test_read_fc04_from_real_modbus_server() -> None:
    async def scenario() -> None:
        server = ModbusTestServer()
        server.set_input_registers(0, [11, 22, 33])
        await server.start()

        client = None
        try:
            client = await open_connection_modbus_tcp(server.host, server.port)
            response = await read_fc04_input_register(
                client,
                offset=0,
                read_count=3,
                plc_id=server.device_id,
            )

            assert response is not None
            assert response.isError() is False
            assert response.registers == [11, 22, 33]
        finally:
            if client is not None:
                client.close()
            await server.stop()

    asyncio.run(scenario())

import asyncio

import pytest

from pstg.app.read_signal_config import get_signals_config
from pstg.domain.connection_state import ConnectionState
from pstg.domain.registers_modbus_device_settings import (
    RegistersModbusDeviceSettings,
)
from pstg.drivers.open_connection_modbus_tcp import open_connection_modbus_tcp
from pstg.drivers.read_registers_safely import read_registers_safely
from pstg.drivers.read_signals import read_signals
from tests.helpers.modbus_test_server import ModbusTestServer
from tests.helpers.signals_modbus_test_server import SignalsModbusTestServer


def test_read_signals_reads_fc03_signal_values() -> None:
    async def scenario() -> None:
        signals_config = get_signals_config()
        server = SignalsModbusTestServer()
        server.set_signal_values(
            {
                "PT1": 1.5,
                "PT2": 2.5,
                "PT3": 3.5,
                "FlowPerHour": 120.25,
                "FlowAmount": 456.75,
            }
        )
        await server.start()

        client = None
        try:
            client = await open_connection_modbus_tcp(server.host, server.port)
            result = await read_signals(
                3,
                client,
                RegistersModbusDeviceSettings(
                    device_id=server.device_id,
                    offset=0,
                    read_count=12,
                    fc=3,
                ),
                signals_config,
            )

            assert result["PT1"].value == pytest.approx(1.5)
            assert result["PT2"].value == pytest.approx(2.5)
            assert result["PT3"].value == pytest.approx(3.5)
            assert result["FlowPerHour"].value == pytest.approx(120.25)
            assert result["FlowAmount"].value == pytest.approx(456.75)
        finally:
            if client is not None:
                client.close()
            await server.stop()

    asyncio.run(scenario())


def test_read_registers_safely_reads_fc03_holding_registers() -> None:
    async def scenario() -> None:
        server = ModbusTestServer()
        server.set_holding_registers(10, [201, 202, 203])
        await server.start()

        client = None
        try:
            client = await open_connection_modbus_tcp(server.host, server.port)
            result = await read_registers_safely(
                client,
                RegistersModbusDeviceSettings(
                    device_id=server.device_id,
                    offset=10,
                    read_count=3,
                    fc=3,
                ),
            )

            assert result.connection_state == ConnectionState.UP
            assert len(result.blocks) == 1
            assert result.blocks[0].fc == 3
            assert result.blocks[0].ok is True
            assert result.blocks[0].registers == [201, 202, 203]
        finally:
            if client is not None:
                client.close()
            await server.stop()

    asyncio.run(scenario())


def test_read_registers_safely_reads_fc04_input_registers() -> None:
    async def scenario() -> None:
        server = ModbusTestServer()
        server.set_input_registers(20, [101, 102, 103])
        await server.start()

        client = None
        try:
            client = await open_connection_modbus_tcp(server.host, server.port)
            result = await read_registers_safely(
                client,
                RegistersModbusDeviceSettings(
                    device_id=server.device_id,
                    offset=20,
                    read_count=3,
                    fc=4,
                ),
            )

            assert result.connection_state == ConnectionState.UP
            assert len(result.blocks) == 1
            assert result.blocks[0].fc == 4
            assert result.blocks[0].ok is True
            assert result.blocks[0].registers == [101, 102, 103]
        finally:
            if client is not None:
                client.close()
            await server.stop()

    asyncio.run(scenario())

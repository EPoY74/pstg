# Проверяет текущую готовность pstg на уровне orchestration:
# после DOWN происходит reconnect и следующий результат уже UP.
import asyncio

from pstg.app import collector
from pstg.domain.connection_state import ConnectionState
from pstg.domain.modbus_config import ModbusConfig
from pstg.domain.modbus_device_read_settings import ModbusDeviceReadSettings
from pstg.domain.poll_result import PollResult


class DummyClient:
    def __init__(self, name: str) -> None:
        self.name = name
        self.closed = False

    def close(self) -> None:
        self.closed = True


def test_poll_forever_reconnects_after_down_result(monkeypatch) -> None:
    first_client = DummyClient("first")
    second_client = DummyClient("second")
    connect_calls: list[str] = []

    async def fake_open_connection(host: str, port: int):
        connect_calls.append(f"{host}:{port}")
        if len(connect_calls) == 1:
            return first_client
        return second_client

    async def fake_poll_device(device, settings):
        if device is first_client:
            return PollResult(connection_state=ConnectionState.DOWN)
        return PollResult(connection_state=ConnectionState.UP)

    async def fake_sleep(delay: float) -> None:
        return None

    async def fake_reconnect_break(reason: str) -> None:
        return None

    monkeypatch.setattr(
        collector, "open_connection_modbus_tcp", fake_open_connection
    )
    monkeypatch.setattr(collector, "poll_device", fake_poll_device)
    monkeypatch.setattr(collector.asyncio, "sleep", fake_sleep)
    monkeypatch.setattr(collector, "_reconnect_break", fake_reconnect_break)

    async def run_scenario() -> tuple[PollResult, PollResult]:
        generator = collector.poll_forever(
            ModbusConfig(host="127.0.0.1", port=502, poll_interval_s=0),
            ModbusDeviceReadSettings(device_id=1, offset=0, read_count=1),
        )

        first_result = await anext(generator)
        second_result = await anext(generator)
        await generator.aclose()
        return first_result, second_result

    first_result, second_result = asyncio.run(run_scenario())

    assert first_result.connection_state == ConnectionState.DOWN
    assert second_result.connection_state == ConnectionState.UP
    assert len(connect_calls) >= 2
    assert first_client.closed is True

import asyncio

from pstg.app import collector
from pstg.domain.connection_state import ConnectionState
from pstg.domain.error_info import ErrorInfo
from pstg.domain.kind_state import KindState
from pstg.domain.poll_result import PollResult
from pstg.domain.raw_block_result import RawBlockResult
from pstg.domain.registers_modbus_device_settings import (
    RegistersModbusDeviceSettings,
)


def test_poll_device_does_not_fallback_after_fc04_device_error(
    monkeypatch,
) -> None:
    call_order: list[int] = []

    async def fake_read_registers_safely(device, settings):
        call_order.append(settings.fc)
        return PollResult(
            connection_state=ConnectionState.UP,
            blocks=[
                RawBlockResult(
                    fc=4,
                    ok=False,
                    current_error_info=ErrorInfo(
                        message="fc04 device error",
                        kind=KindState.DEVICE,
                        exception_code=2,
                    ),
                )
            ],
        )

    monkeypatch.setattr(
        collector, "read_registers_safely", fake_read_registers_safely
    )

    result = asyncio.run(
        collector.poll_device(
            device_being_polled=object(),
            device_poll_settings=RegistersModbusDeviceSettings(
                device_id=1,
                offset=0,
                read_count=3,
                fc=4,
            ),
        )
    )

    assert call_order == [4]
    assert result.connection_state == ConnectionState.UP
    assert len(result.blocks) == 1
    assert result.blocks[0].fc == 4
    assert result.blocks[0].current_error_info is not None

from pymodbus import ModbusException
from pymodbus.client import AsyncModbusTcpClient
from pymodbus.pdu import ModbusPDU


async def read_fc03_holding_register(
    pstg_client: AsyncModbusTcpClient,
    *,
    offset: int,
    read_count: int,
    plc_id: int,
) -> ModbusPDU | None:
    """
    Читает данные из holding registers (FC04) ПЛК.
    Args:
        pstg_client (AsyncModbusTcpClient): оединение с сервером, от которого получаем данные
        offset (int): Смещение (адрес), откуда читаем
        read_count (int): Сколько читать от смещения (адреса)
        device_id (int): ID устройства, с которого считываем данные
    Raises:
        RuntimeError: FC04 returned None...
        RuntimeError: FC04 transport/library error...
    Returns:
        ModbusPDU | None: Возвращает прочитанные регистры
    """

    holding_regs: ModbusPDU | None = None
    try:
        holding_regs = await pstg_client.read_holding_registers(
            offset, count=read_count, device_id=plc_id
        )
        if holding_regs is None:
            raise RuntimeError(
                f"FC03 returned None: plc_id={plc_id} offset={offset} count={read_count}"
            )
    except ModbusException as err:
        raise RuntimeError(
            f"FC04 transport/library error: plc_id={plc_id} offset={offset} "
            f"count={read_count}: {err!r}"
        ) from err
    return holding_regs

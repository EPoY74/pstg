from pymodbus import ModbusException
from pymodbus.client import AsyncModbusTcpClient
from pymodbus.pdu import ModbusPDU


async def read_fc04_input_register(
    pstg_client: AsyncModbusTcpClient,
    *,
    offset: int,
    read_count: int,
    plc_id: int,
) -> ModbusPDU | None:
    """
    Читает данные из input registers (FC04) ПЛК.
    Args:
        pstg_client (AsyncModbusTcpClient): оединение с сервером, от которого получаем данные
        offset (int): Смещение (адрес), откуда читаем
        read_count (int): Сколько читать от смещения (адреса)
        device_id (int): ID устройства, с которого считываем данные
    Raises:
        RuntimeError: FC04 returned None...
        RuntimeError: FC04 device exception...
        RuntimeError: FC04 transport/library error...
    Returns:
        ModbusPDU | None: Возвращает прочитанные регистры
    """

    input_regs: ModbusPDU | None = None
    try:
        input_regs = await pstg_client.read_input_registers(
            offset, count=read_count, device_id=plc_id
        )
        if input_regs is None:
            raise RuntimeError(
                f"FC04 returned None: plc_id={plc_id} offset={offset} count={read_count}"
            )
        if (input_regs) and input_regs.isError():
            raise RuntimeError(
                f"FC04 device exception: plc_id={plc_id} offset={offset} "
                f"count={read_count}: {input_regs!r}"
            )
    except ModbusException as err:
        raise RuntimeError(
            f"FC04 transport/library error: plc_id={plc_id} offset={offset} "
            f"count={read_count}: {err!r}"
        ) from err
    return input_regs

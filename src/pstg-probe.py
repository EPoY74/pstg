import asyncio
import logging

from pymodbus import ModbusException
from pymodbus.client import AsyncModbusTcpClient
from pymodbus.pdu import ModbusPDU

logger = logging.getLogger(__name__)


async def open_connection_modbus_tcp(
    ip_host: str, ip_port: int = 502
) -> AsyncModbusTcpClient:
    """Создает соединение с TCP Modbus контроллером
    Args:
        ip_host (str): IP адрес устройства или хоста, за которым устройство
        ip_port (int, optional): Номер порта, который работает с modbus. Defaults to 502.
    Raises:
        ConnectionError: Ошибка подключения к modbus серверу (общая)
        ConnectionError: Ошибка подключения к modbus серверу (генерируется клиентом)
    Returns:
        AsyncModbusTcpClient: Соединение с сервером, от которого получаем данные
    """

    logger.info("Open Connection")
    pstg_client = AsyncModbusTcpClient(host=ip_host, port=ip_port)

    try:
        is_ok: bool = await pstg_client.connect()
    except Exception as err:
        logger.error("Failed to connect to Modbus server (%s)", err)
        raise ConnectionError("Failed to connect to Modbus server") from err
    if not is_ok or not pstg_client.connected:
        logger.error("Client is not connected")
        raise ConnectionError("Client is not connected")
    logger.info("Connection is opened!")
    return pstg_client


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
        RuntimeError: FC04 device exception...
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
        if (holding_regs) and holding_regs.isError():
            raise RuntimeError(
                f"FC03 device exception: plc_id={plc_id} offset={offset} "
                f"count={read_count}: {holding_regs!r}"
            )
    except ModbusException as err:
        raise RuntimeError(
            f"FC04 transport/library error: plc_id={plc_id} offset={offset} "
            f"count={read_count}: {err!r}"
        ) from err
    return holding_regs


async def main() -> None:

    holding_regs: ModbusPDU | None = None
    input_regs: ModbusPDU | None = None
    is_read_ok: bool = True

    pstg_client = await open_connection_modbus_tcp(
        ip_host="10.0.6.10", ip_port=506
    )

    try:
        logger.info("Reading input registers (FC04)")
        input_regs = await read_fc04_input_register(
            pstg_client, offset=0, read_count=1, plc_id=1
        )
        logger.info("Registers (FC04) have been read!")
    except RuntimeError as err:
        is_read_ok = False
        logger.warning("Read failed: %s", err)
        # raise RuntimeError("FC04 read failed in poll:") from err

    if not is_read_ok:
        try:
            holding_regs = await read_fc03_holding_register(
                pstg_client, offset=0, read_count=1, plc_id=1
            )
        except RuntimeError as err:
            raise RuntimeError("FC03 read failed in poll:") from err

    if input_regs and (not input_regs.isError()):
        value_int16_input = input_regs.registers[0]
        bits_inp = f"{value_int16_input:016b}"
        logger.info(
            "Got input registers (FC04) int16: %s (%s)",
            value_int16_input,
            bits_inp,
        )

    if not is_read_ok:
        if holding_regs and (not holding_regs.isError()):
            value_int16_holding = holding_regs.registers[0]
            bits_hold = f"{value_int16_holding:016b}"
            logger.info(
                "Got holding registers (FC03) int16: %s (%s)",
                value_int16_holding,
                bits_hold,
            )
        is_read_ok = True
    logger.info("Close connection")


if __name__ == "__main__":
    # ✅ Настройка логов только при запуске как скрипт
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    logger.info("Start Pump Station Telemetry Gateway")
    asyncio.run(main(), debug=True)
    logger.info("Stop Pump Station Telemetry Gateway")

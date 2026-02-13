from pymodbus.client import AsyncModbusTcpClient


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

    # logger.info("Open Connection")
    pstg_client = AsyncModbusTcpClient(host=ip_host, port=ip_port)

    try:
        is_ok: bool = await pstg_client.connect()
    except Exception as err:
        # logger.error("Failed to connect to Modbus server (%s)", err)
        raise ConnectionError("Failed to connect to Modbus server") from err
    if not is_ok or not pstg_client.connected:
        # logger.error("Client is not connected")
        raise ConnectionError("Client is not connected")
    # logger.info("Connection is opened!")
    return pstg_client

from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ConnectionException


async def open_connection_modbus_tcp(
    ip_host: str, ip_port: int = 502
) -> AsyncModbusTcpClient:
    """Создает соединение с TCP Modbus контроллером, автоматически переподключается.
    Args:
        ip_host (str): IP адрес устройства или хоста, за которым устройство
        ip_port (int, optional): Номер порта, который работает с modbus. Defaults to 502.
    Raises:
        ConnectionException: Failed to connect to Modbus server (modbus)
        ConnectionError: Ошибка подключения к modbus серверу (общая)
        ConnectionError: Ошибка подключения к modbus серверу (генерируется клиентом)
    Returns:
        AsyncModbusTcpClient: Соединение с сервером, от которого получаем данные
    """

    # logger.info("Open Connection")

    #  TODO Подумать и реализовать?  - самостоятельный контроль за
    # повторными подключениями. Оценить необходимость усложнения кода
    pstg_client = AsyncModbusTcpClient(
        host=ip_host, port=ip_port, reconnect_delay=1, reconnect_delay_max=60, timeout=3, retries=3)
    #  ConnectionException выкидивает,  time  - in seconds
    #  reconnect_delay автоматически удваивается при каждой неудачной попытке подключения
    #  — от значения reconnect_delay до reconnect_delay_max.
    try:
        is_ok: bool = await pstg_client.connect()

    except ConnectionException as err:
        raise ConnectionError(
            f"Failed to connect to Modbus server {ip_host}:{ip_port}") from err

    except Exception as err:
        # logger.error("Failed to connect to Modbus server (%s)", err)
        raise ConnectionError("Failed to connect to Modbus server") from err
    if not is_ok or not pstg_client.connected:
        # logger.error("Client is not connected")
        raise ConnectionError("Client is not connected")
    # logger.info("Connection is opened!")
    return pstg_client

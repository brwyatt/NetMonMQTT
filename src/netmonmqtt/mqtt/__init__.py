import machineid
from paho.mqtt.client import Client
from paho.mqtt.client import CallbackAPIVersion


def on_connect(client, userdata, flags, rc, properties):
    if rc == 0:
        print("Connected!")
    else:
        print(f"Connection failed! Code: {rc}")


def on_disconnect(cleint, userdata, flags, rc, properties):
    print(f"Disconnected! Code: {rc}")


def on_log(client, userdata, level, buf):
    print(f"LOG: [{level}]: {buf}")


def connect(
    host: str,
    port: int,
    username: str,
    password: str,
    secure: bool = False,
    async_connect: bool = False,
):
    client = Client(
        client_id=f"NetMon-{machineid.id()}",
        callback_api_version=CallbackAPIVersion.VERSION2,
        clean_session=True,
    )
    client.username_pw_set(username, password)
    if secure:
        client.tls_set()

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_log = on_log


    if async_connect:
        client.connect_async(host, port)
    else:
        client.connect(host, port)

    return client
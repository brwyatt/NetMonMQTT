from random import randint
from time import sleep
from typing import Any, Callable, Dict, List, NamedTuple, Optional, Union
import machineid
from paho.mqtt.client import Client
from paho.mqtt.client import CallbackAPIVersion


class Action(NamedTuple):
    action: Callable
    args: List[Any]
    kwargs: Dict[str, Any]


def call_actions(client: Client, action_class: str):
    for action in client.extra_actions.get(action_class, []):
        action.action(*action.args, **action.kwargs)


def on_connect(client, userdata, flags, rc, properties):
    if rc == 0:
        print("Connected!")
        call_actions(client, "connect")
    else:
        print(f"Connection failed! Code: {rc}")


def on_disconnect(client, userdata, flags, rc, properties):
    print(f"Disconnected! Code: {rc}")
    call_actions(client, "disconnect")


def on_log(client, userdata, level, buf):
    print(f"MQTT: [{level}]: {buf}")


class HAMQTTClient(Client):
    extra_actions: Dict[str, List[Action]] = {}

    @property
    def availability_topic(self):
        return f"netmon/{self._client_id}/availability"

    def add_connect_action(self, action: Union[Callable, Action]):
        action = action if action is Action else Action(action, [], {})
        self.extra_actions["connect"].append(action)

        if self.is_connected():
            action.action(*action.args, **action.kwargs)

    def add_disconnect_action(self, action: Union[Callable, Action]):
        action = action if action is Action else Action(action, [], {})
        self.extra_actions["disconnect"].append(action)

        if not self.is_connected():
            action.action(*action.args, **action.kwargs)


def connect(
    host: str,
    port: int,
    username: str,
    password: str,
    secure: bool = False,
    async_connect: bool = False,
    client_id: Optional[str] = None,
    connect_actions: Optional[Union[Callable, Action]] = None,
    disconnect_actions: Optional[Union[Callable, Action]] = None,
):
    if client_id is None:
        client_id = f"NetMon-{machineid.id()}"

    client = HAMQTTClient(
        client_id=client_id,
        callback_api_version=CallbackAPIVersion.VERSION2,
        clean_session=True,
    )
    client.username_pw_set(username, password)
    if secure:
        client.tls_set()

    client.extra_actions = {
        "connect": [x if x is Action else Action(x, [], {}) for x in connect_actions] if connect_actions else [],
        "disconnect": [x if x is Action else Action(x, [], {}) for x in disconnect_actions] if disconnect_actions else []
    }

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_log = on_log

    client.keepalive = 15

    client.will_set(client.availability_topic, "offline", retain=False)

    if async_connect:
        client.connect_async(host, port)
    else:
        client.connect(host, port)

    return client
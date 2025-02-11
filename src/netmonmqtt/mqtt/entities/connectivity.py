from typing import TYPE_CHECKING
from netmonmqtt.mqtt.entity import Entity

if TYPE_CHECKING:
    from netmonmqtt.mqtt.device import MQTTDevice


class ConnectivityEntity(Entity):
    def __init__(
        self,
        parent: "MQTTDevice",
        name: str,
        unique_id: str,
        expire: int = 60,
    ):
        super().__init__(
            parent,
            name,
            unique_id,
            "binary_sensor",
            device_class="connectivity",
            expire=expire,
        )

from typing import TYPE_CHECKING, Optional
from netmonmqtt.mqtt.entity import Entity

if TYPE_CHECKING:
    from netmonmqtt.mqtt.device import MQTTDevice


class IPAddressEntity(Entity):
    def __init__(
        self,
        parent: "MQTTDevice",
        name: str,
        unique_id: str,
        state_topic: Optional[str] = None,
        value_template: Optional[str] = None,
        expire: int = 60,
        via_device: Optional["MQTTDevice"] = None,
    ):
        super().__init__(
            parent,
            name,
            unique_id,
            "sensor",
            device_class=None,
            state_class=None,
            unit_of_measurement=None,
            state_topic=state_topic,
            value_template=value_template,
            expire=expire,
            via_device=via_device,
        )

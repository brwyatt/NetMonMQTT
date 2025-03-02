from typing import TYPE_CHECKING, Optional
from netmonmqtt.mqtt.entity import Entity

if TYPE_CHECKING:
    from netmonmqtt.mqtt.device import MQTTDevice


class LatencyEntity(Entity):
    def __init__(
        self,
        parent: "MQTTDevice",
        name: str,
        unique_id: str,
        unit_of_measurement: str = "ms",
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
            device_class="duration",
            state_class="measurement",
            unit_of_measurement=unit_of_measurement,
            state_topic=state_topic,
            value_template=value_template,
            expire=expire,
            via_device=via_device,
        )

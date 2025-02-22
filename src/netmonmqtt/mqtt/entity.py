from importlib.metadata import metadata
import json
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from netmonmqtt.mqtt.device import MQTTDevice


origin_data = metadata("NetMonMQTT")


class Entity():
    def __init__(
        self,
        parent: "MQTTDevice",
        name: str,
        entity_id: str,
        platform: str,
        device_class: Optional[str] = None,
        unit_of_measurement: Optional[str] = None,
        expire: int = 60,
        command_callback: Optional[callable]= None,
    ):
        self.parent = parent
        self.name = name
        self.platform = platform
        self.entity_id = entity_id
        self.device_class = device_class
        self.unit_of_measurement = unit_of_measurement
        self.expire = expire
        self.command_callback = command_callback
        if self.command_callback:
            parent.register_listener(self.command_topic, self.command_callback)

    def send_discovery(self):
        self.parent.client.publish(self.discovery_topic, json.dumps(self.full_discovery_payload), retain=False)

    @property
    def unique_id(self):
        return f"{self.parent.device_id}_{self.entity_id}"

    @property
    def state_topic(self):
        return f"netmon/{self.parent.device_id}/{self.entity_id}/state"

    @property
    def command_topic(self):
        return f"netmon/{self.parent.device_id}/{self.entity_id}/command"

    @property
    def discovery_topic(self):
        return f"homeassistant/{self.platform}/{self.parent.device_id}/{self.entity_id}/config"

    @property
    def full_discovery_payload(self):
        return {
            "device": self.parent.device_discovery_payload,
            "origin": {
                "name": "NetMonMQTT",
                "sw_version": origin_data.get("Version", "unknown"),
                "url": {
                    x[0]: x[1]
                    for x in [
                        x.split(", ")
                        for x in origin_data.get_all("Project-Url", [])
                    ]
                }.get("Homepage"),
            },
            **self.entity_discovery_payload,
        }

    @property
    def entity_discovery_payload(self):
        return {
            "name": self.name,
            "platform": self.platform,
            **({"device_class": self.device_class,} if self.device_class else {}),
            **({"unit_of_measurement": self.unit_of_measurement,} if self.unit_of_measurement else {}),
            "state_topic": self.state_topic,
            **({"command_topic": self.command_topic,} if self.command_callback else {}),
            "entity_id": self.entity_id,
            "unique_id": self.unique_id,
            "expire_after": self.expire,
        }

    def publish_state(self, state):
        if type(state) is bool:
            state = "ON" if state else "OFF"
        self.parent.client.publish(self.state_topic, state, retain=False)
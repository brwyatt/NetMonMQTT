from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from netmonmqtt.mqtt.device import MQTTDevice


class Entity():
    def __init__(self, parent: "MQTTDevice", name: str, platform: str, unique_id: str, command_callback: Optional[callable]= None):
        self.parent = parent
        self.name = name
        self.platform = platform
        self.unique_id = unique_id
        self.command_callback = command_callback
        if self.command_callback:
            parent.register_listener(self.command_topic, self.command_callback)

    @property
    def entity_id(self):
        return self.unique_id

    @property
    def state_topic(self):
        return f"netmon/{self.parent.device_id}/{self.entity_id}/state"

    @property
    def command_topic(self):
        return f"netmon/{self.parent.device_id}/{self.entity_id}/command"

    @property
    def entity_discovery_payload(self):
        return {
            "name": self.name,
            "platform": self.platform,
            "state_topic": self.state_topic,
            **({"command_topic": self.command_topic,} if self.command_callback else {}),
            "unique_id": self.unique_id,
        }

    def publish_state(self, state):
        self.parent.client.publish(self.state_topic, state, retain=False)
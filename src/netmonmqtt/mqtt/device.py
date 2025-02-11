import json
from importlib.metadata import metadata
from typing import List, Optional
from paho.mqtt.client import Client as MQTTClient

from netmonmqtt.mqtt.entity import Entity


origin_data = metadata("NetMonMQTT")


class MQTTDevice():
    def __init__(
        self,
        client: MQTTClient,
        device_id: str,
        name: str,
        model: Optional[str] = None,
        manufacturer: Optional[str] = None,
        sw_version: Optional[str] = None
    ):
        self.client = client
        self.device_id = device_id
        self.name = name
        self.model = model
        self.manufacturer = manufacturer
        self.sw_version = sw_version

        self.entities: List[Entity] = []

    def register(self):
        topic = f"homeassistant/device/{self.device_id}/config"
        self.client.publish(topic, json.dumps(self.full_discovery_payload), retain=False)

    @property
    def full_discovery_payload(self):
        return {
            "device": self.device_discovery_payload,
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
            "components": {
                x.entity_id: x.entity_discovery_payload
                for x in self.entities
            },
        }

    @property
    def device_discovery_payload(self):
        return {
            "identifiers": [self.device_id],
            "name": self.name,
            **({"model": self.model,} if self.model else {}),
            **({"manufacturer": self.manufacturer,} if self.manufacturer else {}),
            **({"sw_version": self.sw_version,} if self.sw_version else {}),
        }

    def register_listener(self, topic, callback):
        self.client.subscribe(topic)
        self.client.message_callback_add(topic, callback)

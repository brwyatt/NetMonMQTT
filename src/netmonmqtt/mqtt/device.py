import json
from paho.mqtt.client import Client as MQTTClient


class MQTTDevice():
    def __init__(self, client: MQTTClient, device_id: str, name: str, model: str, manufacturer: str):
        self.client = client
        self.device_id = device_id
        self.name = name
        self.model = model
        self.manufacturer = manufacturer
        self.entities = []

    def register(self):
        topic = f"homeassistant/device/{self.device_id}/config"
        self.client.publish(topic, json.dumps(self.full_discovery_payload), retain=False)

    @property
    def full_discovery_payload(self):
        return {
            "device": self.device_discovery_payload,
            "origin": {
                "name": "NetMonMQTT",
            },
            "components": { x.entity_id: x.entity_discovery_payload for x in self.entities },
        }

    @property
    def device_discovery_payload(self):
        return {
            "identifiers": [self.device_id],
            "name": self.name,
            "model": self.model,
            "manufacturer": self.manufacturer,
        }

    def register_listener(self, topic, callback):
        self.client.subscribe(topic)
        self.client.message_callback_add(topic, callback)

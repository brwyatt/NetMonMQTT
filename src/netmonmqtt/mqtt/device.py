import json
from paho.mqtt.client import Client as MQTTClient


class MQTTDevice():
    def __init__(self, client: MQTTClient, device_id: str, name: str, model: str, manufacturer: str):
        self.client = client
        self.device_id = device_id
        self.name = name
        self.model = model
        self.manufacturer = manufacturer

    def _publish_discovery(self, component, payload):
        topic = f"homeassistant/{component}/{self.device_id}/{payload['unique_id']}/config"
        self.client.publish(topic, json.dumps(payload), retain=True)

    def register_listener(self, topic, callback):
        self.client.subscribe(topic)
        self.client.message_callback_add(topic, callback)

import json
from importlib.metadata import metadata
from random import randint
from time import sleep
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
        sw_version: Optional[str] = None,
    ):
        self.client = client
        self.device_id = device_id
        self.name = name
        self.model = model
        self.manufacturer = manufacturer
        self.sw_version = sw_version

        self.entities: List[Entity] = []

    def send_discovery(self):
        self.client.publish(self.discovery_topic, json.dumps(self.full_discovery_payload), retain=False)
        self.client.publish(self.availability_topic, "online", retain=False)

    def register(self):
        self.send_discovery()
        self.register_listener("homeassistant/status", self._handle_homeassistant_status)

    @property
    def discovery_topic(self):
        return f"homeassistant/device/{self.device_id}/config"

    @property
    def availability_topic(self):
        return f"netmon/{self.device_id}/availability"

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
            "availability": {
                "topic": self.availability_topic,
                "payload_available": "online",
                "payload_not_available": "offline"
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

    def _handle_homeassistant_status(self, client, userdata, msg):
        if msg.payload.decode() == "online":
            print("Home Assistant has come Online")
            sleep(float(randint(0,1000))/1000)
            self.send_discovery()
        else:
            print("Home Assistant has gone Offline")


    def register_listener(self, topic, callback):
        self.client.subscribe(topic)
        self.client.message_callback_add(topic, callback)

import json
from importlib.metadata import metadata
from random import randint
from time import sleep
from typing import List, Optional, Set
from paho.mqtt.client import Client as MQTTClient

from netmonmqtt.mqtt.check import Check
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

        self.entities: Set[Entity] = set()
        self.checks: Set[Check] = set()

    def send_discovery(self):
        self.client.publish(self.discovery_topic, json.dumps(self.full_discovery_payload), retain=False)
        self.client.publish(self.availability_topic, "online", retain=False)

    def register(self):
        self.send_discovery()
        self.register_listener("homeassistant/status", self._handle_homeassistant_status)
        for entity in self.all_entities:
            if entity.command_callback:
                self.register_listener(entity.command_topic, entity.command_callback)

    @property
    def discovery_topic(self):
        return f"homeassistant/device/{self.device_id}/config"

    @property
    def availability_topic(self):
        return f"netmon/{self.device_id}/availability"

    @property
    def all_entities(self):
        return self.entities.union({x for check in self.checks for x in check.entities})

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
                for x in self.all_entities
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

    def on_connect(self):
        if self.client.is_connected():
            self.register()
            for check in self.checks:
                check.start()


    def on_disconnect(self):
        for check in self.checks:
            check.stop()

    def _handle_homeassistant_status(self, client, userdata, msg):
        if msg.payload.decode() == "online":
            print("Home Assistant has come Online")
            sleep(float(randint(0,1000))/1000)
            self.send_discovery()
        else:
            print("Home Assistant has gone Offline")


    def register_listener(self, topic, callback):
        if not self.client.is_connected():
            return
        self.client.subscribe(topic)
        self.client.message_callback_add(topic, callback)

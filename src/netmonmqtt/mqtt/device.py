import json
from importlib.metadata import metadata
from random import randint
from time import sleep
from typing import List, Optional, Set
from paho.mqtt.client import Client as MQTTClient

from netmonmqtt.mqtt import HAMQTTClient
from netmonmqtt.mqtt.check import Check
from netmonmqtt.mqtt.entity import Entity


origin_data = metadata("NetMonMQTT")


class MQTTDevice():
    def __init__(
        self,
        client: HAMQTTClient,
        device_id: str,
        name: str,
        model: Optional[str] = None,
        manufacturer: Optional[str] = None,
        sw_version: Optional[str] = None,
        set_availability: bool = True,
        availability_topic: Optional[str] = None,
        via_device: Optional["MQTTDevice"] = None,
    ):
        self.client = client
        self.device_id = device_id
        self.name = name
        self.model = model
        self.manufacturer = manufacturer
        self.sw_version = sw_version
        self.set_availability = set_availability
        self._availability_topic = availability_topic
        self.via_device = via_device

        self.entities: Set[Entity] = set()
        self.checks: Set[Check] = set()
        self.independant_entities: Set[Check] = set()
        self.independant_checks: Set[Check] = set()

    def send_discovery(self):
        self.client.publish(self.discovery_topic, json.dumps(self.full_discovery_payload), retain=False)
        for entity in self.all_independant_entities:
            entity.send_discovery()

    def register(self):
        self.send_discovery()
        for entity in self.all_entities:
            if entity.command_callback:
                self.register_listener(entity.command_topic, entity.command_callback)

    @property
    def discovery_topic(self):
        return f"homeassistant/device/{self.device_id}/config"

    @property
    def availability_topic(self):
        if self._availability_topic is not None:
            return self._availability_topic
        return f"netmon/{self.device_id}/availability"

    @property
    def all_independant_entities(self):
        return self.independant_entities.union({x for check in self.independant_checks for x in check.entities})

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
            **({
                "availability": {
                    "topic": self.availability_topic,
                    "payload_available": "online",
                    "payload_not_available": "offline"
                }
            } if self.set_availability else {}),
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
            **({"via_device": self.via_device.device_id,} if self.via_device else {}),
        }

    def on_connect(self):
        if self.client.is_connected():
            self.register()
            for check in self.checks.union(self.independant_checks):
                check.start()


    def on_disconnect(self):
        for check in self.checks.union(self.independant_checks):
            check.stop()

    def register_listener(self, topic, callback):
        if not self.client.is_connected():
            return
        self.client.subscribe(topic)
        self.client.message_callback_add(topic, callback)

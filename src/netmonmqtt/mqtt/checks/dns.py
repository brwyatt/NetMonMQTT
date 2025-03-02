import json
from typing import Any, Dict, List, Optional
from netmonmqtt.checks.dns import check_dns
from netmonmqtt.mqtt.check import Check
from netmonmqtt.mqtt.device import MQTTDevice
from netmonmqtt.mqtt.entities.connectivity import ConnectivityEntity
from netmonmqtt.mqtt.entities.latency import LatencyEntity


class DNSCheck(Check):
    def __init__(
        self,
        parent: MQTTDevice,
        name: str,
        check_args: List[Any],
        check_kwargs: Dict[str, Any],
        state_topic: Optional[str] = None,
        expire: Optional[int] = None,
        interval: int = 60,
        jitter: float = 0.5,
    ):
        self.parent = parent
        self.name = f"{name} DNS"
        self.entity_id = self.name.lower().replace(" ", "_")
        self._state_topic = state_topic
        expire = expire if expire is not None else ((interval + jitter) * 2)
        entities = (
            ConnectivityEntity(
                parent,
                f"{self.name} Resolution",
                f"{self.entity_id}_resolution",
                state_topic=self.state_topic,
                value_template="{{ value_json.resolvable }}",
                expire=expire,
                via_device=parent.via_device,
            ),
            LatencyEntity(
                parent,
                f"{self.name} Lookup Latency",
                f"{self.entity_id}_latency",
                state_topic=self.state_topic,
                value_template="{{ value_json.latency }}",
                expire=expire,
                via_device=parent.via_device
            ),
        )
        super().__init__(check_dns, check_args, check_kwargs, entities, interval, jitter)

    @property
    def state_topic(self):
        if self._state_topic is not None:
            return self._state_topic
        return f"netmon/{self.parent.device_id}/{self.entity_id}/state"


    def run_check(self):
        results = self.check(*self.check_args, **self.check_kwargs)

        self.parent.client.publish(
            self.state_topic,
            json.dumps({
                "resolvable": "ON" if results[0] else "OFF",
                "latency": results[1],
            }),
            retain=False,
        )

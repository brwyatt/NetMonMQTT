import json
from typing import Any, Dict, List, Optional
from netmonmqtt.checks.route import check_route
from netmonmqtt.mqtt.check import Check
from netmonmqtt.mqtt.device import MQTTDevice
from netmonmqtt.mqtt.entities.connectivity import ConnectivityEntity
from netmonmqtt.mqtt.entities.ip_address import IPAddressEntity


class RouteCheck(Check):
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
        self.name = name
        self.entity_id = self.name.lower().replace(" ", "_")
        self._state_topic = state_topic
        expire = expire if expire is not None else ((interval + jitter) * 2)
        entities = (
            ConnectivityEntity(
                parent,
                f"{self.name} Expected Route",
                f"{self.entity_id}_expected_route",
                state_topic=self.state_topic,
                value_template="{{ value_json.expected }}",
                expire=expire,
                via_device=parent.via_device,
            ),
            ConnectivityEntity(
                parent,
                f"{self.name} Direct Response",
                f"{self.entity_id}_direct_response",
                state_topic=self.state_topic,
                value_template="{{ value_json.direct }}",
                expire=expire,
                via_device=parent.via_device,
            ),
            IPAddressEntity(
                parent,
                f"{self.name} Response IP",
                f"{self.entity_id}_response_ip",
                state_topic=self.state_topic,
                value_template="{{ value_json.ip }}",
                expire=expire,
                via_device=parent.via_device,
            ),
        )
        super().__init__(check_route, check_args, check_kwargs, entities, interval, jitter)

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
                "expected": "ON" if results[0] else "OFF",
                "direct": "ON" if results[1] else "OFF",
                "ip": results[2],
            }),
            retain=False,
            qos=1,
        )

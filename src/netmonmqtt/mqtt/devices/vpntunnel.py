from typing import Optional
from netmonmqtt.mqtt import HAMQTTClient
from netmonmqtt.mqtt.device import MQTTDevice


class VPNTunnel(MQTTDevice):
    def __init__(
        self,
        client: HAMQTTClient,
        tunnel_name: str,
        via_device: Optional["MQTTDevice"] = None,
    ):
        device_id = f"NetMon_{tunnel_name}".replace(" ", "_").replace("/", "_")

        super().__init__(
            client,
            device_id,
            f"S2S Tunnel {tunnel_name}",
            model="Site-to-Site VPN",
            set_availability=False,
            via_device=via_device,
        )
        self.tunnel_name = tunnel_name

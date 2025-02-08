import subprocess
import sys
from netmonmqtt.mqtt.device import MQTTDevice


class NetMon(MQTTDevice):
    def __init__(self, client, site_name):
        with  open("/etc/machine-id", "r") as f:
            machine_id = f.read().strip()
        device_id = f"NetMon_{site_name}_{machine_id}"

        super().__init__(client, device_id, f"{site_name} NetMon ({machine_id})", "NetMon", "brwyattt")
        self.site_name = site_name

    def register(self):
        button_payload = {
            "name": f"{self.name} Reinstall",
            "state_topic": f"netmon/{self.device_id}/reinstall/state",
            "command_topic": f"netmon/{self.device_id}/reinstall/set",
            "unique_id": f"{self.device_id}_reinstall",
            "device": self._get_device_info(),
        }
        self._publish_discovery("button", button_payload)
        self.register_listener(button_payload["command_topic"], self._handle_reinstall_command)

    def _get_device_info(self):
        return {
            "identifiers": [self.device_id],
            "name": self.name,
            "model": self.model,
            "manufacturer": self.manufacturer,
        }

    def _handle_reinstall_command(self, client, userdata, msg):
        if msg.payload.decode() == "ON":
            try:
                subprocess.run(
                    [
                        sys.executable,
                        "-m", "pip", "install",
                        "--upgrade",
                        "--force-reinstall",
                        "git+https://github.com/brwyatt/NetMonMQTT",
                    ],
                    check=True,
                )

                # Reset
                client.publish(f"netmon/{self.device_id}/reinstall/state", "OFF")

                # Might do something different, but if running as a Systemd service, this should trigger a restart
                exit(0)
            except Exception as e:
                print(f"Error reinstalling: {e}")
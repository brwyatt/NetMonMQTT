import subprocess
import sys
from netmonmqtt.mqtt.device import MQTTDevice
from netmonmqtt.mqtt.entity import Entity


class NetMon(MQTTDevice):
    def __init__(self, client, site_name):
        with  open("/etc/machine-id", "r") as f:
            machine_id = f.read().strip()
        device_id = f"NetMon_{machine_id}".replace(" ", "_")

        super().__init__(client, device_id, f"{site_name} NetMon ({machine_id})", "NetMon", "brwyattt")
        self.site_name = site_name

        self.entities.append(
            Entity(self, "Reinstall NetMon", "button", f"{self.device_id}_reinstall", self._handle_reinstall_command)
        )

    def _handle_reinstall_command(self, client, userdata, msg):
        if msg.payload.decode() == "PRESS":
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

                # Might do something different, but if running as a Systemd service, this should trigger a restart
                exit(0)
            except Exception as e:
                print(f"Error reinstalling: {e}")
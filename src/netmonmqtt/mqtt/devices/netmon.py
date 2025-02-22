import os
from typing import Optional
import machineid
import platform
import subprocess
import sys

from netmonmqtt.mqtt import HAMQTTClient
from netmonmqtt.mqtt.device import MQTTDevice
from netmonmqtt.mqtt.entity import Entity


class NetMon(MQTTDevice):
    def __init__(
        self,
        client: HAMQTTClient,
        site_name: str,
        availability_topic: Optional[str] = None,
    ):
        machine_id = machineid.id()
        device_id = f"NetMon_{machine_id}"

        super().__init__(
            client,
            device_id,
            f"{site_name} NetMon ({machine_id})",
            model=platform.system(),
            sw_version=platform.release(),
            availability_topic=availability_topic,
        )
        self.site_name = site_name

        self.entities.add(
            Entity(
                self,
                "Reinstall NetMon",
                f"{self.device_id}_reinstall",
                "button",
                command_callback=self._handle_reinstall_command,
            )
        )
        self.entities.add(
            Entity(
                self,
                "Restart NetMon",
                f"{self.device_id}_restart",
                "button",
                command_callback=self._handle_restart_command,
            )
        )

    def restart(self):
        print("Restarting!")
        self.client.disconnect()
        os.execv(sys.executable, [sys.executable] + sys.argv)
        exit(0)

    def _handle_restart_command(self, client, userdata, msg):
        if msg.payload.decode() == "PRESS":
            print("Received restart request from server")
            self.restart()

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

                self.restart()
            except Exception as e:
                print(f"Error reinstalling: {e}")


import sys
import threading
from typing import List, Optional

from netmonmqtt.checks.dns import check_dns
from netmonmqtt.checks.ping import check_ping
from netmonmqtt.config import Config
from netmonmqtt.mqtt import connect
from netmonmqtt.mqtt.check import Check
from netmonmqtt.mqtt.devices.netmon import NetMon
from netmonmqtt.mqtt.entities.connectivity import ConnectivityEntity
from netmonmqtt.mqtt.entities.latency import LatencyEntity


def get_check(check_type: str):
    if check_type == "dns":
        return check_dns
    if check_type == "ping":
        return check_ping
    raise ValueError(f"Invalid check type: {check_type}")


def get_check_entities(check_type: str, netmon: NetMon, name: str, expire: int):
    cleaned_name = name.lower().replace(" ", "_")
    if check_type in ["dns", "ping"]:
        return (
            ConnectivityEntity(netmon, f"{name} Connectivity", f"{cleaned_name}_connectivity", expire=expire),
            LatencyEntity(netmon, f"{name} Latency", f"{cleaned_name}_latency", expire=expire),
        )


def main(args: Optional[List[str]] = None):
    if args is None:
        args = sys.argv[1:]

    config = Config(file_name="./config.yaml")

    client = connect(
        config.connection.host,
        config.connection.port,
        config.connection.username,
        config.connection.password,
        secure=config.connection.secure,
        async_connect=True,
    )

    netmon = NetMon(
        client,
        config.site_name,
        availability_topic=client.availability_topic,
    )
    for site_check in config.site_checks:
        netmon.checks.add(Check(
            get_check(site_check.check_type),
            site_check.args,
            site_check.kwargs,
            get_check_entities(site_check.check_type, netmon, site_check.name, site_check.expire),
            interval=site_check.interval,
            jitter=site_check.jitter,
        ))

    client.add_connect_action(netmon.on_connect)
    client.add_disconnect_action(netmon.on_disconnect)

    try:
        client.loop_forever()
    except KeyboardInterrupt as ki:
        print("Got keboard interrupt!")
        client.disconnect()
        for thread in threading.enumerate():
            print(f"Waiting for thread stop: {thread.name}")
            try:
                thread.join()
            except RuntimeError as re:
                pass  # don't care!
        sys.exit(0)


if __name__ == "__main__":
    main()

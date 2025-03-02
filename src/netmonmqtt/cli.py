
import sys
import threading
from typing import List, Optional

from netmonmqtt.checks.dns import check_dns
from netmonmqtt.checks.ping import check_ping
from netmonmqtt.config import Config
from netmonmqtt.mqtt import connect
from netmonmqtt.mqtt.check import Check
from netmonmqtt.mqtt.checks.dns import DNSCheck
from netmonmqtt.mqtt.checks.ping import PingCheck
from netmonmqtt.mqtt.device import MQTTDevice
from netmonmqtt.mqtt.devices.netmon import NetMon
from netmonmqtt.mqtt.devices.vpntunnel import VPNTunnel
from netmonmqtt.mqtt.entities.connectivity import ConnectivityEntity
from netmonmqtt.mqtt.entities.latency import LatencyEntity


def get_check(check_type: str):
    if check_type == "dns":
        return DNSCheck
    if check_type == "ping":
        return PingCheck
    raise ValueError(f"Invalid check type: {check_type}")


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
        netmon.checks.add(
            get_check(site_check.check_type)(
                parent=netmon,
                name=site_check.name,
                check_args=site_check.args,
                check_kwargs=site_check.kwargs,
                expire=site_check.expire,
                interval=site_check.interval,
                jitter=site_check.jitter,
            )
        )

    client.add_connect_action(netmon.on_connect)
    client.add_disconnect_action(netmon.on_disconnect)

    for tunnel_config in config.tunnels:
        tunnel = VPNTunnel(
            client,
            tunnel_config.tunnel_id,
            via_device=netmon,
        )
        if tunnel_config.ping_check is not None:
            tunnel.independant_checks.add(PingCheck(
                parent=tunnel,
                name=tunnel_config.ping_check.name,
                check_args=tunnel_config.ping_check.args,
                check_kwargs=tunnel_config.ping_check.kwargs,
                expire=tunnel_config.ping_check.expire,
                interval=tunnel_config.ping_check.interval,
                jitter=tunnel_config.ping_check.jitter,
            ))
        if tunnel_config.dns_check is not None:
            tunnel.independant_checks.add(DNSCheck(
                parent=tunnel,
                name=tunnel_config.dns_check.name,
                check_args=tunnel_config.dns_check.args,
                check_kwargs=tunnel_config.dns_check.kwargs,
                expire=tunnel_config.dns_check.expire,
                interval=tunnel_config.dns_check.interval,
                jitter=tunnel_config.dns_check.jitter,
            ))

        client.add_connect_action(tunnel.on_connect)
        client.add_disconnect_action(tunnel.on_disconnect)

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

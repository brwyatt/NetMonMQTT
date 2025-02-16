
import sys
from typing import List, Optional

from netmonmqtt.checks.dns import check_dns
from netmonmqtt.config import Config
from netmonmqtt.mqtt import connect
from netmonmqtt.mqtt.check import Check
from netmonmqtt.mqtt.devices.netmon import NetMon
from netmonmqtt.mqtt.entities.connectivity import ConnectivityEntity
from netmonmqtt.mqtt.entities.latency import LatencyEntity


def main(args: Optional[List[str]] = None):
    if args is None:
        args = sys.argv[1:]

    conf = Config()

    client = connect(
        conf["host"],
        conf["port"],
        conf["username"],
        conf["password"],
        secure=True,
        async_connect=True,
    )

    netmon = NetMon(
        client,
        conf["site_name"],
    )
    dns_8dot = Check(
        check_dns,
        ["google.com", "8.8.8.8"],
        {"query_type": "A", "timeout": 2, "answer": None},
        (
            ConnectivityEntity(netmon, "8-dot Connectivity", "8_dot_connectivity"),
            LatencyEntity(netmon, "8-dot Latency", "8_dot_latency"),
        ),
        interval=10,
    )
    netmon.checks.add(dns_8dot)
    dns_1dot = Check(
        check_dns,
        ["google.com", "1.1.1.1"],
        {"query_type": "A", "timeout": 2, "answer": None},
        (
            ConnectivityEntity(netmon, "1-dot Connectivity", "1_dot_connectivity"),
            LatencyEntity(netmon, "1-dot Latency", "1_dot_latency"),
        ),
        interval=10,
    )
    netmon.checks.add(dns_1dot)

    client.add_connect_action(netmon.on_connect)
    client.add_disconnect_action(netmon.on_disconnect)

    client.loop_forever()


if __name__ == "__main__":
    main()

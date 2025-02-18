# MQTTNetworkMonitor
Monitor network connectivity stats and report to Home Assistant over MQTT

## Features
### Checks
* `ping`: Simple ICMP check against an endpoint, reports reachability and latency (requires sudo/root)
* `dns`: Does a DNS record lookup check against a server, reports success and latency
* `traceroute`: (WIP) Checks that a specified hop number is within a list of IPs (requires sudo/root)

### Site Checks
Checks related and assigned to the NetMon device will show up from the NetMon device directly in Home Assistant

### Tunnel Checks
Checks related to a Site-to-Site VPN and assigned to a VPN tunnel device in Home Assistant. Checks come from NetMons on both sides of the tunnel and report in to the same device in Home Assistant.

## Installation
Create the venv and install NetMonMQTT
```
sudo python3 -m venv /opt/NetMonMQTT
sudo /opt/NetMonMQTT/bin/pip install --upgrade --force-reinstall git+https://github.com/brwyatt/NetMonMQTT
```

Install the systemd unit file
```
curl -L https://github.com/brwyatt/NetMonMQTT/raw/refs/heads/main/netmon.service | sudo tee /etc/systemd/system/netmonmqtt.service > /dev/null
```

Edit the config file
```
sudo vim /opt/NetMonMQTT/config.yaml
```

Enable and start the service
```
sudo systemctl enable netmonmqtt.service
sudo systemctl start netmonmqtt.service
```

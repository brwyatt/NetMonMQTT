# MQTTNetworkMonitor
Monitor network connectivity stats and report over MQTT

## Install

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

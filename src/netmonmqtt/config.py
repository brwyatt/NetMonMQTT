from typing import Any, Dict, List, Optional
import yaml


class Config:
    def __init__(
        self,
        file_name: Optional[str] = None,
        site_name: Optional[str] = None,
        connection_details: Optional[Dict[str, str]] = None,
    ):
        file_data = {}
        if file_name:
            try:
                with open(file_name, "r") as file:
                    file_data = yaml.safe_load(file)
            except FileNotFoundError:
                pass

        if connection_details is None:
            connection_details = {}

        self.site_name = file_data.get("site_name", site_name)
        if self.site_name is None:
            raise ValueError(f"Site Name is required, but not provided explicitly or in config file")

        self.check_defaults = file_data.get("check_defaults", {})

        self.connection = ConnectionConfig({**file_data.get("connection", {}), **connection_details})
        self.site_checks = [CheckConfig(**x, defaults=self.check_defaults.get(x.get("check_type"), {})) for x in file_data.get("site_checks", [])]
        self.tunnels: List[TunnelConfig] = []
        for local_interface, remote_sites in file_data.get("tunnels", {}).items():
            for remote_site_name, remote_interfaces in remote_sites.items():
                for remote_interface, tunnel_data in remote_interfaces.items():
                    self.tunnels.append(TunnelConfig(
                        local_site_name=self.site_name,
                        local_interface=local_interface,
                        remote_site_name=remote_site_name,
                        remote_interface=remote_interface,
                        data=tunnel_data,
                        check_defaults=self.check_defaults,
                    ))


class ConnectionConfig:
    def __init__(
        self,
        connection_details: Optional[Dict[str, Any]] = None,
    ):
        file_data = {}
        file_name = connection_details.get("file")
        if file_name:
            try:
                with open(file_name, "r") as file:
                    file_data = yaml.safe_load(file)
            except FileNotFoundError:
                pass

        self.host = file_data.get("host", connection_details.get("host"))
        self.port = file_data.get("port", connection_details.get("port"))
        self.username = file_data.get("username", connection_details.get("username"))
        self.password = file_data.get("password", connection_details.get("password"))
        self.secure = file_data.get("secure", connection_details.get("secure", True))

        if self.host is None:
            raise ValueError(f"Host is required, but not provided explicitly or in config file")
        if self.port is None:
            raise ValueError(f"Port is required, but not provided explicitly or in config file")
        if self.username is None:
            raise ValueError(f"Username is required, but not provided explicitly or in config file")
        if self.password is None:
            raise ValueError(f"Password is required, but not provided explicitly or in config file")


class CheckConfig:
    def __init__(
        self,
        check_type: str,
        name: str,
        args: Optional[List[Any]] = None,
        kwargs: Optional[Dict[str, Any]] = None,
        interval: Optional[int] = None,
        jitter: Optional[float] = None,
        expire: Optional[int] = None,
        defaults: Optional[Dict[str, Any]] = None,
    ):
        if check_type not in ["dns", "ping"]:
            raise ValueError(f"Invalid check type: {check_type}")
        if defaults is None:
            defaults = {}
        self.check_type = check_type
        self.name = name
        self.args = args if args is not None else defaults.get("args", [])
        self.kwargs = {**defaults.get("kwargs", {}), **kwargs} if kwargs is not None else defaults.get("kwargs", {})
        self.interval = interval if interval is not None else defaults.get("interval", 60)
        self.jitter = jitter if jitter is not None else defaults.get("jitter", 0.5)
        self.expire = expire if expire is not None else defaults.get("expire", int((self.interval + self.jitter) * 2))


class TunnelConfig:
    def __init__(
        self,
        local_site_name: str,
        local_interface: str,
        remote_site_name: str,
        remote_interface: str,
        data: Dict[str, any],
        check_defaults: Optional[Dict[str, Any]] = None,
    ):
        self.local_site_name = local_site_name
        self.local_interface = local_interface
        self.remote_site_name = remote_site_name
        self.remote_interface = remote_interface
        if check_defaults is None:
            check_defaults = {}

        self.local_id = f"{local_site_name}-{local_interface}"
        self.remote_id = f"{remote_site_name}-{remote_interface}"

        self.tunnel_id = (
            f"{self.local_id}/{self.remote_id}"
            if self.local_id.lower() < self.remote_id.lower()
            else f"{self.remote_id}/{self.local_id}"
        )

        self.remote_ip = data.get("remote_ip", None)

        self.ping_check = None
        if data.get("ping", {}).get("enable", False):
            self.ping_check = CheckConfig(
                check_type="ping",
                name=f"{local_site_name} Tunnel",
                args=data.get("ping", {}).get("args", []),
                kwargs={**{"target": self.remote_ip}, **data.get("ping", {}).get("kwargs", {})},
                interval=data.get("ping", {}).get("interval", None),
                jitter=data.get("ping", {}).get("jitter", None),
                expire=data.get("ping", {}).get("expire", None),
                defaults=check_defaults.get("ping", {}),
            )

        self.dns_check = None
        if data.get("dns", {}).get("enable", False):
            self.dns_check = CheckConfig(
                check_type="dns",
                name=f"{local_site_name} Tunnel",
                args=data.get("dns", {}).get("args", []),
                kwargs={**{"server": self.remote_ip}, **data.get("dns", {}).get("kwargs", {})},
                interval=data.get("dns", {}).get("interval", None),
                jitter=data.get("dns", {}).get("jitter", None),
                expire=data.get("dns", {}).get("expire", None),
                defaults=check_defaults.get("dns", {}),
            )

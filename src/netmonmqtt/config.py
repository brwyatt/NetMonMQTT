from typing import Any, Dict, Optional
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

        self.connection = ConnectionConfig({**file_data.get("connection", {}), **connection_details})


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

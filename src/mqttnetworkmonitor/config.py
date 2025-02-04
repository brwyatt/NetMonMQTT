from typing import Optional
import yaml


class ConnectionConfig:
    def __init__(
        self,
        file_name: Optional[str] = "./connection.yaml",
        host: Optional[str] = None,
        port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ):
        file_data = {}
        if file_name:
            try:
                with open(file_name, "r") as file:
                    file_data = yaml.safe_load(file)
            except FileNotFoundError:
                pass

        self._host = file_data.get("host", host)
        self._port = file_data.get("port", port)
        self._username = file_data.get("username", username)
        self._password = file_data.get("password", password)

        if self._host is None:
            raise ValueError(f"Host is required, but not provided explicitly or in {file_name}")
        if self._port is None:
            raise ValueError(f"Port is required, but not provided explicitly or in {file_name}")
        if self._username is None:
            raise ValueError(f"Username is required, but not provided explicitly or in {file_name}")
        if self._password is None:
            raise ValueError(f"Password is required, but not provided explicitly or in {file_name}")

    def __getitem__(self, key):
        if not key in ["host", "port", "username", "password"]:
            raise KeyError(f"{key} is not a valid key")
        return getattr(self, f"_{key}")


class Config:
    def __init__(self, file_name: str = "./config.yaml"):
        try:
            with open(file_name, "r") as file:
                self._data = yaml.safe_load(file)
        except FileNotFoundError:
            raise ValueError(f"Config file {file_name} not found")

        if not isinstance(self._data.get("site"), dict):
            raise ValueError("Missing 'site' in config file")

        if not isinstance(self._data.get("site", {}).get("name"), str):
            raise ValueError("Missing 'site.name' in config file or not a string")

        if not isinstance(self._data.get("site", {}).get("domain"), str):
            raise ValueError("Missing 'site.domain' in config file or not a string")

        if not isinstance(self._data.get("site", {}).get("interfaces"), int):
            raise ValueError("Missing 'site.interfaces' in config file or not a number")

    def __getitem__(self, key):
        return self._data[key]

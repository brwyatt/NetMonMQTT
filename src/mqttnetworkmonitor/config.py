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
            raise ValueError("Host is required")
        if self._port is None:
            raise ValueError("Port is required")
        if self._username is None:
            raise ValueError("Username is required")
        if self._password is None:
            raise ValueError("Password is required")

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

    def __getitem__(self, key):
        return self._data[key]

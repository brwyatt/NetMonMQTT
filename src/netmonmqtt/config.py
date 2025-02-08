from typing import Optional
import yaml


class Config:
    def __init__(
        self,
        file_name: Optional[str] = "./config.yaml",
        host: Optional[str] = None,
        port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        site_name: Optional[str] = None,
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
        self._site_name = file_data.get("site_name", site_name)

        if self._host is None:
            raise ValueError(f"Host is required, but not provided explicitly or in {file_name}")
        if self._port is None:
            raise ValueError(f"Port is required, but not provided explicitly or in {file_name}")
        if self._username is None:
            raise ValueError(f"Username is required, but not provided explicitly or in {file_name}")
        if self._password is None:
            raise ValueError(f"Password is required, but not provided explicitly or in {file_name}")
        if self._site_name is None:
            raise ValueError(f"Site Name is required, but not provided explicitly or in {file_name}")


    def __getitem__(self, key):
        if not key in ["host", "port", "username", "password", "site_name"]:
            raise KeyError(f"{key} is not a valid key")
        return getattr(self, f"_{key}")

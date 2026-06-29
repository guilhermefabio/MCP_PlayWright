"""Runtime configuration loaded from the .env file for use in generated tests."""

import os

from dotenv import load_dotenv


class Config:
    """Reads BASE_URL, LOGIN_USER and LOGIN_PASSWORD from the environment.

    Raises EnvironmentError on the first missing variable so the failure is
    obvious before any browser or network call is made.
    """

    def __init__(self) -> None:
        load_dotenv()
        self.base_url: str = self._require("BASE_URL")
        self.login_user: str = self._require("LOGIN_USER")
        self.login_password: str = self._require("LOGIN_PASSWORD")

    @staticmethod
    def _require(var_name: str) -> str:
        value = os.getenv(var_name)
        if not value:
            raise EnvironmentError(
                f"Required environment variable not set: {var_name}\n"
                f"Create a .env file based on .env.example"
            )
        return value

"""Runtime configuration loaded from the .env file for use in generated tests."""

import os

from dotenv import find_dotenv, load_dotenv


class Config:
    """Reads BASE_URL, LOGIN_USER and LOGIN_PASSWORD from the environment.

    Raises EnvironmentError on the first missing variable so the failure is
    obvious before any browser or network call is made.
    """

    def __init__(self) -> None:
        # find_dotenv() walks up from cwd until it finds a .env file,
        # so this works regardless of where pytest is invoked from.
        load_dotenv(find_dotenv(usecwd=True))
        self.base_url: str = self._require("BASE_URL")
        self.login_user: str = self._require("LOGIN_USER")
        self.login_password: str = self._require("LOGIN_PASSWORD")

    @staticmethod
    def _require(var_name: str) -> str:
        value = os.getenv(var_name)
        if not value:
            raise OSError(
                f"Required environment variable not set: {var_name}\n"
                f"Create a .env file based on .env.example"
            )
        return value

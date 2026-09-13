"""Config for the Robocorp Control Room API."""

import pydantic


class ControlRoomConfig(pydantic.BaseModel):
    """Robocorp Control Room API configuration."""

    api_key: str
    """
    Control Room API key with an appropriate permission set for the
    actions to be performed.
    """

    endpoint: str = "https://cloud.robocorp.com/api/v1/"
    """
    Alternative endpoint of the Control Room API. Only required for
    SSO users with a custom Robocorp API endpoint. Defaults to
    `https://cloud.robocorp.com/api/v1/`.
    """

    @property
    def auth_header(self) -> dict[str, str]:
        """Return the 'Authorization' header required for CR API auth."""
        return {"Authorization": f"RC-WSKEY {self.api_key}"}

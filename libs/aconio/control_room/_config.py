"""Wrapper config for the Robocorp Control Room API."""

import functools


class _ControlRoomAPIConfig:
    """Robocorp Control Room API configuration."""

    api_key: str | None = None
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

        if not self.api_key:
            raise ValueError(
                "Failed to generate API auth header! "
                "`api_key` must be set first!"
            )

        return {"Authorization": f"RC-WSKEY {self.api_key}"}


@functools.lru_cache
def config() -> _ControlRoomAPIConfig:
    return _ControlRoomAPIConfig()

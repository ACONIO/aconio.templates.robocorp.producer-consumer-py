"""Data models used throughout the module."""

from __future__ import annotations

import robocorp.vault


class USPCredentials:
    """Credentials for USP login."""

    def __init__(self, participant_id: str, user_id: str, pin: str) -> None:
        self.participant_id = participant_id
        self.user_id = user_id
        self.pin = pin

    @staticmethod
    def from_vault(vault_secret_name: str) -> USPCredentials:
        """Load credentials from Robocorp vault.

        Args:
            vault_secret_name (str):
                The name of the Robocorp vault secret to use.

        The provided Robocorp vault secret must include the following keys:
        - `participant_id`
        - `user_id`
        - `pin`
        """
        creds = robocorp.vault.get_secret(vault_secret_name)

        return USPCredentials(
            participant_id=creds["teilnehmer_id"],
            user_id=creds["benutzer_id"],
            pin=creds["pin"],
        )

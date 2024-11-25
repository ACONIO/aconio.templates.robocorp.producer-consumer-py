"""USP helper class."""

import os

from robocorp import vault, browser


class USP:
    """Base class for any USP task."""

    _base_url = "https://mein.usp.gv.at/"

    def __init__(self, debug: bool = False) -> None:
        # Enable Playwright debug mode
        if debug:
            os.environ["PWDEBUG"] = "1"

        browser.configure_context(viewport={"width": 1800, "height": 900})

        self._context = browser.context()
        self._page = browser.page()

    def login_usp(self, vault_secret: str = "usp_credentials") -> None:
        """Login to USP.

        Open the browser, navigate to `_base_url`, and login.

        Args:
            vault_secret (str):
                The name of the Robocorp vault secret to use.
                The provided Robocorp vault secret must include the keys
                - `teilnehmer_id`
                - `benutzer_id`
                - `pin`.
        """
        self._page.goto(self._base_url)

        creds = vault.get_secret(vault_secret)
        self._page.locator("[id=tid]").fill(creds["teilnehmer_id"])
        self._page.locator("[id=benid]").fill(creds["benutzer_id"])
        self._page.locator("[id=pin]").fill(creds["pin"])
        self._page.locator("[id=kc-login]").click()

    def pause(self) -> None:
        self._page.pause()

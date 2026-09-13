"""USP helper class."""

import os

import robocorp.browser

from aconio.usp.models import USPCredentials
from aconio.usp._config import config


class USP:
    """Base class for any USP task."""

    def __init__(
        self,
        base_url="https://mein.usp.gv.at/",
    ) -> None:

        self.base_url = base_url

        # Enable Playwright debug mode
        if config().browser_debug:
            os.environ["PWDEBUG"] = "1"

        robocorp.browser.configure_context(
            viewport={"width": 1800, "height": 900}
        )

        self._context = robocorp.browser.context()
        self._page = robocorp.browser.page()

    def login_usp(self, creds: USPCredentials) -> None:
        """Login to USP.

        Open the browser, navigate to the base URL, and login.

        Args:
            credentials (USPCredentials):
                The credentials to use for the login.
        """
        self._page.goto(self.base_url)

        self._page.locator("[id=tid]").fill(creds.participant_id)
        self._page.locator("[id=benid]").fill(creds.user_id)
        self._page.locator("[id=pin]").fill(creds.pin)
        self._page.locator("[id=kc-login]").click()

    def pause(self) -> None:
        self._page.pause()

"""Playwright browser for interacting with FinanzOnline.

This is used for special interactions with FinanzOnline that
cannot be imitated via the "Pseudo API", such as downloading
the "Steuerkonto" PDF.
"""

import time
import typing

import robocorp.browser

import aconio.utils

from aconio.fon._urls import FonURL
from aconio.fon._auth import FonSession, FonCredential


class FonBrowser:
    """Playwright browser for interacting with FinanzOnline."""

    def __init__(self, session: FonSession) -> None:
        self.session = session

        robocorp.browser.configure(headless=True)

        self.context = robocorp.browser.context()
        self.context.add_cookies(
            cookies=[
                {"name": k, "value": v, "url": FonURL.BASE}
                for k, v in session.get_cookies().items()
            ]
        )

    def _login_finanzonline(self, credential: FonCredential) -> typing.Any:
        """Login to FinanzOnline.

        Note: This login is not required for authentication. Passing the FON
        session upon class initialization is sufficient. This method is only
        required for performing a FON login via the browser.

        This can be useful to trigger certain scenarios such as the
        "Personifizierung" pop-up.

        Note that the page is not closed after login. This allows for further
        interaction with the page if needed.
        """

        page = self.context.new_page()

        page.locator("[name=tid]").fill(credential.participant_id)
        page.locator("[name=benid]").fill(credential.user_id)
        page.locator("[name=pin]").fill(credential.pin)

        # Wait for all values to be set properly before submitting.
        time.sleep(1.5)

        page.locator('//input[@name="submit"]').click()

        return page

    # TODO: This function can be removed if we find out that we do not need to
    # actually handle the "Personifizierung" dialog in the browser, but we can
    # just directly navigate to the routes we need.
    def skip_personification(self, credential: FonCredential) -> None:
        """Login to FinanzOnline and skip the "Personifizierung" dialog.

        This cuases the dialog to now show in subsequent logins.

        This is useful for testing purposes, where the dialog
        should not block the test execution.
        """

        page = self._login_finanzonline(credential)

        # pylint: disable=line-too-long
        page.locator(
            '//label[contains(text(),"Ich möchte die Personifizierung später durchführen.")]'
        ).click()
        page.locator('//input[@name="submit"]').click()

        page.close()

    def download_tax_account_pdf(
        self,
        tax_id: str,
        output_filepath: str,
        anmerkungen: bool = False,
        rueckzahlungen: bool = False,
        zahlungsplan: bool = False,
        vorauszahlungen: bool = False,
        rueckstandsaufgliederung: bool = False,
    ) -> None:
        """Save the FinanzOnline "Steuerkonto" as PDF."""

        page = self.context.new_page()
        page.goto(
            f"{FonURL.BASE}/fon/p/konto.do?reqkey={self.session.request_key}"
        )

        page.locator('//input[@id="suchob"]').fill(tax_id)

        # Select the query result checkboxes according to the given params
        if rueckzahlungen:
            page.locator('//input[@name="sabfrrz"]').check()
        if anmerkungen:
            page.locator('//input[@name="sabfranm"]').check()
        if zahlungsplan:
            page.locator('//input[@name="sabfrzp5"]').check()
        if vorauszahlungen:
            page.locator('//input[@name="sabfrvan"]').check()
        if rueckstandsaufgliederung:
            page.locator('//input[@name="sabfrraufgl"]').check()

        page.locator('//input[@name="submit"]').click()

        time.sleep(1)  # Wait for page to properly load before storing PDF

        # Remove the header, since it will display on each page and
        # overlap other content.
        # pylint: disable=line-too-long
        aconio.utils.wait_until_succeeds(
            retries=3,
            timeout=3,
            function=page.evaluate,
            expression="""document.querySelector('[id="reactHeaderRoot"]').style.display = 'none';""",
        )

        page.pdf(
            path=output_filepath,
            scale=0.7,
            margin={
                "top": "20px",
                "right": "20px",
                "left": "20px",
                "bottom": "20px",
            },
        )

        page.close()

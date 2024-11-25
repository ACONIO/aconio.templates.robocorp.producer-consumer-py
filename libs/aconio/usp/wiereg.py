"""Interactions with the WiEReG service."""

import time
import functools

from robocorp import log

from ._usp import USP


class _WiEReG(USP):
    """WiEReG Management System class.

    We use the word extract for the "Auszug" throughout.
    """

    def __init__(self, debug: bool = False) -> None:
        super().__init__(debug=debug)
        self._repr_form_url = (
            "https://www.usp.gv.at/at.gv.bmf.wieregmgmt-p/"
            "formulare/mpu-formulare/meldung-anlegen"
        )

    def navigate_to(self, page_name: str):
        """Navigate to specific page in WiEReG Management System."""

        self._goto_home()

        time.sleep(1)  # Wait for page to catch-up.

        # First, collapse to get the same starting point each time.
        collapse_btn = self._page.locator("[id='collapseTree']")
        collapse_btn.wait_for(state="visible")
        collapse_btn.click()

        # Then, uncollapse all menu items.
        expand_btn = self._page.locator("[id='expandTree']")
        expand_btn.wait_for(state="visible")
        expand_btn.click()

        time.sleep(1)  # Wait for navigation to uncollapse.

        # Then click (now visible) menu item.
        page_btn = self._page.get_by_text(page_name, exact=True)
        page_btn.wait_for(state="visible")
        page_btn.click()

    def repr_form_open(self, stammzahl: str):
        """Open "Meldung durch Parteienvertreter" form."""

        self._page.goto(self._repr_form_url)

        self._page.get_by_text(
            "Meldung als Parteienvertreter", exact=True
        ).click()

        self._page.locator("[id='stammzahl_input']").fill(stammzahl)
        self._page.get_by_text(" Suchen ", exact=True).click()
        self._page.get_by_text(" Weiter zum Formular > ", exact=True).click()

    def repr_form_update(self, email: str):
        """Update "Meldung durch Parteienvertreter" form.

        Args:
            email (str):
                The email address to use for the "E-Mailadressen für Rückfragen
                zur Meldung bzw. einem Compliance-Package" field.
        """
        self._page.get_by_text(" Angaben zur Meldung ", exact=True).click()

        # Click on "Ja" for "Feststellung und Überprüfung durch einen
        # berufsmäßigen Parteienvertreter".
        self._page.locator("[id='feststellung_uberprufung_pv_Ja']").click()

        # Click on "Nein" for "Soll ein Compliance-Package übermittelt werden?".
        self._page.locator(
            "[id='ubermittlung_compliance_package_Nein']"
        ).click()

        # Fill in email addresses.
        self._page.locator("[id='email_pv_input']").fill(email)
        self._page.locator("[id='email_rt_input']").fill(email)
        self._page.get_by_text(" Zwischenspeichern ", exact=True).click()

    def repr_form_submit(self, test_mode: bool = True):
        """Submit "Meldung durch Parteienvertreter" form."""
        self._page.get_by_text(" Zusammenfassung ", exact=True).click()

        submit_btn = self._page.get_by_text(" Formular abschicken ", exact=True)
        submit_btn.wait_for(state="visible")
        if test_mode:
            is_visible = submit_btn.is_visible()
            log.info(
                f"Test mode activated. Send button is visible: {is_visible} "
            )
        else:
            log.info("Test mode deactivated. Submitting form.")
            submit_btn.click()
            self._page.wait_for_url(self._repr_form_url + "?erfolg=true")

    def extract_insert_stammzahl(self, stammzahl: str):
        """Insert "Stammzahl" into input field and press submit."""
        self._page.locator(
            "[id='j_id_4b:j_id_4t:j_id_4u:sucherechtstraegerform_stammzahl']"
        ).fill(stammzahl)
        self._page.locator("[id='j_id_4b:j_id_4t:j_id_4u:j_id_57']").click()

        time.sleep(1)  # Wait for new page.

    def extract_create(self):
        """Download "einfach" extract."""
        self._page.locator("[id='j_id_4c:auszug']").click()

        time.sleep(5)  # Wait for document creation.

    def extract_save(self, filepath: str):
        """Save the downloaded extract to a file."""
        with self._page.expect_download() as download_info:
            self._page.get_by_text("Speichern").click()

        download = download_info.value
        download.save_as(filepath)

    def _goto_home(self):
        """Navigate to WiEReG home page."""
        self._page.goto(self._base_url)

        with self._context.expect_page() as new_page:
            self._page.get_by_text("WiEReG Management System").click()

        self._page = new_page.value


@functools.lru_cache
def _wiereg() -> _WiEReG:
    """Return a new WiEReG instance."""
    return _WiEReG(debug=False)


def login(usp_vault_secret: str = "usp_credentials"):
    """Login to USP.

    Open the browser, navigate to the USP base URL and login.
    The given Robocorp vault secret must include the keys `teilnehmer_id`,
    `benutzer_id`, and `pin` and is being used to login to the USP portal.
    """
    _wiereg().login_usp(vault_secret=usp_vault_secret)


def download_extract(stammzahl: str, filepath: str):
    """Download WiEReG extract.

    Must call `login` beforehand.

    Args:
        stammzahl:
            The "Stammzahl" of the entity.
        filepath:
            The path where the downloaded extract should be saved.
    """
    _wiereg().navigate_to(page_name="Suche mit der Stammzahl")
    _wiereg().extract_insert_stammzahl(stammzahl=stammzahl)
    _wiereg().extract_create()
    _wiereg().extract_save(filepath=filepath)


def perform_meldung(stammzahl: str, email: str, test_mode: bool = False):
    """Perform "Meldung".

    Must call `login` beforehand.

    Args:
        stammzahl:
            The "Stammzahl" of the entity.
        email:
            The email address to use for the "Meldung".
        test_mode:
            If enabled, all functions will be performed as usual, except
            the button to submit the form will only be checked for visibility,
            not actually clicked. Defaults to `False`.
    """
    _wiereg().navigate_to(page_name="Einmeldung als Parteienvertreter")
    _wiereg().repr_form_open(stammzahl)
    _wiereg().repr_form_update(email)
    _wiereg().repr_form_submit(test_mode=test_mode)

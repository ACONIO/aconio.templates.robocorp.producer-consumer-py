"""Interactions with the WEBEKU service."""

import re
import time
import datetime
import functools

from dataclasses import dataclass
from enum import StrEnum

from bs4 import BeautifulSoup
from robocorp import browser

from ._usp import USP


class Action(StrEnum):
    """Represent the available WE-BE-KU actions for an account."""

    KONTOINFORMATIONEN = "K"
    BUCHUNGEN = "B"
    CLEARING = "C"
    AGH = "A"


@dataclass
class Account:
    """Represent a "Beitragskonto" on the WE-BE-KU page."""

    ogk_id: str
    actions: list[Action]


class NoAghTransactionsFound(Exception):
    """Exception raised when no AGH bookings are found.

    Raise if "Es wurden keine AGH Buchungen gefunden" is displayed
    upon retrieving the 'AGH Kontoauszug' in WEBEKU portal.
    """

    def __init__(
        self, *args, msg="no AGH transactions for this client", **kwargs
    ):
        super().__init__(msg, *args, **kwargs)


class NoTransactionsFound(Exception):
    """Exception raised when no bookings are found.

    Raise if "Für das Beitragskonto ... keine Buchungen gefunden"
    is displayed upon retrieving the "Buchungen" in WEBEKU portal.
    """

    def __init__(self, *args, msg="no transactions for this client", **kwargs):
        super().__init__(msg, *args, **kwargs)


class WEBEKU(USP):
    """WE-BE-KU service portal class."""

    def login(
        self,
        usp_vault_secret: str = "usp_credentials",
        role: str = "Bevollmächtigte(r)",
    ):
        """Login to USP.

        Open the browser, navigate to the USP base URL and login. Then open
        the WEBEKU service and select the correct role, ("Bevollmächtigte(r)").
        The given Robocorp vault secret must include the keys `teilnehmer_id`,
        `benutzer_id`, and `pin` and is being used to login to the USP portal.
        """

        self.login_usp(usp_vault_secret)

        # Get WE-BE-KU page after clicking on USP service (opens in new tab).
        with self._context.expect_page() as new_page_info:
            self._page.get_by_text("WEB-BE-Kunden-Portal (WEBEKU)").click()

        self.__webeku = new_page_info.value
        self.__webeku.wait_for_load_state()

        # Choose the "Bevollmächtigter" which then directs to the WE-BE-KU
        # main page.
        self.__webeku.get_by_role("link", name=role).click()

    def get_all_accounts(self) -> list[Account]:
        """Query all available "Beitragskonten" from the "Kontoübersicht".

        Navigates through multiple pages if necessary.
        """
        self.select_menu("Kontoübersicht")

        accounts: list[Account] = []

        # Get locator for next button that is not disabled.
        next_btn = self.__webeku.locator(
            '//div[contains(@class, "aui-dt-p-next") and '
            'not(contains(@class, "aui-dt-p-disabled"))]'
        )
        while True:
            accounts.extend(self.__read_accounts_table())

            if not next_btn.is_visible():
                break  # stop if next button not visible (no more pages).
            else:
                next_btn.click()
                time.sleep(1)

        return accounts

    def load_account(self, ogk_account_number: str):
        """Query a "Beitragskonto".

        Automatically navigates to 'Kontoübersicht' before starting query.
        """

        self.select_menu("Kontoübersicht")

        self.__webeku.get_by_label("Beitragskontonummer").fill(
            ogk_account_number
        )
        self.__webeku.get_by_role("button", name="Suchen", exact=True).click()

    def select_menu(self, name: str):
        """Select a menu from the WE-BE-KU nav bar on the left side.

        Must be used after a "Beitragskonto" has been loaded using
        `load_account`.

        Args:
            name: The name of the menu to select.
        """
        self.__webeku.get_by_role("button", name=name).click()

    def start_query(self, start_date: datetime.date, end_date: datetime.date):
        """Start a query for a given date range.

        Enter a search date on a sub-page such as 'Buchungen' and start the
        search. Expects the date formatted as `DD.MM.YYYY`.

        Raises:
            NoAghTransactionsFound:
                If "Es wurden keine AGH Buchungen gefunden" msg appears.
            NoTransactionsFound:
                If "Beitragskonto ... keine Buchungen gefunden" msg appears.
        """
        self.__webeku.get_by_role(
            "cell", name="Buchungsdatum", exact=True
        ).locator("label").click()

        self.__webeku.get_by_label("atum von").fill(
            start_date.strftime("%d.%m.%Y")
        )
        self.__webeku.get_by_label("atum bis").fill(
            end_date.strftime("%d.%m.%Y")
        )

        self.__webeku.get_by_role("button", name="Suchen", exact=True).click()

        # Stop if "Es wurden keine AGH Buchungen" text is displayed!
        if self.__webeku.get_by_text(
            "Es wurden keine AGH Buchungen"
        ).is_visible():
            raise NoAghTransactionsFound()
        elif self.__webeku.get_by_text(
            "wurden keine Buchungen gefunden!"
        ).is_visible():
            raise NoTransactionsFound()

    def download_pdf(self, filepath: str):
        """Expand all rows of the table and download the PDF.

        This can only be called after a search has been performed with
        `start_search`.
        """
        self.__download_file(
            locator=self.__webeku.get_by_role("link", name="Als PDF speichern"),
            filepath=filepath,
        )

    def download_csv(self, filepath: str):
        """Expand all rows of the table and download the CSV.

        This can only be called after a search has been performed with
        `start_search`.
        """
        self.__download_file(
            locator=self.__webeku.get_by_role("link", name="Als CSV speichern"),
            filepath=filepath,
        )

    def __download_file(self, locator: browser.Locator, filepath: str):
        """Download a file from the WE-BE-KU portal using the given locator.

        Expand all rows of the table and download a file, where the given
        locator is the button to download the file. This can only be called
        after a search has been performed with `start_search`.
        """
        self.__expand_all_rows()

        with self.__webeku.expect_download() as download_info:
            locator.click()

        # Wait for the download process to complete and save the downloaded
        # file.
        download_info.value.save_as(filepath)

    def __expand_all_rows(self):
        """Expand all rows of a table after a query (e.g. in 'Buchungen').

        If they are already expanded, do nothing.

        Raises:
            RuntimeError:
                If the indicator that rows are already expanded,
                or the expand all button are not found.
        """
        # Only click expand button if rows are not already expanded.
        if not self.__webeku.get_by_role(
            "img", name="Alle Buchungen zuklappen"
        ).is_visible():
            expand_btn = self.__webeku.get_by_role(
                "link", name=re.compile("Alle.*")
            )

            if expand_btn.is_visible():
                expand_btn.click()
            else:
                raise RuntimeError(
                    "Rows expanded indicator and 'Expand all rows'"
                    "button not found!"
                )

    def __read_accounts_table(self) -> list[Account]:
        """Parse all "Beitragskonten" from the "Kontoübersicht" table."""

        soup = BeautifulSoup(self.__webeku.content(), "html.parser")

        accounts: list[Account] = []
        for row in soup.find("tbody").find_all(
            "tr"
        ):  # only one table on this page
            cols = row.find_all("td")

            accounts.append(
                Account(
                    ogk_id=cols[0].text.strip(),
                    actions=[
                        Action(act.get("value"))
                        for act in cols[5].find_all("input")
                    ],
                )
            )

        return accounts


@functools.lru_cache
def webeku() -> WEBEKU:
    """Return a new WEBEKU instance."""
    return WEBEKU(debug=False)

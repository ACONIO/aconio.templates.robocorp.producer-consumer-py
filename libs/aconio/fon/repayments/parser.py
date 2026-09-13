""" "FinanzOnline" HTML data parsers."""

import re
import bs4
import requests

from aconio.fon.repayments.dto import BankDetails


class RepaymentParsingError(Exception):
    """Exception raised when the repayment page cannot be parsed."""

    pass


class RepaymentParser:
    """Parse the response from the "FinanzOnline" repayment page."""

    def __init__(self, response: requests.Response) -> None:
        self._response = response

        self.soup = bs4.BeautifulSoup(self._response.text, "html.parser")

    def get_bank_details(self) -> BankDetails:

        iban = self._extract_bank_detail("IBAN")
        try:
            bic = self._extract_bank_detail("BIC")
        except Exception:  # pylint: disable=broad-except
            bic = None

        return BankDetails(iban=iban, bic=bic)

    def _extract_bank_detail(self, detail_name: str) -> str:
        """Extract a specific bank detail from the soup.

        Args:
            detail_name:
                The name of the bank detail to extract (e.g., "IBAN", "BIC").

        Returns:
            The extracted bank detail.
        """

        return (
            self.soup.find("div", attrs={"class": "well"})
            .find("div", text=re.compile(rf".*{detail_name}:.*"))
            .find_next_sibling("div")
            .text.strip()
        )

""" "FinanzOnline" HTML data parsers."""

import re
import bs4
import requests

import aconio.utils

from typing import Any

from aconio.fon.errors import TaxAccountQueryError, TaxAccountParsingError
from aconio.fon.tax_account.dto import TaxAccount


class TaxAccountParser:
    """Parse the response from the "FinanzOnline" tax account query."""

    def __init__(self, response: requests.Response) -> None:
        self._response = response

        self.soup = bs4.BeautifulSoup(self._response.text, "html.parser")

    def parse(self) -> TaxAccount:
        self._raise_if_query_error()
        return self._extract_tax_account_info()

    def _raise_if_query_error(self) -> bool:
        error_msg = self.soup.find("ul", attrs={"id": "fehlerAufgetretenListe"})

        if error_msg is not None:
            # Remove "list sign" (dot) from error message
            err = error_msg.text[2::]
            raise TaxAccountQueryError(err)

    def _extract_tax_account_info(self) -> TaxAccount:
        account = TaxAccount()

        account.tax_id = self._extract_tax_id()
        account.finanzamt_number = self._extract_finanzamt_number()

        if self._has_no_data():
            account.balance_date = None
            account.balance = None
        else:
            balance_table = self._get_balance_table()
            account.balance_date = self._extract_balance_date(balance_table)
            account.balance = self._extract_balance(balance_table)

        account.postings = self._extract_postings_table()
        account.payment_plan = self._extract_payment_plan_table()
        account.repayments = self._extract_repayments_table()
        account.prepayments = self._extract_prepayments_table()
        account.quarterly_amounts = self._extract_quarterly_amounts_table()
        account.arrears = self._extract_arrears_breakdown_table()

        return account

    def _extract_tax_id(self) -> str:
        return (
            self.soup.find("div", text=re.compile(r".*Steuernummer.*"))
            .find_next_sibling("div")
            .text.strip()
        )

    def _extract_finanzamt_number(self) -> str | None:
        finanzamt_text = (
            self.soup.find("div", text=re.compile(r".*Finanzamt.*"))
            .find_next_sibling("div")
            .text.strip()
        )

        match = re.search(r"\((\d+)\)", finanzamt_text)
        if match:
            return match.group(1)

        return None

    def _get_balance_table(self) -> Any:
        """Get the "Endsaldo" table from the tax account query response."""
        tables = self.soup.find_all("table", attrs={"class": "table"})
        if len(tables) < 3:
            raise TaxAccountParsingError(
                "Expected at least three elements with "
                "CSS class 'table', but found fewer."
            )
        return tables[2]

    def _extract_balance(self, balance_table: Any) -> float:
        amount = balance_table.find_all("td")[1].text.strip()
        return aconio.utils.from_german_currency_string(amount)

    def _extract_balance_date(self, balance_table: Any) -> str:
        return balance_table.find_all("td")[0].text.strip()

    def _has_no_data(self) -> bool:
        """Check if "Buchungen" section shows "keine Daten vorhanden"."""

        return self.soup.find(
            "div", attrs={"aria-label": re.compile(r".*Buchungen (vom|bis).*")}
        ).find(
            "div", text=re.compile(r".*Keine entsprechenden Daten vorhanden.*")
        )

    def _extract_postings_table(self) -> list[dict] | None:
        pattern = r".*Buchungen (vom|bis).*"
        return self._parse_tax_account_table(re.compile(pattern))

    def _extract_payment_plan_table(self) -> list[dict] | None:
        return self._parse_tax_account_table("Zahlungsplan")

    def _extract_repayments_table(self) -> list[dict] | None:
        return self._parse_tax_account_table("Information zu Rückzahlungen")

    def _extract_prepayments_table(self) -> list[dict] | None:
        return self._parse_tax_account_table(
            "Vorauszahlungen/Veranlagungen",
            headers=["Abgabenart", "Jahr", "Betrag", "Veranlagung"],
        )

    def _extract_quarterly_amounts_table(self) -> list[dict] | None:
        return self._parse_tax_account_table(
            "Vierteljahresbeträge",
            headers=["Art", "Periode", "Betrag", "Anmerkung"],
        )

    def _extract_arrears_breakdown_table(self) -> list[dict] | None:
        return self._parse_tax_account_table("Rückstandsaufgliederung")

    def _parse_tax_account_table(
        self, aria_label: str | re.Pattern, headers: list[str] | None = None
    ) -> list[dict] | None:
        """Parse an HTML table of the "Steuerkonto".

        This works with all tables on the "Steuerkonto" page
        (e.g. "Buchungen", "Zahlungsplan", "Rückzahlungen", etc.).

        Table headers can be optionally provided. This is useful if
        the table uses merged header columns (e.g. there is only one
        "Vorauszahlung/Veranlagung" header column, but three actual
        columns "Abgabenart", "Jahr", "Betrag"). If not provided, the
        headers will be extracted from the HTML table (which works for
        tables without merged header columns, e.g. "Buchungen").

        Args:
            aria_label:
                The `aria-label` HTML property value of the section `div`.
                Can be regex pattern.

        Returns:
            List of dictionaries with the extracted data.
            Each entry in the list represents a row in the table.
        """

        section = self.soup.find("div", attrs={"aria-label": aria_label})

        if not section:
            return None

        # Check if section is empty
        no_data_text = section.find(
            "div", text=re.compile(r".*Keine entsprechenden Daten vorhanden.*")
        )

        if no_data_text is not None:
            return None

        table = section.find("table", attrs={"class": "table-striped"})

        # Grab all table header names
        if not headers:
            headers = [th.text for th in table.find_all("th")]

        # Extract values from the table rows
        extracted_data = []

        # For each table row, create a dictionary with:
        # key=column name / value=column value
        for row in table.find_all("tr"):
            data = {}
            columns = row.find_all("td")

            if len(columns) > 0:
                # Get the data of this row for each header (i.e. column)
                for idx, th in enumerate(headers):
                    data[th] = (
                        columns[idx]
                        .text.strip()
                        .replace("\t", "")
                        .replace("\n", "")
                    )
                extracted_data.append(data)

        return extracted_data

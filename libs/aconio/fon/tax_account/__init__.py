"""FinanzOnline pseudo-API for tax account interactions.

Equivalent to the "Steuerkonto" option within the
"Abfragen" menu on the "FinanzOnline" portal.
"""

import requests

from aconio.fon._urls import FonURL
from aconio.fon._browser import FonBrowser

from aconio.fon._wrapper import _FinanzOnlineWrapperAPI

from aconio.fon.tax_account.dto import TaxAccount
from aconio.fon.tax_account.parser import TaxAccountParser


class _TaxAccountAPI(_FinanzOnlineWrapperAPI):
    """FinanzOnline pseudo-API for tax account interactions."""

    def get_tax_account(
        self,
        tax_id: str,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> TaxAccount:
        """Query the tax account for a specific tax number."""

        response = self._post_query_request(tax_id, date_from, date_to)
        parser = TaxAccountParser(response)
        return parser.parse()

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
        """Return the FinanzOnline "Steuerkonto" as PDF.

        Args:
            tax_id:
                Client tax number for which the query should be performed.

            output_filepath:
                Download location for the PDF file.

            anmerkungen:
                Include "Anmerkungen" section in the PDF.

            rueckzahlungen:
                Include "Rückzahlungen" section in the PDF.

            zahlungsplan:
                Include "Zahlungsplan" section in the PDF.

            vorauszahlungen:
                Include "Vorauszahlungen/Veranlagungen" section in the PDF.

            rueckstandsaufgliederung:
                Include "Rückstandsaufgliederung" section in the PDF.
        """

        browser = FonBrowser(self._session)
        browser.download_tax_account_pdf(
            tax_id=tax_id,
            output_filepath=output_filepath,
            anmerkungen=anmerkungen,
            rueckzahlungen=rueckzahlungen,
            zahlungsplan=zahlungsplan,
            vorauszahlungen=vorauszahlungen,
            rueckstandsaufgliederung=rueckstandsaufgliederung,
        )

    def _post_query_request(
        self,
        tax_id: str,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> requests.Response:
        form_data = {
            "suchob": tax_id,
            "sabfrzp5": "true",  # enable "Zahlungsplan"
            "sabfrrz": "true",  # enable "Rückzahlungen"
            "sabfrvan": "true",  # enable "Vorauszahlungen/Veranlagungen"
            "sabfrraufgl": "true",  # enable "Rückstandsaufgliederung"
        }

        # Add "Zeitraum ab" parameter to query
        if date_from is not None:
            form_data["sabfrbubta"] = date_from

        # Add "Zeitraum bis" parameter to query
        if date_to is not None:
            form_data["sabfrbubtb"] = date_to

        return self._session.post(
            url=FonURL.QUERY_TAX_ACCOUNT,
            data=form_data,
        )

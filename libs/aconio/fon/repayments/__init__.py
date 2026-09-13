"""FinanzOnline pseudo-API for repayment interactions.

Equivalent to the "Rückzahlungen" option within the
"Weitere Services" menu on the "FinanzOnline" portal.
"""

import re
import bs4

from aconio.fon._urls import FonURL
from aconio.fon.errors import RepaymentRequestError

from aconio.fon._wrapper import _FinanzOnlineWrapperAPI
from aconio.fon.repayments.dto import (
    RepaymentRecipient,
    BankDetails,
    RepaymentDestination,
)
from aconio.fon.repayments.parser import RepaymentParser


class _RepaymentAPI(_FinanzOnlineWrapperAPI):
    """FinanzOnline pseudo-API for repayment interactions."""

    COID_RE_PATTERN = re.compile(r"coid=(.*?)&")

    REPAYMENT_SUCCESS_RE_PATTERN = re.compile(
        r"Die eingegebenen Daten wurden gespeichert."
    )

    def get_saved_bank_details(self, tax_id: str) -> BankDetails:
        """Obtain the default bank details stored in FinOn for a tax ID.

        These are the default bank details stored in FinanzOnline."""

        # We can always use destination "Inland" to obtain the bank details.
        response = self._initiate_repayment(
            tax_id, destination=RepaymentDestination.DOMESTIC
        )
        parser = RepaymentParser(response)

        return parser.get_bank_details()

    def create_repayment_draft(
        self,
        tax_id: str,
        recipients: list[RepaymentRecipient] | RepaymentRecipient,
        destination: RepaymentDestination = RepaymentDestination.DOMESTIC,
    ) -> None:
        """Create a "Rückzahlungsantrag" draft."""

        if isinstance(recipients, RepaymentRecipient):
            recipients = [recipients]

        self._validate_repayment_request(recipients, destination)

        response = self._initiate_repayment(tax_id, destination)
        coid = self._extract_coid(response.text)

        self._create_draft(coid, recipients)

    def _validate_repayment_request(
        self,
        recipients: list[RepaymentRecipient],
        destination: RepaymentDestination,
    ) -> None:
        """Perform basic validation of the repayment request."""

        for recipient in recipients:
            if not recipient.bank_details:
                # In theory, FinanzOnline allows recipients without bank
                # details, but we require bank details for all recipients.
                raise ValueError(
                    "Cannot create repayment without bank details."
                )

            # If the destination is "Ausland", we need to ensure that
            # the IBAN is not an Austrian one.
            if (
                destination == RepaymentDestination.FOREIGN
                and recipient.bank_details.iban.startswith("AT")
            ):
                raise ValueError(
                    "Cannot create foreign repayment with Austrian IBAN. "
                    "Please use destination 'RepaymentDestination.DOMESTIC'."
                )

            if (
                destination == RepaymentDestination.DOMESTIC
                and not recipient.bank_details.iban.startswith("AT")
            ):
                raise ValueError(
                    "Cannot create domestic repayment with foreign IBAN. "
                    "Please use destination 'RepaymentDestination.FOREIGN'."
                )

    def _initiate_repayment(
        self, tax_id: str, destination: RepaymentDestination
    ) -> str:
        """Initiate a "Rückzahlungsantrag" for a specific tax number.

        We need to initiate a repayment as a first step, which allows us
        to extract the "COID" from the reponse HTML. This ID is required
        for the subsequent step of handing in the repayment request.
        """

        form_data = {
            "stnr": tax_id,
            "artRz": destination.value,
            "submit": "Weiter",
        }

        return self._session.post(
            url=FonURL.SERVICE_REPAYMENT_START,
            data=form_data,
        )

    def _extract_coid(self, html: str) -> str:
        """Extract the COID from the response HTML."""

        soup = bs4.BeautifulSoup(html, "html.parser")

        try:
            form_submit_element = soup.find("form", attrs={"id": "command"})
            action_str = form_submit_element.get("action")

            match = self.COID_RE_PATTERN.search(action_str)
            if match:
                return match.group(1)
        except Exception as exc:
            raise RepaymentRequestError(
                "Unable to extract COID from response HTML."
            ) from exc

    def _create_draft(
        self,
        coid: str,
        recipients: list[RepaymentRecipient],
    ) -> None:
        """Create a draft for the "Rückzahlungsantrag" using the COID."""

        form_data = {
            "speichern": "Speichern",
        }

        form_data.update(self._get_recipients_form_data(recipients))

        params = {"coid": coid}

        res = self._session.post(
            url=FonURL.SERVICE_REPAYMENT_SUBMIT,
            params=params,
            data=form_data,
        )

        self._validate_successful_repayment(res.text)

    def _get_recipients_form_data(
        self, recipients: list[RepaymentRecipient]
    ) -> dict[str, str]:
        """Get the recipients form data for the repayment request."""

        form_data = {}

        # If there are less than 3 recipients, we need to add empty ones
        # to the form data. Otherwise, the request will fail.
        if len(recipients) < 3:
            for _ in range(3 - len(recipients)):
                recipients.append(RepaymentRecipient())
        elif len(recipients) > 3:
            raise ValueError("Maximum of 3 repayment recipients allowed.")

        # Merge the form data representations of all recipients.
        for idx, r in enumerate(recipients):
            form_data.update(r.get_form_data(recipient_id=idx))

        return form_data

    def _validate_successful_repayment(self, html: str) -> None:
        """Validate the response of the repayment request.

        If the request was successful, the response will contain a
        success message. If the success message is not present, an
        error will be raised.
        """

        try:
            soup = bs4.BeautifulSoup(html, "html.parser")

            form_submit_element = soup.find("div", attrs={"id": "fon-pinfo"})
            text = form_submit_element.get_text()

            match = self.REPAYMENT_SUCCESS_RE_PATTERN.search(text)
            if not match:
                raise RepaymentRequestError(
                    "Failed to detect success message after repayment request."
                )
        except Exception as exc:
            raise RepaymentRequestError(
                "Failed to validate repayment request response."
            ) from exc

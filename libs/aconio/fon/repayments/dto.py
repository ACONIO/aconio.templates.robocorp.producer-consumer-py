"""Repayment API data transfer object."""
import re
import enum
import pydantic

import aconio.utils

# Strip chars FinanzOnline rejects (e.g. ' " < > Ù Ú). Allow-list; widen if
# FON rejects a legit character.
_FINON_DISALLOWED_RE = re.compile(r"[^A-Za-z0-9ÄÖÜäöüß \-./,()&]")


def _sanitize_finon_text(value: str | None) -> str | None:
    """Strip characters FinanzOnline does not accept in text fields."""
    if value is None:
        return None
    return _FINON_DISALLOWED_RE.sub("", value)

class RepaymentDestination(enum.StrEnum):
    """Repayment destination for a FinanzOnline repayment request."""

    DOMESTIC = "I"
    """Destination "Inland"."""

    FOREIGN = "A"
    """Destination "Ausland"."""


class BaseDTO(pydantic.BaseModel):
    """Base class for DTOs with common configuration."""

    model_config = pydantic.ConfigDict(extra="forbid")


class BankDetails(BaseDTO):
    """Bank details for a "FinanzOnline Rückzahlungsantrag" recipient."""

    iban: str
    bic: str | None = None


class RepaymentRecipient(BaseDTO):
    """Details for a "FinanzOnline Rückzahlungsantrag" recipient.

    Note:
    Values withint this class can be `None`, so an empty recipient
    is valid. This is useful because FinanzOnline always requires
    a full list of recipients, even if only one recipient is
    specified.
    """

    name: str | None = None
    amount: float | None = None
    bank_details: BankDetails | None = None

    _is_cash: bool = False

    @property
    def is_cash(self) -> str:
        return "B" if self._is_cash else "U"

    @is_cash.setter
    def is_cash(self, value: bool) -> None:
        self._is_cash = value

    def get_form_data(self, recipient_id: str) -> dict[str, str]:
        """Get the form data representation for this recipient.

        The form data representation of the recipient is useful
        for submitting repayment requests to FinanzOnline.

        Keys are formatted as `empfaenger[<recipient_id>].<field_name>`.

        **Example:**
        ```python
        {
            "empfaenger[1].name": "John Doe",
            "empfaenger[1].betrag": "100,00",
            "empfaenger[1].land": "",
            "empfaenger[1].iban": "AT611904300234573201",
            "empfaenger[1].bic": "BKAUATWW",
            "empfaenger[1].bar": "U",
            "empfaenger[1].bankname": "",
            "empfaenger[1].plz": "",
            "empfaenger[1].adresse": "",
        }
        ```
        """

        prefix = f"empfaenger[{recipient_id}]"

        iban = self.bank_details.iban if self.bank_details else ""
        bic = self.bank_details.bic if self.bank_details else ""

        return {
            f"{prefix}.name": _sanitize_finon_text(self.name) or "",
            f"{prefix}.betrag": self._get_str_amount(),
            f"{prefix}.land": self._get_destination_country() or "",
            f"{prefix}.iban": iban,
            f"{prefix}.bic": bic or "",
            f"{prefix}.bar": str(self.is_cash).upper(),
            f"{prefix}.bankname": "",
            f"{prefix}.plz": "",
            f"{prefix}.adresse": "",
        }

    def _get_str_amount(self) -> str:
        """Get the amount as a string formatted for FinanzOnline."""

        if self.amount is None:
            return ""

        amount_str = aconio.utils.to_german_currency_string(
            number=self.amount, show_currency_symbol=False
        )

        # FinanzOnline expects the amount without thousand separators,
        # so we remove the dot if it exists.
        return amount_str.replace(".", "")

    def _get_destination_country(self) -> str | None:
        """Get the destination country code for the recipient.

        If the IBAN starts with "AT", which indicates an Austrian
        bank account, return `None`. This is because FinanzOnline
        does not require a country code for domestic payments.

        Otherwise, return the first two characters of the IBAN.
        """

        if not self.bank_details:
            return None

        country_code = self.bank_details.iban[:2]

        if country_code.lower() == "at":
            # If the IBAN starts with "AT", it is an Austrian bank account,
            # so we return None for domestic payments.
            return None

        # The space is required by FinanzOnline.
        return country_code.upper() + " "

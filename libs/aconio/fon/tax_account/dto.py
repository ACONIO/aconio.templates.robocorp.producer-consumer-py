"""Tax account data transfer object."""

import pydantic


class TaxAccount(pydantic.BaseModel):
    """Represent a "FinanzOnline Steuerkonto"."""

    balance: float | None = None
    """Tax account "Endsaldo"."""

    balance_date: str | None = None
    """Tax account "Endsaldo Stand"."""

    tax_id: str | None = None
    """Tax account "Steuernummer"."""

    finanzamt_number: str | None = None
    """Tax account "Finanzamt Nummer"."""

    postings: list[dict] | None = None
    """Tax account "Buchungen" table."""

    payment_plan: list[dict] | None = None
    """Tax account "Zahlungsplan" table."""

    repayments: list[dict] | None = None
    """Tax account "Rückzahlungen" table."""

    prepayments: list[dict] | None = None
    """Tax account "Vorauszahlungen/Veranlagungen" table."""

    quarterly_amounts: list[dict] | None = None
    """Tax account "Vierteljahresbeträge" table."""

    arrears: list[dict] | None = None
    """Tax account "Rückstandsaufgliederung" table."""

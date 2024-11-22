"""Retrieve and set client data."""

import os
import re
import pydantic

import aconio.db as db
import aconio.core.utils as utils

from enum import StrEnum

__all__ = [
    "ContactPersonType",
    "Client",
    "set_salutation",
    "set_display_email",
    "set_client_by_addresstype",
    "set_client_contact_person",
]


class ContactPersonType(StrEnum):
    PERSONAL = "PERSONAL"
    PROFESSIONAL = "PROFESSIONAL"


class Client(pydantic.BaseModel):
    """Represent the client for which to process the BMD 'Frist'."""

    model_config = pydantic.ConfigDict(coerce_numbers_to_str=True)

    bmd_id: str
    """
    Equivalent to the BMD DB field `PER_PERSONENID`. Example: `KL2000201001`.
    """

    bmd_number: str
    """
    Equivalent to the BMD DB field `PER_PERSONENNR`. Example: `201001`.
    """

    bmd_company_id: str
    """Equivalent to the BMD DB field `PER_FIRMENNR`."""

    bmd_tax_company_id: str
    """
    Equivalent to the BMD DB field `KLI_QUOTEN_FIRMENNR`. Better known as the
    'STB-Firma' field in the "Kunden-Stammdaten".
    """

    first_name: str | None = None
    """
    Equivalent to the BMD DB field `PER_VORNAME`. In case of a company, this
    field is `None`.
    """

    last_name: str
    """Equivalent to the BMD DB field `PER_NAME`."""

    language: str | None = None
    """Equivalent to the BMD DB field `ADR_SPRACHNR`."""

    tax_number: str | None = None
    """
    The "Steuernummer" of the client. Equivalent to the BMD DB field
    `PER_FSTEUERNR`.
    """

    salutation: str | None = None
    """Salutation extracted from BMD, based on the process config."""

    emails: list[str] | None = None
    """E-Mail addresses extracted from BMD, based on the process config."""

    employees: list[str] | None = None
    """A List of responsible employees for the client."""

    @property
    def language_iso(self) -> str:
        match str(self.language):
            case "4":
                return "en"
            case _:
                return "de"

    @property
    def full_name(self) -> str:
        return utils.filter_none_and_join([self.first_name, self.last_name])

    @property
    def emails_str(self) -> str:
        """Return client e-mail addresses as a semicolon separated string."""
        if self.emails is None:
            return ""

        return ";".join(self.emails)

    @property
    def parsed_tax_number(self) -> str:
        """Tax number without any special chars.

        Can be used for FinanzOnline "Steuerkonto" queries.

        Steps:
            - Remove all '/'.
            - Remove all white spaces.
            - Remove the '-' and everything after it.
                Some contain a '-' at the end, followed by validation number.
            - Remove numbers in brackets and the brackets itself.
                Some contain the validation number in brackets.
        """
        client_tax_id = (
            self.tax_number.replace("/", "").replace(" ", "").partition("-")[0]
        )

        return re.sub(r"\(.*\)", "", client_tax_id)


def set_salutation(
    bmddb: db.MSSQLConnection,
    client: Client,
    default_salutation: str,
    bmd_freifeld: str | None = None,
) -> Client:
    """Set client salutation and return client object."""

    client.salutation = default_salutation

    if bmd_freifeld:
        path = os.path.join(
            os.path.dirname(__file__),
            "queries/client/get_salutation_freifeld.sql",
        )
        salutations = bmddb.execute_query_from_file(
            sql_filepath=path,
            salutation_bmd_freifeld=bmd_freifeld,
            client_bmd_id=client.bmd_id,
            client_bmd_company_id=client.bmd_company_id,
        )
        client.salutation = salutations[0].get("salutation")

    return client


def set_display_email(
    bmddb: db.MSSQLConnection,
    client: Client,
) -> Client:
    """Set emails of client and return client object."""

    path = os.path.join(
        os.path.dirname(__file__),
        "queries/client/get_display_email.sql",
    )
    rows = bmddb.execute_query_from_file(
        sql_filepath=path,
        client_bmd_id=client.bmd_id,
        client_bmd_company_id=client.bmd_company_id,
    )

    if rows:
        client.emails = [rows[0].get("display_email")]

    return client


def set_client_by_addresstype(
    bmddb: db.MSSQLConnection,
    client: Client,
    addresstype: str,
) -> Client:
    """Set emails of client and return client object."""

    rows = _query_email_by_adressart(
        bmddb=bmddb, client=client, email_address_type=addresstype
    )
    if rows:
        client.emails = [r["email"] for r in rows]

    return client


def set_client_contact_person(
    bmddb: db.MSSQLConnection,
    client: Client,
    contact_person_type: ContactPersonType,
    contact_person_identifier: str | None = None,
) -> Client:
    """Return the client with the clients contactperson."""

    cps = _query_contact_persons(
        bmddb=bmddb,
        client=client,
        contact_person_type=contact_person_type,
        contact_person_identifier=contact_person_identifier,
    )
    client.emails = [cp.get("email") for cp in cps]

    # If one of the contact persons has no salutation defined, set the
    # full client salutation to None, since this should result in an error
    salutations = [cp.get("salutation") for cp in cps]
    if None in salutations:
        client.salutation = None
    else:
        client.salutation = ",<br>".join(salutations)

    return client


def _query_contact_persons(
    bmddb: db.MSSQLConnection,
    client: Client,
    contact_person_type: ContactPersonType,
    contact_person_identifier: str | None,
) -> list[dict]:
    """Retrieve the contact person of the given `client.bmd_id`."""

    if contact_person_identifier:
        path = os.path.join(
            os.path.dirname(__file__),
            "queries/client/get_cp_by_identifier.sql",
        )
        rows = bmddb.execute_query_from_file(
            sql_filepath=path,
            client_bmd_id=client.bmd_id,
            client_bmd_company_id=client.bmd_company_id,
            identifier=contact_person_identifier,
        )
    else:
        path = os.path.join(
            os.path.dirname(__file__),
            "queries/client/get_cp_main.sql",
        )
        rows = bmddb.execute_query_from_file(
            sql_filepath=path,
            client_bmd_id=client.bmd_id,
            client_bmd_company_id=client.bmd_company_id,
        )

    cps = []
    for row in rows:
        salutation, name = None, None
        match contact_person_type:
            # Use BMD personal salutation followed by the clients first name
            # without titles (e.g. "Lieber Max")
            case ContactPersonType.PERSONAL:
                if salutation := row.get("salutation_personal"):
                    salutation = salutation.rstrip(", ")
                name = row["first_name"]

            # Use BMD professional salutation followed by the clients titles
            # and last name (e.g. "Sehr geehrter Herr Mag. Mustermann")
            case ContactPersonType.PROFESSIONAL:
                if salutation := row.get("salutation_professional"):
                    salutation = salutation.rstrip(", ")

                # if last name is None, titles are also ignored, otherwise
                # construct the full name with title prefix and suffix
                if last_name := row["last_name"]:
                    name_positions = []
                    if title_prefix := row["title_prefix"]:
                        name_positions.append(title_prefix.strip())

                    name_positions.append(last_name)

                    if title_suffix := row["title_suffix"]:
                        name_positions.append(title_suffix.strip())

                    name = " ".join(name_positions)

        cp = {"email": row["email"], "salutation": None}

        # if either the salutation or the name is None, the full salutation
        # should also be None
        full_salutation = [salutation, name]
        if None not in full_salutation:
            cp["salutation"] = " ".join([i.strip() for i in full_salutation])

        cps.append(cp)

    return cps


def _query_email_by_adressart(
    bmddb: db.MSSQLConnection,
    client: Client,
    email_address_type: str,
) -> list[dict]:
    """Retrieve the email of the given `client.bmd_id` with an addresstype."""

    path = os.path.join(
        os.path.dirname(__file__),
        "queries/client/get_client_email_by_adressart.sql",
    )
    return bmddb.execute_query_from_file(
        sql_filepath=path,
        client_bmd_id=client.bmd_id,
        email_address_type=email_address_type,
        client_bmd_company_id=client.bmd_company_id,
    )

"""Data access objects (DAO) for BMD-related data."""

import re
import enum
import pydantic

import aconio.db
import aconio.utils
import aconio.bmd.dao.queries as queries


class BMDSachbearbeiter(enum.StrEnum):
    HAUPT = "HAUPT"
    """"Sachbearbeiter" of a client."""

    FRIST = "FRIST"
    """"Sachbearbeiter" associated with "Frist"."""


class EmployeeSelectionMode(enum.StrEnum):
    ALWAYS_APPEND_SB = "ALWAYS_APPEND_SB"
    """Append responsible employees and "Sachbearbeiter"."""

    FALLBACK_TO_SB = "FALLBACK_TO_SB"
    """Append "Sachbearbeiter" only if no responsible employees are found."""

    SB_ONLY = "SB_ONLY"
    """Append "Sachbearbeiter". Ignore responsible employees."""


class Employee(pydantic.BaseModel):
    """Represent the employee responsible for the client."""

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

    email: str | None = None
    """E-Mail address extracted from BMD, based on the process config."""


def filter_duplicate_employees(employees: list[Employee]) -> list[Employee]:
    return list({e.bmd_id: e for e in employees}.values())


class ContactPersonType(enum.StrEnum):
    PERSONAL = "PERSONAL"
    """
    Use BMD personal salutation followed by the clients first name
    without titles (e.g. "Lieber Max").
    """

    PROFESSIONAL = "PROFESSIONAL"
    """
    Use BMD professional salutation followed by the clients titles
    and last name (e.g. "Sehr geehrter Herr Mag. Mustermann").
    """


class ContactPerson(pydantic.BaseModel):
    """Represent a contact person of a client."""

    model_config = pydantic.ConfigDict(coerce_numbers_to_str=True)

    client_id: str
    last_name: str | None
    first_name: str | None
    title_prefix: str | None
    title_suffix: str | None
    email: str | None
    salutation_personal: str | None
    salutation_professional: str | None
    identifier: str | None

    def name(self, contact_person_type: ContactPersonType) -> str | None:
        """Return the name of the contact person given the type."""
        match contact_person_type:
            case ContactPersonType.PERSONAL:
                return self.first_name
            case ContactPersonType.PROFESSIONAL:
                # If last name is None, titles are also ignored, otherwise
                # construct the full name with title prefix and suffix.
                if last_name := self.last_name:
                    name_positions = []
                    if title_prefix := self.title_prefix:
                        name_positions.append(title_prefix.strip())

                    name_positions.append(last_name)

                    if title_suffix := self.title_suffix:
                        name_positions.append(title_suffix.strip())

                    return " ".join(name_positions)

    def salutation_prefix(
        self, contact_person_type: ContactPersonType
    ) -> str | None:
        """Return the salutation of the contact person given the type."""
        match contact_person_type:
            case ContactPersonType.PERSONAL:
                if self.salutation_personal:
                    return self.salutation_personal.rstrip(", ")
            case ContactPersonType.PROFESSIONAL:
                if self.salutation_professional:
                    return self.salutation_professional.rstrip(", ")

    def salutation(self, contact_person_type: ContactPersonType) -> str | None:
        """Return salutation given the type.

        If either `salutation_prefix()` or `name()` is None, the combined
        salutation is also None.
        """
        full_salutation = [
            self.salutation_prefix(contact_person_type),
            self.name(contact_person_type),
        ]

        if None not in full_salutation:
            return " ".join([i.strip() for i in full_salutation]).rstrip(", ")


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
    field is None.
    """

    name: str
    """Equivalent to the BMD DB field `PER_NAME`."""

    title_prefix: str | None
    """Equivalent to the BMD DB field `PER_TITEL`."""

    title_suffix: str | None
    """Equivalent to the BMD DB field `PER_TITEL_HINTEN`."""

    language: str | None = None
    """Equivalent to the BMD DB field `ADR_SPRACHNR`."""

    tax_number: str | None = None
    """
    The "Steuernummer" of the client. Equivalent to the BMD DB field
    `PER_FSTEUERNR`.
    """

    iban: str | None = None
    """IBAN of the client."""

    bic: str | None = None
    """BIC of the client."""

    additional_name: str | None = None
    """Equivalent to the BMD DB field `PER_ZUSATZNAME`."""

    salutation: str | None = None
    """Salutation extracted from BMD, based on the process config."""

    emails: list[str] | None = None
    """E-Mail addresses extracted from BMD, based on the process config."""

    employees: list[Employee] = []
    """The responsible employees for the client."""

    @property
    def language_iso(self) -> str:
        match str(self.language):
            case "4":
                return "en"
            case _:
                return "de"

    @property
    def last_name(self) -> str:
        return aconio.utils.filter_none_and_join(
            [self.name, self.additional_name]
        )

    @property
    def full_name(self) -> str:
        """Return the full name of the client, including titles."""
        return aconio.utils.filter_none_and_join(
            [
                self.title_prefix,
                self.first_name,
                self.last_name,
                self.title_suffix,
            ]
        )

    @property
    def emails_str(self) -> str:
        """Return client e-mail addresses as a semicolon separated string."""
        if not self.emails:
            return ""

        return ";".join(self.emails)

    @property
    def parsed_tax_number(self) -> str:
        """Tax number without any special chars.

        - Removes each `/` and whitespaces.
        - Removes `-` and the validation number that follows (e.g. `-42`).
        - Removes numbers in brackets and the brackets itself (e.g. `(42)`).
        """
        client_tax_id = (
            self.tax_number.replace("/", "").replace(" ", "").partition("-")[0]
        )

        return re.sub(r"\(.*\)", "", client_tax_id)

    @property
    def employee_emails(self) -> list[str]:
        """Return all employee e-mails as a list of strings."""
        return [e.email for e in self.employees if e.email]


class ClientDAO:
    """DAO for client data."""

    def __init__(self, conn: aconio.db.BaseConnection):
        self._conn = conn

    def with_ids(
        self, client_bmd_id: str, client_bmd_company_id: str
    ) -> Client:
        """Return client given its respective BMD ids."""
        return queries.client_with_ids(
            conn=self._conn,
            client_bmd_id=client_bmd_id,
            client_bmd_company_id=client_bmd_company_id,
        )

    def from_frist(self, bmd_frist_id: str) -> Client:
        """Return client associated with "Frist"."""
        return queries.client_from_frist(
            conn=self._conn, bmd_frist_id=bmd_frist_id
        )

    def set_salutation(
        self,
        client: Client,
        default_salutation: str | None = None,
        bmd_freifeld: str | None = None,
    ):
        """Set client salutation.

        Given an invalid `bmd_freifeld`, the salutation may be None even if a
        default salutation is provided.
        """
        client.salutation = default_salutation

        if bmd_freifeld:
            freifeld_salutation = queries.salutation_freifeld(
                conn=self._conn,
                client_bmd_id=client.bmd_id,
                client_bmd_company_id=client.bmd_company_id,
                bmd_freifeld=bmd_freifeld,
            )
            if freifeld_salutation:
                client.salutation = freifeld_salutation

        if client.salutation:
            client.salutation = client.salutation.rstrip(", ")

    def set_emails_to_display(self, client: Client):
        """Set emails of client to its `PER_DISPLAY_EMAIL`."""
        client.emails = queries.display_email(
            conn=self._conn,
            client_bmd_id=client.bmd_id,
            client_bmd_company_id=client.bmd_company_id,
        )

    def set_emails_by_addresstype(self, client: Client, addresstype: str):
        """Set emails of client given its addresstype."""
        client.emails = queries.email_by_adressart(
            bmddb=self._conn,
            client_bmd_id=client.bmd_id,
            client_bmd_company_id=client.bmd_company_id,
            email_address_type=addresstype,
        )

    def set_by_contact_person(
        self,
        client: Client,
        contact_person_type: ContactPersonType,
        contact_person_identifier: str | None = None,
        salutation_separator: str = ",<br>",
        default_salutation: str | None = None,
    ):
        """Set the email and salutation provided given its contact person."""
        cps: list[ContactPerson] = []
        if contact_person_identifier:
            cps = queries.cp_by_identifier(
                conn=self._conn,
                client_bmd_id=client.bmd_id,
                client_bmd_company_id=client.bmd_company_id,
                contact_person_identifier=contact_person_identifier,
            )
        else:
            cps = queries.cp_main(
                conn=self._conn,
                client_bmd_id=client.bmd_id,
                client_bmd_company_id=client.bmd_company_id,
            )

        emails, salutations = [], []
        for cp in cps:
            emails.append(cp.email)
            salutations.append(cp.salutation(contact_person_type))

        # If one of the contact persons has no email or salutation
        # defined, set the whole salutation / email list to empty / None
        # to indicate an error.
        if None in emails:
            client.emails = []
        else:
            client.emails = emails

        if None in salutations:
            client.salutation = default_salutation
        else:
            client.salutation = salutation_separator.join(salutations)

    def set_employees(
        self,
        client: Client,
        bmd_frist_id: str | None,
        bmd_sachbearbeiter: BMDSachbearbeiter,
        append_mode: EmployeeSelectionMode,
        bmd_responsible_areas: list[str] | None = None,
    ):
        """Set the employees of the client."""
        responsibles = []
        if bmd_responsible_areas:
            responsibles = queries.responsible_employees(
                bmddb=self._conn,
                client_bmd_id=client.bmd_id,
                client_bmd_company_id=client.bmd_company_id,
                bmd_responsible_areas=bmd_responsible_areas,
            )

        sb = None
        match bmd_sachbearbeiter:
            case BMDSachbearbeiter.FRIST:
                sb = queries.frist_employee(
                    bmddb=self._conn, bmd_frist_id=bmd_frist_id
                )
            case BMDSachbearbeiter.HAUPT:
                sb = queries.sachbearbeiter_of_client(
                    bmddb=self._conn,
                    client_bmd_id=client.bmd_id,
                    client_bmd_company_id=client.bmd_company_id,
                )

        employees = []
        match append_mode:
            case EmployeeSelectionMode.SB_ONLY:
                if sb:
                    employees.append(sb)
            case EmployeeSelectionMode.ALWAYS_APPEND_SB:
                employees.extend(responsibles)
                if sb:
                    employees.append(sb)
            case EmployeeSelectionMode.FALLBACK_TO_SB:
                employees.extend(responsibles)

                if not employees and sb:
                    employees.append(sb)

        client.employees = filter_duplicate_employees(employees)

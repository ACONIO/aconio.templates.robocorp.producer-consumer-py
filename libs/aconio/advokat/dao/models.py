"""Data models for the Advokat DAO."""

import pydantic
import datetime


class ExecutionPermit(pydantic.BaseModel):
    """Execution permit ("Exekutionsbewilligung")."""

    name: str
    date: datetime.date


class VBDocument(pydantic.BaseModel):
    """Enforcement report document ("Vollzugsbericht")."""

    name: str
    date: datetime.date


class Service(pydantic.BaseModel):
    """A service ("Leistung") entry in an Advokat act."""

    name: str
    date: datetime.date
    type: str


class VVZDocument(pydantic.BaseModel):
    """Asset register document ("Vermögensverzeichnis")."""

    subject: str | None = None
    date: datetime.date | None = None
    employee: str | None = None


class Opponent(pydantic.BaseModel):
    """Advokat act opponent ("Gegner")."""

    first_name: str | None = None
    last_name: str | None = None
    dob: datetime.date | None = None

    address: str | None = None
    city: str | None = None
    zip_code: str | None = None

    is_primary: bool
    """Whether the opponent is the primary opponent of the act."""

    @property
    def name(self) -> str:
        """Get the full name of the opponent."""
        parts = []
        if self.first_name:
            parts.append(self.first_name)
        if self.last_name:
            parts.append(self.last_name)
        return " ".join(parts)


class Court(pydantic.BaseModel):
    """Advokat court ("Gericht")."""

    name: str
    address: str | None = None
    city: str | None = None
    zip_code: str | None = None


class Act(pydantic.BaseModel):
    """Advokat act information relevant for the process."""

    number: int
    """Advokat act number ("ANr")."""

    short_name: str
    """Advokat act shortname ("AKurz")."""

    status: str | None = None
    """Advokat act status."""

    completion_date: datetime.date | None = None
    """Date when the act was completed (if applicable)."""

    case_number: str | None = None
    """Advokat case number ("Geschäftszahl")."""

    court: Court | None = None
    """Court associated with the act."""

    debtor_payments: list[datetime.date] = []
    """Dates when payments were made from the "Schuldner"."""

    execution_permits: list[ExecutionPermit] = []

    vb_documents: list[VBDocument] = []
    """
    Existing 'Vollzugsbericht' documents for the act.
    
    Note: This does not include the actual 'Vollzugsbericht' read from
    the ERV data and stored in the act during this process.
    """

    vvz_documents: list[VVZDocument] = []
    """
    Existing 'Vermögensverzeichnis' documents for the act.
    """

    opponents: list[Opponent] = []
    """Opponents associated with the act."""

    services: list[Service] = []
    """Services ("Leistungen") associated with the act."""

    @property
    def primary_opponent(self) -> Opponent | None:
        """Get the primary opponent of the act, if any."""
        return next(filter(lambda o: o.is_primary, self.opponents), None)

    @property
    def latest_vvz(self) -> VVZDocument | None:
        """Get the latest 'Vermögensverzeichnis' document, if any."""
        if not self.vvz_documents:
            return None

        # First, filter out VVZ documents without a date.
        dated_vvzs = [v for v in self.vvz_documents if v.date is not None]

        if not dated_vvzs:
            return None

        return max(dated_vvzs, key=lambda v: v.date)


class ERVMessage(pydantic.BaseModel):
    """Advokat ERV message."""

    erv_id: int
    """Advokat ERV message ID."""

    act_number: int
    """Advokat act number associated with the ERV message."""

    date: datetime.date
    """Date of the ERV message."""

    completed_date: datetime.date | None = None
    """Date when the ERV message was completed (if applicable)."""

    zip_path: str
    """Path to the ERV data zip (".E") file (without the base path)."""

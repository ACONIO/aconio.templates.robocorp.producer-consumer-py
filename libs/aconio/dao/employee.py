"""Retrieve and set employee data."""

import os
import pydantic

from enum import StrEnum

import aconio.db as db
import aconio.dao.client as _client

__all__ = [
    "BMDSachbearbeiter",
    "EmployeeAppendMode",
    "Employee",
    "set_employees",
]


class BMDSachbearbeiter(StrEnum):
    HAUPT = "HAUPT"
    FRIST = "FRIST"


class EmployeeAppendMode(StrEnum):
    APPEND = "APPEND"
    FALLBACK = "FALLBACK"
    DEFAULT = "DEFAULT"


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


def set_employees(
    bmddb: db.MSSQLConnection,
    client: _client.Client,
    bmd_sachbearbeiter: BMDSachbearbeiter,
    append_mode: EmployeeAppendMode,
    bmd_responsible_areas: list[str] | None = None,
    employees: list[Employee] = None,
):
    """Set the responsible employee for the client and return client object."""

    sb = None
    employees = []
    responsibles = []

    if bmd_responsible_areas:
        rows = _query_responsible_employees(
            bmddb=bmddb,
            client_bmd_id=client.bmd_id,
            client_bmd_company_id=client.bmd_company_id,
            bmd_responsible_areas=bmd_responsible_areas,
        )

        responsibles = [Employee(**r) for r in rows]

    match bmd_sachbearbeiter:
        case BMDSachbearbeiter.HAUPT:
            row = _query_client_sachbearbeiter(
                bmddb=bmddb,
                client_bmd_id=client.bmd_id,
                client_bmd_company_id=client.bmd_company_id,
            )

            if row:
                sb = Employee(**row)

        case BMDSachbearbeiter.FRIST:
            # At this point, the item should only contain one employee from
            # the initial "Fristen" query.
            sb = employees[0]

    match append_mode:
        case EmployeeAppendMode.DEFAULT:
            if sb:
                employees.append(sb)
        case EmployeeAppendMode.APPEND:
            employees.extend(responsibles)
            if sb:
                employees.append(sb)
        case EmployeeAppendMode.FALLBACK:
            employees.extend(responsibles)

            if not employees and sb:
                employees.append(sb)

    client.employees = _filter_duplicate_employees(employees)

    return client


def _filter_duplicate_employees(employees: list[Employee]) -> list[Employee]:
    """Remove duplicate employees from list of employees."""
    return list({e.bmd_id: e for e in employees}.values())


def _query_responsible_employees(
    bmddb: db.MSSQLConnection,
    client_bmd_id: str,
    client_bmd_company_id: str,
    bmd_responsible_areas: list[str],
):
    """Retrieve the client's responsible employee."""

    path = os.path.join(
        os.path.dirname(__file__),
        "queries/employee/get_responsible_employees.sql",
    )
    return bmddb.execute_query_from_file(
        sql_filepath=path,
        client_bmd_id=client_bmd_id,
        client_bmd_company_id=client_bmd_company_id,
        responsible_areas=",".join(
            ["'" + i + "'" for i in bmd_responsible_areas]
        ),
    )


def _query_client_sachbearbeiter(
    bmddb: db.MSSQLConnection, client_bmd_id: str, client_bmd_company_id: str
):
    """Retrieve the client's "Sachbearbeiter" from the BMD DB."""

    path = os.path.join(
        os.path.dirname(__file__),
        "queries/employee/get_sachbearbeiter_of_client.sql",
    )
    rows = bmddb.execute_query_from_file(
        sql_filepath=path,
        client_bmd_id=client_bmd_id,
        client_bmd_company_id=client_bmd_company_id,
    )

    if rows:
        return rows[0]

    return None

"""Functions that execute SQL queries."""

from __future__ import annotations

import os

import aconio.db as db
import aconio.dao.client as client


def full_path(file: str) -> str:
    return os.path.join(os.path.dirname(__file__), file)


def client_with_ids(
    conn: db.BaseConnection,
    client_bmd_id: str,
    client_bmd_company_id: str,
) -> client.Client | None:
    sql_filepath = full_path("queries/client/client_with_ids.sql")
    rows = conn.execute_query_from_file(
        sql_filepath=sql_filepath,
        client_bmd_id=client_bmd_id,
        client_bmd_company_id=client_bmd_company_id,
    )

    if rows:
        return client.Client(**rows[0])


def client_from_frist(
    conn: db.BaseConnection, bmd_frist_id: str
) -> client.Client | None:
    sql_filepath = full_path("queries/client/client_from_frist.sql")
    rows = conn.execute_query_from_file(
        sql_filepath=sql_filepath, bmd_frist_id=bmd_frist_id
    )

    if rows:
        return client.Client(**rows[0])


def salutation_freifeld(
    conn: db.BaseConnection,
    client_bmd_id: str,
    client_bmd_company_id: str,
    bmd_freifeld: str | None = None,
) -> str | None:
    sql_filepath = full_path("queries/client/salutation_freifeld.sql")
    rows = conn.execute_query_from_file(
        sql_filepath=sql_filepath,
        salutation_bmd_freifeld=bmd_freifeld,
        client_bmd_id=client_bmd_id,
        client_bmd_company_id=client_bmd_company_id,
    )

    if rows:
        return rows[0].get("salutation")


def display_email(
    conn: db.BaseConnection, client_bmd_id: str, client_bmd_company_id: str
) -> list[str]:
    sql_filepath = full_path("queries/client/display_email.sql")
    rows = conn.execute_query_from_file(
        sql_filepath=sql_filepath,
        client_bmd_id=client_bmd_id,
        client_bmd_company_id=client_bmd_company_id,
    )

    if rows:
        return [r.get("display_email") for r in rows if r.get("display_email")]

    return []


def cp_by_identifier(
    conn: db.BaseConnection,
    client_bmd_id: str,
    client_bmd_company_id: str,
    contact_person_identifier: str | None,
) -> list[client.ContactPerson]:
    sql_filepath = full_path("queries/client/cp_by_identifier.sql")
    rows = conn.execute_query_from_file(
        sql_filepath=sql_filepath,
        client_bmd_id=client_bmd_id,
        client_bmd_company_id=client_bmd_company_id,
        identifier=contact_person_identifier,
    )

    if rows:
        return [client.ContactPerson(**r) for r in rows]

    return []


def cp_main(
    conn: db.BaseConnection, client_bmd_id: str, client_bmd_company_id: str
) -> list[client.ContactPerson]:
    sql_filepath = full_path("queries/client/cp_main.sql")
    rows = conn.execute_query_from_file(
        sql_filepath=sql_filepath,
        client_bmd_id=client_bmd_id,
        client_bmd_company_id=client_bmd_company_id,
    )

    if rows:
        return [client.ContactPerson(**r) for r in rows]

    return []


def email_by_adressart(
    bmddb: db.BaseConnection,
    client_bmd_id: str,
    client_bmd_company_id: str,
    email_address_type: str,
) -> list[dict]:
    """Retrieve the email of the given `client.bmd_id` with an addresstype."""

    sql_filepath = full_path("queries/client/client_email_by_adressart.sql")
    rows = bmddb.execute_query_from_file(
        sql_filepath=sql_filepath,
        client_bmd_id=client_bmd_id,
        client_bmd_company_id=client_bmd_company_id,
        email_address_type=email_address_type,
    )

    if rows:
        return [r["email"] for r in rows]

    return []


def responsible_employees(
    bmddb: db.BaseConnection,
    client_bmd_id: str,
    client_bmd_company_id: str,
    bmd_responsible_areas: list[str],
) -> list[client.Employee]:
    """Retrieve the client's responsible employee."""
    sql_filepath = full_path("queries/employee/responsible_employees.sql")
    rows = bmddb.execute_query_from_file(
        sql_filepath=sql_filepath,
        client_bmd_id=client_bmd_id,
        client_bmd_company_id=client_bmd_company_id,
        responsible_areas=",".join(
            ["'" + i + "'" for i in bmd_responsible_areas]
        ),
    )

    if rows:
        return [client.Employee(**r) for r in rows]

    return []


def sachbearbeiter_of_client(
    bmddb: db.BaseConnection, client_bmd_id: str, client_bmd_company_id: str
) -> client.Employee | None:
    """Retrieve the client's "Sachbearbeiter" from the BMD DB."""
    sql_filepath = full_path("queries/employee/sachbearbeiter_of_client.sql")
    rows = bmddb.execute_query_from_file(
        sql_filepath=sql_filepath,
        client_bmd_id=client_bmd_id,
        client_bmd_company_id=client_bmd_company_id,
    )

    if rows:
        return client.Employee(**rows[0])


def frist_employee(
    bmddb: db.BaseConnection, bmd_frist_id: str
) -> client.Employee | None:
    sql_filepath = full_path("queries/employee/frist_employee.sql")
    rows = bmddb.execute_query_from_file(
        sql_filepath=sql_filepath, bmd_frist_id=bmd_frist_id
    )

    if rows:
        return client.Employee(**rows[0])

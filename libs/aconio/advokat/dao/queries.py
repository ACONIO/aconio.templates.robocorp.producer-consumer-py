"""Data access functions for the 'Advokat' module."""

import os
import datetime

import aconio.db
import aconio.advokat.dao as dao


def full_path(file: str) -> str:
    return os.path.join(os.path.dirname(__file__), file)


def get_erv_messages(
    db: aconio.db.MSSQLConnection,
    ss_type: str,
    ss_type_detailed: str,
    date: datetime.date | None = None,
    act_short_name: str | None = None,
    max_results: int | None = None,
) -> list[dao.ERVMessage]:
    """Obtain all ERV messages with the given 'Schriftsatz' type."""

    limit_clause = ""
    if max_results:
        limit_clause = f"TOP {max_results}"

    results = db.execute_query_from_file(
        sql_filepath=full_path("queries/get_erv_messages.sql"),
        limit_clause=limit_clause,
        ss_type=ss_type,
        ss_type_detailed=ss_type_detailed,
        date=date,
        act_short_name=act_short_name,
    )

    erv_messages = []
    for r in results:
        erv_messages.append(
            dao.ERVMessage(
                erv_id=r["erv_id"],
                act_number=r["act_number"],
                date=r["date"],
                completed_date=r["completed_date"],
                zip_path=r["erv_data_zip"],
            )
        )

    return erv_messages


def get_erv_message(
    db: aconio.db.MSSQLConnection, erv_id: int
) -> dao.ERVMessage:
    """Obtain a single ERV message by its ID."""

    results = db.execute_query_from_file(
        sql_filepath=full_path("queries/get_erv_message.sql"),
        erv_id=erv_id,
    )

    if len(results) == 0:
        raise ValueError(f"No ERV message found for ID {erv_id}!")
    elif len(results) > 1:
        raise ValueError(f"Multiple ERV messages found for ID {erv_id}!")

    r = results[0]

    return dao.ERVMessage(
        erv_id=r["erv_id"],
        act_number=r["act_number"],
        date=r["date"],
        completed_date=r["completed_date"],
        zip_path=r["erv_data_zip"],
    )


def get_act_by_number(
    db: aconio.db.MSSQLConnection, act_number: int
) -> dao.Act | None:
    """Get act information for a given act number."""

    results = db.execute_query_from_file(
        sql_filepath=full_path("queries/get_act_by_number.sql"),
        act_number=act_number,
    )

    if not results:
        return None

    if len(results) > 1:
        raise ValueError(f"Multiple acts found for act number {act_number}!")

    r = results[0]

    return dao.Act(
        number=r["act_number"],
        short_name=r["act_short_name"],
        case_number=r["case_number"],
        status=r["status"],
        completion_date=r["completion_date"],
    )


def get_act_court(
    db: aconio.db.MSSQLConnection, act_number: int
) -> dao.Court | None:
    """Get court information for a given act number."""

    results = db.execute_query_from_file(
        sql_filepath=full_path("queries/get_act_court.sql"),
        act_number=act_number,
    )

    if not results:
        return None

    if len(results) > 1:
        raise ValueError(f"Multiple courts found for act number {act_number}!")

    r = results[0]
    return dao.Court(
        name=r["name"],
        address=r["address"],
        city=r["city"],
        zip_code=r["zip_code"],
    )


def get_act_execution_permits(
    db: aconio.db.MSSQLConnection, act_number: int
) -> list[dao.ExecutionPermit]:
    """Get execution permits for a given act number."""

    results = db.execute_query_from_file(
        sql_filepath=full_path("queries/get_act_execution_permits.sql"),
        act_number=act_number,
    )

    permits = []
    for r in results:
        permits.append(
            dao.ExecutionPermit(
                name=r["name"],
                date=r["date"],
            )
        )

    return permits


def get_act_opponents(
    db: aconio.db.MSSQLConnection, act_number: int
) -> list[dao.Opponent]:
    """Get opponents for a given act number."""

    results = db.execute_query_from_file(
        sql_filepath=full_path("queries/get_act_opponents.sql"),
        act_number=act_number,
    )

    opponents = []
    for r in results:
        opponents.append(
            dao.Opponent(
                first_name=r["first_name"],
                last_name=r["last_name"],
                dob=r["dob"],
                address=r["address"],
                city=r["city"],
                zip_code=r["zip_code"],
                is_primary=r["is_primary"] == 1,
            )
        )

    return opponents


def get_act_payments(
    db: aconio.db.MSSQLConnection, act_number: int
) -> list[str]:
    """Get debtor payment dates for a given act number."""

    results = db.execute_query_from_file(
        sql_filepath=full_path("queries/get_act_payments.sql"),
        act_number=act_number,
    )

    payments = []
    for r in results:
        payments.append(r["date"])

    return payments


def get_act_services(
    db: aconio.db.MSSQLConnection, act_number: int
) -> list[dao.Service]:
    """Get services ("Leistungen") for a given act number."""

    results = db.execute_query_from_file(
        sql_filepath=full_path("queries/get_act_services.sql"),
        act_number=act_number,
    )

    services = []
    for r in results:
        services.append(
            dao.Service(
                name=r["name"],
                date=r["date"],
                type=r["type"],
            )
        )

    return services


def get_act_vb_docs(
    db: aconio.db.MSSQLConnection, act_number: int
) -> list[dao.VBDocument]:
    """Get 'Vollzugsbericht' documents for a given act number."""

    results = db.execute_query_from_file(
        sql_filepath=full_path("queries/get_act_vb_docs.sql"),
        act_number=act_number,
    )

    vbs = []
    for r in results:
        vbs.append(
            dao.VBDocument(
                name=r["name"],
                date=r["date"],
            )
        )

    return vbs


def get_act_vvz_docs(
    db: aconio.db.MSSQLConnection, act_number: int
) -> list[dao.VVZDocument]:
    """Get 'Vermögensverzeichnis' documents for a given act number."""

    results = db.execute_query_from_file(
        sql_filepath=full_path("queries/get_act_vvz_docs.sql"),
        act_number=act_number,
    )

    vvzs = []
    for r in results:
        vvzs.append(
            dao.VVZDocument(
                subject=r["subject"],
                employee=r["employee"],
                date=r["date"],
            )
        )

    return vvzs

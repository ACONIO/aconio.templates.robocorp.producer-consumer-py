"""Interactions with BMD services ('Leistungen')."""

import os
import csv
import time
import pydantic

from typing import Annotated
from datetime import datetime

from aconio.bmd._config import config
from aconio.bmd.cli import _utils, ntcs_cli, logfiles


class BMDService(pydantic.BaseModel):
    """Represent a BMD service ('Leistung').

    ### Field Annotations
    Each property within the `BMDService` class is of type `Annotated` to add
    additional metadata to the field. The added metadata is a dictionary
    holding the following keys:
    - `const_id`:
        The BMD const-ID of the field, required for a 'Standard-CSV' import to
        determine the respective DB-field to which the data should be imported.
    - `column_name`:
        The BMD column name of the field, required for a 'Standard-CSV' import.
        This column name is required in the second header line of the import
        file in order for the import to work.

    ### Generating an Import CSV File
    When generating the CSV file for importing the BMD service, we first write
    a header row holding all BMD Const-IDs and then add a second header row
    holding the column names.

    When writing the data rows, we can find the respective field value to the
    BMD Const-ID in the header using the `to_dict` method, which provides a
    mapping dictionary, holding the BMD Const-IDs as keys and the respective
    field values as values.
    """

    client_number: Annotated[
        str, {"const_id": "MCU_LEI_KUNDE", "column_name": "Kunden-Nr."}
    ]
    """BMD number (not ID) of the client for which the service is recorded."""

    employee_number: Annotated[
        str, {"const_id": "MCU_LEI_MITARBNR", "column_name": "Ma-Nr"}
    ]
    """BMD number (not ID) of the employee for which the service is recorded."""

    article_id: Annotated[
        str,
        {"const_id": "MCA_LEI_ARL_ARTIKELNR", "column_name": "Tät-Nr/Art-Nr"},
    ]
    """BMD article ID of the service (basically the service type)."""

    amount: Annotated[
        int, {"const_id": "MCU_LEI_MENGEN_EINGABE", "column_name": "Menge"}
    ] = 1
    """Amount of articles (respectively services) recorded.
    
    For services, this amount usually is 1.
    """

    recorded_date: Annotated[
        str,
        {"const_id": "MCA_LEI_LEISTUNGSDATUM", "column_name": "Leistungsdatum"},
    ] = datetime.today().strftime("%d.%m.%Y")
    """Date the service was recorded (format 'DD.MM.YYYY')."""

    reference_year: Annotated[
        int | None,
        {"const_id": "MCA_LEI_BEZUGSJAHR", "column_name": "BJ"},
    ] = None
    """The year referenced by the recorded service.
    
    For example, when the service is 'Bearbeitung Buchhaltung 12/2024', the
    reference year would be 2024, even though the service might have been
    recorded in 01/2025.
    """

    reference_month: Annotated[
        int | None,
        {"const_id": "MCA_LEI_BEZUGSMONAT", "column_name": "BM"},
    ] = None
    """The month referenced by the recorded service.
    
    For example, when the service is 'Bearbeitung Buchhaltung 12/2024', the
    reference month would be 12, even though the service might have been
    recorded in 01/2025.
    """

    text: Annotated[
        str,
        {"const_id": "MCA_LEI_LEISTUNGSTEXT", "column_name": "Text"},
    ]
    """Service description."""

    def to_dict(self) -> dict[str, str]:
        """Map BMD Const-IDs of all object properties to their values.

        For each object property, which has a `const_id` metadata value, the
        returned dictionary contains a pair, where the key is the Const-ID,
        and the value is the value of the property respetive to this Const-ID.

        Example:
        `{"MCA_LEI_BEZUGSMONAT": 6, "MCA_LEI_LEISTUNGSDATUM": 11.07.2024, ...}`
        """
        return {
            field.metadata[0]["const_id"]: getattr(self, name)
            for name, field in self.model_fields.items()
            if "const_id" in field.metadata[0]
        }

    @classmethod
    def bmd_const_ids(cls) -> list[str]:
        """Return a list of BMD Const-IDs for all class properties."""
        return [
            f.metadata[0]["const_id"]
            for f in cls.model_fields.values()
            if "const_id" in f.metadata[0]
        ]

    @classmethod
    def bmd_column_names(cls) -> list[str]:
        """Return a list of BMD column names for all class properties."""
        return [
            f.metadata[0]["column_name"]
            for f in cls.model_fields.values()
            if "column_name" in f.metadata[0]
        ]


def _services_to_csv(services: list[BMDService], file: str) -> None:
    """Write services to a CSV file for BMD 'Standard-CSV' imports.

    Args:
        services:
            List of BMD services that should be included in the CSV file.
        file:
            Filpath to the output CSV file.
    """

    _, ext = os.path.splitext(file)
    if ext != ".csv":
        raise ValueError("Please only provide '.csv' files to this function.")

    const_ids = BMDService.bmd_const_ids()
    column_names = BMDService.bmd_column_names()

    # pylint: disable=unspecified-encoding
    with open(file, "w", newline="") as csvfile:
        writer = csv.writer(
            csvfile, delimiter=";", quotechar='"', quoting=csv.QUOTE_MINIMAL
        )

        # Write the Const-ID header row with '%' delimiter
        header = f'NTCS_CONSTID_INFO%{len(const_ids)}%{"%".join(const_ids)}'
        csvfile.write(header + "\n")

        # Write the column names header row
        writer.writerow(column_names)

        # Write each BMDService object's data as a row in the CSV
        for s in services:
            data = s.to_dict()
            writer.writerow([data[const_id] for const_id in const_ids])


def import_services(services: list[BMDService]) -> None:
    """Import services ('Leistungen') into BMD via 'Standard-CSV' import.

    Args:
        services:
            List of services to import.
    """
    import_file = _utils.create_import_file("import_services.csv")
    _services_to_csv(services, import_file)

    ntcs_cli().run(
        function_name="MCS_BATCH_IMPORT_CSV",
        params={
            "STP_IMP_FILENAME": import_file,
            "STP_MD_CONSTID": "448500",
            "STP_ATTR_HAUPTGRP": "70001016",
            "STP_ATTR_SUBGRP": "1",
            "STP_IGNORE_FIRSTLINE": "1",
            "STP_SILENTSUCCESS": "1",
        },
    )
    time.sleep(2)

    # Validate logfile
    logfile = logfiles.BMDLogfile.from_file(
        os.path.join(config().log_dir, "StdCSVImport.log")
    )
    if not logfile.check_success():
        raise RuntimeError("BMD log file indicates failed services import!")

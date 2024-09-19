"""Handling of documents and interaction with the BMD archive."""

import os
import dataclasses

from datetime import datetime

from robocorp import log

from aconio.bmd import ui as bmd
from aconio.bmd.cli import ntcs_cli
from aconio.bmd.cli import _utils
from aconio.bmd._config import config, ExecutableType


@dataclasses.dataclass
class DMSDocument:
    """A BMD DMS document."""

    archive_id: str
    """ID of the BMD DMS archive the document belongs to."""

    category: str
    """BMD DMS category shortname ('Kurzbezeichnung')."""

    name: str
    """Name of the document in the BMD DMS."""

    path: str
    """Path to the document on the filesystem."""

    client_id: str
    """BMD ID of the client."""

    client_company_id: str
    """BMD company ID the client belongs to."""

    employee_id: str | None = None
    """
    BMD ID of the employee responsible for the document ('Sachbearbeiter').
    """

    employee_company_id: str | None = None
    """BMD company ID the employee belongs to."""

    archive_date: str = datetime.today().strftime("%Y%m%d")
    """Date the document was archived (format 'YYYYMMDD')."""

    def __post_init__(self):
        if self.employee_id and not self.employee_company_id:
            raise ValueError(
                "'employee_company_id' mandatory if 'employee_id' is set"
            )

        if self.employee_company_id and not self.employee_id:
            raise ValueError(
                "'employee_id' mandatory if 'employee_company_id' is set"
            )

        self.path = os.path.abspath(self.path)

    def bmddocs_row(self) -> str:
        """Return the document as a row usable for a 'bmddocs.dok' import."""

        # Empty strings represent fields not needed for the import
        row_items = [
            self.archive_id,
            self.client_id,
            "",
            self.category,
            self.path,
            self.name,
            "",
            "",
            "",
            self.archive_date,
        ]

        suffix = f"$EOD$DOCSPERSFIRMENNR={self.client_company_id}$EOD$"

        # Add 'Sachbearbeiter'
        if self.employee_id:
            suffix += f"DOK_MITARBEITERID={self.employee_id}$EOD$"
            suffix += f"DOK_MIT_FIRMENNR={self.employee_company_id}$EOD$"

        return ";".join(row_items) + suffix


def _documents_to_dok(
    docs: list[DMSDocument],
    file: str,
    optional: dict[str, str] | None = None,
) -> None:
    """Write documents to a '.dok' file for BMD DMS imports.

    Args:
        docs:
            List of BMD documents that should be included in the '.dok' file.
        file:
            Filpath to the output '.dok' file.
        optional:
            Used to pass optional arguments to the import. All optional fields
            available for the import can be found in the BMD help. Example:
            passing `{"KD": "1"}` would result in `$EOD$KD=1$EOD$` being added
            to all import lines.
    """

    _, ext = os.path.splitext(file)
    if ext != ".dok":
        raise ValueError("Please only provide '.dok' files to this function.")

    # Add optional import arguments
    optional_args = ""
    if optional:
        for k, v in optional.items():
            optional_args += f"{k}={v}$EOD$"

    lines = []
    for doc in docs:
        line = f"{doc.bmddocs_row()}$EOD${optional_args}"
        log.info(f"Adding line to 'bmddocs.dok' import file: '{line}'")
        lines.append(line)

    with open(file, "w") as f: # pylint: disable=unspecified-encoding
        f.write("\n".join(lines))


def open_dms_document(doc_id: str, archive_id: str) -> None:
    """Open a file directly from the BMD DMS.

    Note: The file will be opened via the default reader for the respective
    file type configured on the system.

    Args:
        doc_id:
            ID of the DMS document.
        archive_id:
            ID of the DMS archive to which the document belongs.
    """
    ntcs_cli().run(
        function_name="MCS_OPEN_DOCUMENT",
        params={"DOK_ARCHIVNR": archive_id, "DOK_DOKUMENTENNR": doc_id},
    )


def import_bmddocs(
    docs: list[DMSDocument], optional: dict[str, str] | None = None
) -> None:
    """Import files into the BMD DMS using the 'bmddocs.dok' interface.

    Args:
        docs:
            List of documents to import.
        optional:
            Used to pass optional arguments to the import. All optional fields
            available for the import can be found in the BMD help. Example:
            passing `{"KD": "1"}` would result in `$EOD$KD=1$EOD$` being added
            to all import lines.
    """
    import_file = _utils.create_import_file("bmddocs.dok")

    _documents_to_dok(docs=docs, file=import_file, optional=optional)

    ntcs_cli().run(
        function_name="MCS_MDDOKUMENTMGR_IMPORTNEWDOCS",
        params={"FILE": import_file},
    )

    # In case of a BMDExec call, we handle the pop-up which states that the
    # function execution was successful. If the pop-up cannot be found, it
    # indicates that something went wrong with the executed function.
    if config().ntcs_exec_type == ExecutableType.EXEC:
        bmd.bmd_window().find('name:"Achtung" class:TBMDMessageBoxFRM').find(
            'name:"Ok" class:TButton'
        ).click()

"""Extractor for compressed Advokat ERV data."""

import os
import shutil
import zipfile
import functools


class ERVExtractor:
    """Extractor for compressed Advokat ERV data.

    Receives an Advokat ".E" file containing the ERV data
    and extracts the ERV XML and any attached files from it.

    Requires a temporary directory for copying and unpacking
    the Advokat ZIP file. It is expected that the caller
    handles creation and cleanup of this temporary directory.
    """

    def __init__(self, advokat_zip_file: str, temp_dir: str) -> None:
        """Initialize the ERV parser.

        Args:
            advokat_zip_file:
                Path to the Advokat ".E" file containing the ERV data.
            temp_dir:
                Temporary directory to which the Advokat ZIP file will
                be copied for extraction.
        """
        self.advokat_zip_file = advokat_zip_file
        self.temp_dir = temp_dir

        self._copied_zip_file = os.path.join(self.temp_dir, "erv.zip")
        self._extract_dir = os.path.join(self.temp_dir, "extract")

        self._erv_xml_file = os.path.join(self._extract_dir, "ERV.XML")

    def extract_files(self) -> list[str]:
        """Parse the ERV data from the given Advokat file.

        Returns:
            The paths to the extracted ERV files.
        """

        self._copy_advokat_file_to_temp_dir_and_rename()
        self._extract_zip_file()

        # An XML file should always be present in the extracted files.
        self._verify_erv_xml_file_exists()

        return [
            os.path.join(self._extract_dir, f)
            for f in os.listdir(self._extract_dir)
        ]

    def _copy_advokat_file_to_temp_dir_and_rename(self) -> str:
        """Copy Advokat ".E" file to temp dir and convert to ".zip".

        Note: The ".Z" extension is used by Advokat to indicate a
        compressed file. Therefore, a rename to is ".zip" without
        any further parsing is sufficient.
        """

        shutil.copyfile(self.advokat_zip_file, self._copied_zip_file)

    def _extract_zip_file(self) -> str:
        """Extract the contents of the Advokat ZIP file."""

        with zipfile.ZipFile(self._copied_zip_file, "r") as zip_ref:
            zip_ref.extractall(self._extract_dir)

    def _verify_erv_xml_file_exists(self) -> str:
        if not os.path.exists(self._erv_xml_file):
            raise FileNotFoundError("ERV XML file not found after ZIP extract!")


@functools.lru_cache
def advokat_erv_base_path() -> str:
    """Get the base path for ERV data stored via Advokat."""
    return os.path.join("F:\\", "ADVOKAT2", "Daten", "ERV")

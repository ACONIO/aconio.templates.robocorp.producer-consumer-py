"""This file handles the instance of the pdf reader."""

import enum

from aconio.pdf_readers.chrome import ChromeReader
from aconio.pdf_readers.edge import EdgeReader
from aconio.pdf_readers.acrobat import AcrobatReader

from aconio import delay


class PDFReaderType(enum.StrEnum):
    CHROME = enum.auto()
    EDGE = enum.auto()
    ACROBAT = enum.auto()


class PDFReaderFactory:
    @staticmethod
    def determine_reader(
        reader: PDFReaderType, delay_manager: delay.DelayManager
    ):
        """Determine pdf reader based on the config."""
        match reader:
            case PDFReaderType.CHROME:
                return ChromeReader(delay_manager)
            case PDFReaderType.EDGE:
                return EdgeReader(delay_manager)
            case PDFReaderType.ACROBAT:
                return AcrobatReader(delay_manager)

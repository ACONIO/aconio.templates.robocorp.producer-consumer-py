"""Acrobat as a PDF-Reader"""

from aconio.pdf_readers import PDFReader


class AcrobatWindowNotFoundError(RuntimeError):
    """Raised when the acrobat window cannot be found."""

    pass


class AcrobatReader(PDFReader):
    """
    Implementation of PDFReader for reading and saving
    PDFs using Adobe Acrobat Reader.
    """

    @property
    def _window_locator(self) -> str:
        return "class:AcrobatSDIWindow"

    def save_as_pdf(self, out_path: str) -> None:
        acrobat = self.window()

        if self.is_open():
            acrobat.send_keys(
                "{Ctrl}{Shift}s", wait_time=self._delay_manager.get(1)
            )
            acrobat.send_keys("{Enter}", wait_time=self._delay_manager.get(1))
            save_dialog = acrobat.find_child_window('name:"Speichern unter"')
            save_dialog.find('subname:"Dateiname:" and class:Edit').send_keys(
                out_path, wait_time=self._delay_manager.get(3)
            )
            save_dialog.find('name:"Speichern" and class:Button').click(
                wait_time=self._delay_manager.get(2)
            )
            acrobat.close_window()
        else:
            raise AcrobatWindowNotFoundError(
                "ERROR: Could not find Acrobat window"
            )

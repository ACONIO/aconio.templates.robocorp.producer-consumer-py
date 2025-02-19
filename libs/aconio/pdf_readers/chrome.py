"""Chrome as a PDF-Reader"""

from aconio.pdf_readers import PDFReader


class ChromeWindowNotFoundError(RuntimeError):
    """Raised when the Chrome window cannot be found."""

    pass


class ChromeReader(PDFReader):
    """Implementation of PDFReader for reading and saving PDFs using Chrome."""

    @property
    def _window_locator(self) -> str:
        return 'subname:"Google Chrome" class:"Chrome_WidgetWin_1"'

    def save_as_pdf(self, out_path: str) -> None:
        chrome = self.window()

        if self.is_open():
            chrome.send_keys(
                keys="{Ctrl}s", wait_time=self._delay_manager.get(1)
            )
            chrome.send_keys(
                locator='name:"Speichern unter"',
                keys=out_path,
                wait_time=self._delay_manager.get(3),
            )
            chrome.find('name:"Speichern" and class:Button').click(
                wait_time=self._delay_manager.get(2)
            )
            chrome.close_window()
        else:
            raise ChromeWindowNotFoundError(
                "ERROR: Could not find Chrome window"
            )

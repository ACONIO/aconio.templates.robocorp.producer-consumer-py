"""Edge as a PDF-Reader"""

from aconio.pdf_readers import PDFReader


class EdgeWindowNotFoundError(RuntimeError):
    """Raised when the Edge window cannot be found."""

    pass


class EdgeReader(PDFReader):
    """Implementation of PDFReader for reading and saving PDFs using Edge."""

    @property
    def _window_locator(self) -> str:

        return 'subname:"Edge" and class:Chrome_WidgetWin_1'

    def save_as_pdf(self, out_path: str) -> None:
        edge = self.window()

        if self.is_open():
            edge.send_keys("{CTRL}P", wait_time=self._delay_manager.get(1))
            root_area = edge.find('id:"RootWebArea"')
            root_area.find('name:"Drucken" and control:ButtonControl').click(
                wait_time=self._delay_manager.get(2)
            )

            save_as_window = edge.find_child_window('subname:"speichern unter"')
            save_as_window.find(
                'subname:"Dateiname:" and class:Edit'
            ).send_keys(out_path, wait_time=self._delay_manager.get(3))
            save_as_window.find('name:"Speichern" and class:Button').click(
                wait_time=self._delay_manager.get(2)
            )
            edge.close_window()
        else:
            raise EdgeWindowNotFoundError("ERROR: Could not find Edge window")

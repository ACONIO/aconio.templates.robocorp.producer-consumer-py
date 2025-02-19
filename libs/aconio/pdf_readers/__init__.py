"""Module to interact with different PDF-Readers."""

from abc import ABC, abstractmethod
import robocorp.windows as windows

from aconio import delay
from aconio.errors import errors


class PDFReader(ABC):
    """Base class for a PDF reader."""

    def __init__(self, delay_manager: delay.DelayManager):
        self._delay_manager = delay_manager

    @property
    @abstractmethod
    def _window_locator(self) -> str:
        """Return the `robocorp.windows` locator for the PDF reader window."""
        pass

    @abstractmethod
    def save_as_pdf(self, out_path: str) -> None:
        """
        Save the currently open PDF document to disk.

        Args:
            out_path: The path where the PDF should be saved.
        """
        pass

    def window(self, **kwargs) -> windows.WindowElement:
        """Return the PDF reader window."""
        return windows.desktop().find_window(
            locator=self._window_locator,
            timeout=self._delay_manager.get(15),
            foreground=True,
            wait_time=self._delay_manager.get(2),
            **kwargs,
        )

    def is_open(self) -> bool:
        """Return whether the PDF reader window is open."""
        return self.window(raise_error=False) is not None

    def close(self) -> None:
        """Close the PDF reader window."""
        self.window().close_window()

    def raise_on_permission_dialog(self) -> None:

        permissions_popup = windows.find_window(
            locator='subname:"BMD - Software" > name:"Achtung"',
            raise_error=False,
        )

        if permissions_popup:
            permissions_popup.send_keys("{Enter}")
            raise errors.BusinessError(
                message='"No Permissons" dialog was found',
                code="INSUFFICIENT_DOCUMENT_PERMISSIONS",
            )

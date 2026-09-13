"""
A wrapper for the "FinanzOnline" web portal.

Since the "FinanzOnline" service does not offer an API, we create a
pseudo-API by sending HTTP requests to the "FinanzOnline" backend to
"fake" a user interacting with the web interface.
"""

import abc

from aconio.fon.repayments import _RepaymentAPI
from aconio.fon.tax_account import _TaxAccountAPI

from aconio.fon._auth import FonAuthenticator, FonCredential


class FonAPI(abc.ABC):
    """An API for the "FinanzOnline" web portal."""

    def __init__(self, credential: FonCredential) -> None:
        session = FonAuthenticator(credential).login()

        self.tax_account = _TaxAccountAPI(session)
        self.repayments = _RepaymentAPI(session)

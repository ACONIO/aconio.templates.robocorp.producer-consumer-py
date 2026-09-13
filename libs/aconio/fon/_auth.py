"""Handle the authentication process against "FinanzOnline"."""

from __future__ import annotations

import re
import bs4
import pyotp
import pydantic
import requests

import robocorp.vault

from requests import adapters

from aconio.fon._urls import FonURL
from aconio.fon._session import FonSession
from aconio.fon.errors import FinanzOnlineError, PersonificationRequiredError


class FonCredential(pydantic.BaseModel):
    """Credential required to authenticate against "FinanzOnline"."""

    participant_id: str
    user_id: str
    pin: str

    otp_code: str | None = None

    @staticmethod
    def from_robocorp_vault(secret_name: str) -> FonCredential:
        """Load the credential from the Robocorp vault.

        The secret keys must be equal to the attribute names of the
        `FonCredential` class.
        """
        secret = robocorp.vault.get_secret(secret_name)
        return FonCredential.model_validate(secret)

    @property
    def mfa_enabled(self) -> bool:
        return self.otp_code is not None

    def generate_otp(self) -> str:
        return pyotp.TOTP(self.otp_code).now()


class FonAuthenticator:
    """Handle the authentication process against "FinanzOnline"."""

    def __init__(self, credential: FonCredential):
        self.credential = credential

        self._session = requests.Session()
        self._session.mount(FonURL.BASE, adapters.HTTPAdapter(max_retries=5))

    def login(self) -> FonSession:
        response = self._request_login()
        request_key = self._extract_request_key(response.text)

        # Currently MFA is not really enforced by FON. We can create
        # a session without the MFA code. This may change in the future.
        # For now we create the session first and then still perform the MFA
        # request to be prepared for future. The URL for the MFA might change.
        session = FonSession(session=self._session, request_key=request_key)

        if self.credential.mfa_enabled:
            # Later we might need to use this response to create
            # the session.
            response = self._request_mfa(session)

        return session

    def _request_login(self) -> requests.Response:
        form_data = {
            "tid": self.credential.participant_id,
            "benid": self.credential.user_id,
            "pin": self.credential.pin,
        }

        response = self._session.post(
            url=FonURL.LOGIN, data=form_data, timeout=10
        )

        if not response.status_code == 200:
            raise FinanzOnlineError(
                "Failed to authenticate against FinanzOnline! "
                "Login request returned status code "
                f"{response.status_code}."
            )

        self._raise_on_fon_error(response.text)

        return response

    def _request_mfa(self, session: FonSession) -> requests.Response:
        form_data = {
            "field": self.credential.generate_otp(),
            "sub": "sub",
        }

        response = session.post(url=FonURL.LOGIN_MFA, data=form_data)

        if not response.status_code == 200:
            raise FinanzOnlineError(
                "Failed to perform FinanzOnline MFA! "
                "MFA request returned status code "
                f"{response.status_code}."
            )

        self._raise_on_fon_error(response.text)
        return response

    # TODO: This function can be removed if we find out that we do not need to
    # actually handle the "Personifizierung" dialog in the browser, but we can
    # just directly navigate to the routes we need.
    def _raise_on_personification(self, login_response_html: str) -> None:
        """Detect FinanzOnline error messages in the response HTML."""

        soup = bs4.BeautifulSoup(login_response_html, "html.parser")

        personification_btn = soup.find(
            "label", text="Ich möchte die Personifizierung sofort durchführen."
        )

        if personification_btn is None:
            return None
        else:
            raise PersonificationRequiredError(
                "A FinanzOnline personification dialog was detected! "
                "Personification is required in a browser instance."
            )

    def _raise_on_fon_error(self, login_response_html: str) -> bool:
        """Detect FinanzOnline error messages in the response HTML."""

        soup = bs4.BeautifulSoup(login_response_html, "html.parser")
        displayed_error = soup.find(
            "ul", attrs={"id": "fehlerAufgetretenListe"}
        )

        if displayed_error:
            raise FinanzOnlineError(
                "A FinanzOnline error was detected! "
                f"Error message: {displayed_error.text.strip()}"
            )

    def _extract_request_key(self, login_response_html: str) -> str:
        try:
            return re.search(r'".*reqkey=(.*?)"', login_response_html).group(1)
        except Exception as exc:
            raise FinanzOnlineError(
                "Failed to extract request key from "
                "FinanzOnline login response!"
            ) from exc

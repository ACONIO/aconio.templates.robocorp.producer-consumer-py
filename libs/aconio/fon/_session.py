"""Handle FinanzOnline sessions."""

import bs4
import requests

from aconio.fon._urls import FonURL


class FonSession:
    """Represent a "FinanzOnline" session.

    The cookies, request key, and CSRF token are carried
    through all subsequent requests to mock an active
    browser session of the user.
    """

    def __init__(self, session: requests.Session, request_key: str) -> None:
        self._session = session
        self.request_key = request_key

        self._csrf_token = self._get_csrf_token()

    def post(
        self, url: FonURL, data: dict, timeout: int = 10, **kwargs
    ) -> requests.Response:
        """Perform a GET request to the given FinanzOnline URL."""

        if kwargs.get("params") is not None:
            kwargs["params"].update({"reqkey": self.request_key})
        else:
            kwargs["params"] = {"reqkey": self.request_key}

        data["_csrf"] = self._csrf_token

        return self._session.post(
            url=url,
            data=data,
            timeout=timeout,
            **kwargs,
        )

    def get(
        self, url: FonURL, timeout: int = 10, **kwargs
    ) -> requests.Response:
        """Perform a GET request to the given FinanzOnline URL."""

        if kwargs.get("params") is not None:
            kwargs["params"].update({"reqkey": self.request_key})
        else:
            kwargs["params"] = {"reqkey": self.request_key}

        return self._session.get(
            url=url,
            timeout=timeout,
            **kwargs,
        )

    def get_cookies(self) -> dict[str, str]:
        """Return the session cookies as dict."""
        return self._session.cookies.get_dict()

    def _get_csrf_token(self) -> str:
        """Extract the CSRF token after a session has been established.

        The CSRF token is a hidden input field in an HTML form of a
        FON page. It is required on all subsequent POST requests to
        submit forms.

        We currently obtain the CSRF token from the login page.
        """

        try:
            response_csrf = self.get(FonURL.LOGIN)

            soup = bs4.BeautifulSoup(response_csrf.text, "html.parser")
            csrf = soup.find("input", attrs={"name": "_csrf"})["value"]

        except Exception as exc:
            raise RuntimeError("Failed to extract CSRF token!") from exc

        return csrf

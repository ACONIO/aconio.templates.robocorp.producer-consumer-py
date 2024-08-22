"""Webscraping functionality for the FinanzOnline website.

### Example Usage
```python
from aconio import fon 

fon.configure(
    teilnehmer_id="424242",
    benutzer_id="7301",
    pin="4774"
)

fon.download_steuerkonto_pdf(
    steuernummer="1234567890",
    output_filepath="steuerkonto.pdf",
)

info, meta = fon.query_steuerkonto(
    steuernummer="1234567890",
)
```
"""

import re
import time
import requests

from functools import lru_cache
from dataclasses import dataclass

from bs4 import BeautifulSoup

from robocorp import browser

from aconio.fon import _config


@lru_cache  # Always return the same instance.
def config() -> _config.Config:
    return _config.Config()


def configure(teilnehmer_id: str, benutzer_id: str, pin: str) -> None:
    """Set the module configuration.

    The credentials (teilnehmer_id, benutzer_id, pin) will be used for all
    interactions with FinanzOnline, thus it is mandatory to call `configure`
    before using any other function in the `aconio.fon` library.

    Args:
        teilnehmer_id:
            'Teilnehmer-ID' part of the FinanzOnline login credentials.

        benutzer_id:
            'Benutzer-ID' part of the FinanzOnline login credentials.

        pin:
            'PIN' part of the FinanzOnline login credentials.
    """
    config().teilnehmer_id = teilnehmer_id
    config().benutzer_id = benutzer_id
    config().pin = pin


def download_steuerkonto_pdf(
    steuernummer: str,
    output_filepath: str,
    anmerkungen: bool = False,
    rueckzahlungen: bool = False,
    zahlungsplan: bool = False,
    vorauszahlungen: bool = False,
    rueckstandsaufgliederung: bool = False,
) -> None:
    """Return the FinanzOnline 'Steuerkonto' as PDF.

    Args:
        steuernummer:
            Client tax number for which the query should be performed.

        output_filepath:
            Download location for the PDF file.

        anmerkungen:
            Include 'Anmerkungen' section in the PDF.

        rueckzahlungen:
            Include 'Rückzahlungen' section in the PDF.

        zahlungsplan:
            Include 'Zahlungsplan' section in the PDF.

        vorauszahlungen:
            Include 'Vorauszahlungen/Veranlagungen' section in the PDF.

        rueckstandsaufgliederung:
            Include 'Rückstandsaufgliederung' section in the PDF.
    """

    auth = _login()
    page = _open_page(auth.cookies)

    acc_url = f"{config().base_url}/fon/p/konto.do"

    # Go to 'Steuerkonto' page after login was handled in the background
    # and set tax ID.
    page.goto(f"{acc_url}?reqkey={auth.request_key}")
    page.locator('//input[@id="suchob"]').fill(steuernummer)

    # Select the checkboxes according to the given params
    if rueckzahlungen:
        page.locator('//input[@name="sabfrrz"]').check()
    if anmerkungen:
        page.locator('//input[@name="sabfranm"]').check()
    if zahlungsplan:
        page.locator('//input[@name="sabfrzp5"]').check()
    if vorauszahlungen:
        page.locator('//input[@name="sabfrvan"]').check()
    if rueckstandsaufgliederung:
        page.locator('//input[@name="sabfrraufgl"]').check()

    page.locator('//input[@name="submit"]').click()

    time.sleep(1)  # Wait for page to properly load before storing PDF

    # Remove the header nav bar, since it will display on each page and
    # overlap other content.
    # pylint: disable=line-too-long
    page.evaluate(
        """document.querySelector('[aria-label="Hauptmenü"]').style.display = 'none';"""
    )

    page.pdf(
        path=output_filepath,
        scale=0.7,
        margin={
            "top": "20px",
            "right": "20px",
            "left": "20px",
            "bottom": "20px",
        },
    )

    page.close()


@dataclass
class TaxAccount:
    endsaldo_stand: str | None = None
    endsaldo: str | None = None
    steuernummer: str | None = None
    finanzamt_number: str | None = None

    buchungen: list[dict] | None = None
    zahlungsplan: list[dict] | None = None
    rueckzahlungen: list[dict] | None = None


def query_steuerkonto(
    steuernummer: str, datum_ab: str = None, datum_bis: str = None
) -> TaxAccount:
    """Queries information of the FinanzOnline 'Steuerkonto'.

    Args:
        steuernummer:
            Client tax number for which the query should be performed.

        datum_ab:
            Begin date of the 'Steuerkonto' query (in format 'DDMMYYYY').

        datum_bis:
            End date of the 'Steuerkonto' query (in format 'DDMMYYYY').

    Raises:
        RuntimeError: Raised if 'Steuerkonto' request fails.

    Returns:
        `TaxAccount` object filled with 'Steuerkonto' data.
    """

    # Authenticate against FinanzOnline
    auth = _login()

    acc_url = f"{config().base_url}/fon/p/konto.do"

    form_data = {
        # 'Steuernummer' for which the query should be executed:
        "suchob": steuernummer,
        "sabfrzp5": "true",  # enable 'Zahlungsplan'
        "sabfrrz": "true",  # enable 'Rückzahlungen'
        "_csrf": _get_csrf_token(acc_url, auth),
    }

    # Add 'Zeitraum ab' parameter to query
    if datum_ab is not None:
        form_data["sabfrbubta"] = datum_ab

    # Add 'Zeitraum bis' parameter to query
    if datum_bis is not None:
        form_data["sabfrbubtb"] = datum_bis

    response = requests.post(
        url=acc_url,
        params={"reqkey": auth.request_key},
        data=form_data,
        cookies=auth.cookies,
        timeout=10,
    )

    if response.status_code == 200:

        account = _get_steuerkonto(response.text)

        # Check if an error occured when the query was performed.
        # e.g. wrong tax-ID will still result in a 200 status code
        # but display an error msg.
        soup = BeautifulSoup(response.text, "html.parser")
        error_msg = soup.find("ul", attrs={"id": "fehlerAufgetretenListe"})

        if error_msg is not None:
            err = error_msg.text[2::]  # Remove List sign
            raise RuntimeError(err)

        # Get the "Buchungen" table
        account.buchungen = _read_steuerkonto_table(
            html=response.text,
            region_label=re.compile(r".*Buchungen (vom|bis).*"),
        )

        # Get the "Zahlungsplan" table
        account.zahlungsplan = _read_steuerkonto_table(
            html=response.text, region_label="Zahlungsplan"
        )

        # Get the "Rückzahlungen" table
        account.rueckzahlungen = _read_steuerkonto_table(
            html=response.text,
            region_label="Information zu Rückzahlungen",
        )

        return account
    else:
        raise RuntimeError(
            f"Failed to query 'Steuerkonto' for ID '{steuernummer}'"
        )


def _login() -> _config.Authentication:
    """Authenticates against FinanzOnline.

    Raises:
        ValueError: If FinanzOnline credentials are not set.
        RuntimeError: If the authentication process fails.
    """

    if config().teilnehmer_id is None:
        raise ValueError("Missing 'Teilnehmer-ID' in the configuration.")

    if config().benutzer_id is None:
        raise ValueError("Missing 'Benutzer-ID' in the configuration.")

    if config().pin is None:
        raise ValueError("Missing 'PIN' in the configuration.")

    form_data = {
        "tid": config().teilnehmer_id,
        "benid": config().benutzer_id,
        "pin": config().pin,
    }

    # Authenticate against FinanzOnline
    login_url = f"{config().base_url}/fon/login.do"
    response = requests.post(url=login_url, data=form_data, timeout=10)
    cookies = response.cookies

    # Check the response status code
    if response.status_code == 200:
        # If a 'Personifizierung' is required, handle it and re-authenticate
        if _handle_personification(response.text, cookies=cookies):
            response = requests.post(url=login_url, data=form_data, timeout=10)
            cookies = response.cookies

        # Obtain request key used for further authenticated requests
        request_key = re.search(r'".*reqkey=(.*)"', response.text).group(1)

        return _config.Authentication(cookies=cookies, request_key=request_key)
    else:
        raise RuntimeError("Failed to authenticate against FinanzOnline!")


def _handle_personification(
    html: str, cookies: requests.cookies.RequestsCookieJar
) -> bool:
    """Handle personification popup.

    Check if the 'Personifizierung' pop-up is in the given HTML (which should be
    the FinanzOnline page after login). If no pop-up is found, return `False`.
    If a 'Personifizierung' pop-up is found, handle it and return `True`.

    Args:
        html (str): HTML of the page after a FinanzOnline login
    """

    # Parse the given HTML page
    soup = BeautifulSoup(html, "html.parser")

    # Try to find the 'Personifizierung' pop-up
    personification_radio_btns = soup.find(
        "label", text="Ich möchte die Personifizierung sofort durchführen."
    )

    if personification_radio_btns is None:
        # If no pop-up was found, return already correct given HTML page
        return False
    else:
        # If the pop-up was found, open the browser, enter login
        # credentials and click away the pop-up to ensure a successful
        # execution of the FinOnline commands.
        page = _open_page(cookies)

        # Login
        page.locator("[name=tid]").fill(config().teilnehmer_id)
        page.locator("[name=benid]").fill(config().benutzer_id)
        page.locator("[name=pin]").fill(config().pin)

        # Wait for all values to be set properly before submitting.
        time.sleep(1.5)
        page.locator('//input[@name="submit"]').click()

        # Skip personification
        # pylint: disable=line-too-long
        page.locator(
            '//label[contains(text(),"Ich möchte die Personifizierung später durchführen.")]'
        ).click()
        page.locator('//input[@name="submit"]').click()

        page.close()

        return True


def _open_page(cookies: requests.cookies.RequestsCookieJar) -> any:
    """Opens a headless Chrome browser and sets the given cookies."""

    browser.configure(headless=True)
    browser.context().add_cookies(
        [
            {"name": c.name, "value": c.value, "url": config().base_url}
            for c in cookies
        ]
    )

    page = browser.page()
    page.goto(config().base_url)

    return page


def _get_csrf_token(url: str, auth: _config.Authentication) -> str:
    """Extract the CSRF token required for later requests."""

    try:
        response_csrf = requests.get(
            url,
            cookies=auth.cookies,
            params={"reqkey": auth.request_key},
            timeout=10,
        )

        soup = BeautifulSoup(response_csrf.text, "html.parser")
        csrf = soup.find("input", attrs={"name": "_csrf"})["value"]

    except Exception as exc:
        raise RuntimeError("Failed to extract CSRF token!") from exc

    return csrf


def _read_steuerkonto_table(html: str, region_label: str) -> list[dict] | None:
    """Read HTML table of the 'Steuerkonto'.

    Args:
        html:
            HTML of the 'FinanzOnline Steuerkonto' page.

        region_label:
            The `aria-label` value of the section `div` (can be regex pattern)

    Returns:
        List of dictionaries with the extracted data.
        Each entry in the list represents a row in the table.
    """
    soup = BeautifulSoup(html, "html.parser")

    section = soup.find("div", attrs={"aria-label": region_label})

    # Check if section is empty
    no_data_text = section.find(
        "div", text=re.compile(r".*Keine entsprechenden Daten vorhanden*")
    )

    if no_data_text is not None:
        return None

    table = section.find("table", attrs={"class": "table-striped"})

    # Grab all table header names
    headers = [th.text for th in table.find_all("th")]

    # Extract values from the table rows
    extracted_data = []

    # For each table row, create a dictionary with:
    # key=column name / value=column value
    for row in table.find_all("tr"):
        data = {}
        columns = row.find_all("td")

        if len(columns) > 0:
            # Get the data of this row for each header (i.e. column)
            for idx, th in enumerate(headers):
                data[th] = (
                    columns[idx]
                    .text.strip()
                    .replace("\t", "")
                    .replace("\n", "")
                )
            extracted_data.append(data)

    return extracted_data


def _get_steuerkonto(html: str) -> TaxAccount:
    """Extract metadata from the FinanzOnline 'Steuerkonto'.

    Particularly, the 'Endsaldo Stand', 'Endsaldo', 'Steuernummer'
    and 'Finanzamtnummer'. If any of those values are not extractable,
    they will be set to `None`.

    Args:
        steuerkonto_html: HTML of the 'FinanzOnline Steuerkonto'.

    Returns:
        `TaxAccount` object.
    """

    account = TaxAccount()

    soup = BeautifulSoup(html, "html.parser")

    # Check if 'Buchungen' section shows "keine Daten vorhanden"
    # If this is the case, the 'Endsaldo' values won't be extractable
    no_data_text = soup.find(
        "div", attrs={"aria-label": re.compile(r".*Buchungen (vom|bis).*")}
    ).find("div", text=re.compile(r".*Keine entsprechenden Daten vorhanden*"))
    if no_data_text is not None:
        account.endsaldo_stand = None
        account.endsaldo = None
    else:
        # Get the 'Endsaldo' table
        endsaldo_table = soup.find_all("table", attrs={"class": "table"})[2]

        # Extract the "Endsaldo Stand" date
        account.endsaldo_stand = endsaldo_table.find_all("td")[0].text.strip()

        # Extract the "Endsaldo" value
        account.endsaldo = endsaldo_table.find_all("td")[1].text.strip()

    # Extract the "Steuernummer" value
    steuernummer = (
        soup.find("div", text=re.compile(r".*Steuernummer.*"))
        .find_next_sibling("div")
        .text.strip()
    )

    account.steuernummer = steuernummer

    # Extract the "Finanzamt" number
    finanzamt_div = soup.find("div", text=re.compile(r".*Finanzamt.*"))
    finanzamt_text = finanzamt_div.find_next_sibling("div").text.strip()

    match = re.search(r"\((\d+)\)", finanzamt_text)
    if match:
        account.finanzamt_number = match.group(1)

    return account

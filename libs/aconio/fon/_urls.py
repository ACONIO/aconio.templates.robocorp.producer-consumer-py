"""URLs used by the FON service."""


class FonURL:
    """URLs used by the FON service."""

    BASE = "https://finanzonline.bmf.gv.at"

    # Auth
    LOGIN = f"{BASE}/fon/login.do"
    LOGIN_MFA = f"{BASE}/fon/p/2fa/login.do"

    # QUERIES
    QUERY_TAX_ACCOUNT = f"{BASE}/fon/p/konto.do"

    # SERVICES
    SERVICE_REPAYMENT_START = f"{BASE}/fon/p/rz/rz.do"
    SERVICE_REPAYMENT_SUBMIT = f"{BASE}/fon/p/rz/rz2.do"

"""Advokat related errors."""


class AdvokatError(Exception):
    """Generic Advokat related error."""


class AdvokatActManagementSearchError(AdvokatError):
    """
    Raised if a search in the Advokat "Aktenverwaltung" yields no results,
    or another unexpected pop-up appears.
    """

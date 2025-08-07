"""Base class for all API namespaces."""

from ..http import Http


class Api:
    """Base class for all API namespaces."""

    def __init__(self, http: Http) -> None:
        """Initialize the API namespace with an HTTP client."""
        self.http = http

    def _filter(self, elements, filters):
        """Filter elements with a list of constraints."""
        if not isinstance(filters, dict) or not filters:
            return elements

        return [
            element
            for element in elements
            if all(element[key] == value for key, value in filters.items())
        ]

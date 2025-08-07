"""Base API for Synology SRM."""

from ..api import Api


class ApiBase(Api):
    """API Base.

    Handles the SYNO.API API namespace.
    """

    def query_info(self):
        """Gets the API info list."""
        # No need to pass restricted=False here, as this is a public API.
        return self.http.call(
            endpoint="query.cgi",
            api="SYNO.API.Info",
            method="query",
            version=1,
            params={
                "query": "ALL",
            },
            restricted=False,
        )

    def test_connection(self):
        """Tests the connection to the API."""
        return self.http.call(
            endpoint="query.cgi",
            api="SYNO.API.Info",
            method="query",
            version=1,
            params={
                "query": "ALL",
            },
        )

    def getinfo_encryption(self):
        """Gets the API encryption."""
        return self.http.call(
            endpoint="encryption.cgi",
            api="SYNO.API.Encryption",
            method="getinfo",
            version=1,
        )

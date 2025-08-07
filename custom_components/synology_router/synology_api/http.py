"""HTTP connection to the Synology API."""

from pathlib import Path

import requests
import urllib3

COMMON_ERROR_CODES = {
    100: "Unknown error",
    101: "No parameter of API, method or version",
    102: "The requested API does not exist",
    103: "The requested method does not exist",
    104: "The requested version does not support the functionality",
    105: "The logged in session does not have permission",
    106: "Session timeout",
    107: "Session interrupted by duplicate login",
    117: "Need manager rights for operation",
}


class Http:
    """HTTP connection to the API.

    This class is responsible for handling all communications with the API.
    """

    def __init__(
        self, host: str, port: int, username: str, password: str, https: bool = True
    ) -> None:
        """Initialize the HTTP connection to the Synology API."""

        self.host = host
        self.port = port

        self.username = username
        self.password = password

        self.https = https
        self.verify = True

        self.sid = None

    def disable_https_verify(self):
        """Disable the HTTPS certificate check."""

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.verify = False

    def _get_base_url(self):
        return "{}://{}:{}/webapi".format(
            "https" if self.https else "http", self.host, self.port
        )

    def _login(self):
        params = {"format": "sid", "account": self.username, "passwd": self.password}

        errors = {
            400: "No such account or incorrect password",
            401: "Account disabled",
            402: "Permission denied",
            403: "2-step verification code required",
            404: "Failed to authenticate 2-step verification code",
        }

        response = self.call(
            endpoint="auth.cgi",
            api="SYNO.API.Auth",
            method="Login",
            version=2,
            params=params,
            restricted=False,
            errors=errors,
        )

        self.sid = response["sid"]

    def download(self, path, **kwargs) -> None:
        """Download a file to the local filesystem from the Synology API."""
        request = self.call(stream=True, **kwargs)
        with Path.open(path, "wb", encoding="utf-8") as stream:
            stream.writelines(request)

    def call(
        self,
        endpoint: str,
        api: str,
        method: str,
        version: int = 1,
        params: dict | None = None,
        stream: bool = False,
        restricted: bool = True,
        retried: bool = False,
        errors: dict | None = None,
    ):
        """Performs an HTTP call to the Synology API."""
        url = f"{self._get_base_url()}/{endpoint}"

        params = params or {}
        errors = errors or {}

        if restricted and self.sid is None:
            self._login()

        cookies = {}
        if self.sid is not None:
            cookies["id"] = self.sid

        params["api"] = api
        params["method"] = method
        params["version"] = version

        response = requests.get(
            url,
            verify=self.verify,
            params=params,
            cookies=cookies,
            stream=stream,
            timeout=5,
        )

        if response.status_code != 200:
            raise SynologyHttpException(
                f"The server answered a wrong status code (code={response.status_code})"
            )

        if (
            "content-type" in response.headers
            and response.headers["content-type"] == "application/zip"
        ):
            return response

        data = response.json()

        if "success" not in data and ("data" not in data or "error" not in data):
            raise SynologyHttpException(
                "The output received by the server is malformed"
            )

        if not data["success"]:
            code = data["error"]["code"]

            if 100 <= code < 200:
                message = self._get_common_error_message(code)

                # 106 Session timeout
                # 107 Session interrupted by duplicate login
                if code in (106, 107):
                    if not restricted or retried:
                        # We should stop here if:
                        #  1 - Public route, no need to retry the login
                        #  2 - We already retried the route
                        raise SynologyCommonError(
                            code,
                            message,
                        )
                    self._login()
                    # Retry the current request with a new token
                    return self.call(
                        endpoint=endpoint,
                        api=api,
                        method=method,
                        version=version,
                        params=params,
                        restricted=True,
                        retried=True,
                        errors=errors,
                    )

                raise SynologyCommonError(
                    code,
                    message,
                )

            if code in errors:
                message = errors[code]
            else:
                message = "Unknown API error, please check the documentation"

            raise SynologyApiError(
                code,
                message,
            )

        if "success" in data and "data" not in data:
            return data["success"]
        return data["data"]

    def _get_common_error_message(self, code):
        """Gets the official message errror from the API documentation."""

        if code not in COMMON_ERROR_CODES:
            return "Unknown common error, please check the documentation"
        return COMMON_ERROR_CODES[code]


class SynologyException(Exception):
    """Base Synology exception."""


class SynologyHttpException(SynologyException):
    """Synology HTTP exception."""


class SynologyError(SynologyException):
    """Base Synology error."""

    def __init__(self, code, message) -> None:
        """Initialize the Synology error."""
        self.code = code
        self.message = message
        super(SynologyError).__init__(f"{message} (error={code})")


class SynologyCommonError(SynologyError):
    """Synology common errror."""


class SynologyApiError(SynologyError):
    """Synology API error."""

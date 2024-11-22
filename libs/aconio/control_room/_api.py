"""Wrapper for the Robocorp Control Room API."""

import json
import time
import requests
import functools
from urllib.parse import urljoin

from typing import Any

from ._config import config


class _ControlRoomAPI:
    """Wrapper for the Robocorp Control Room API."""

    def get(
        self,
        route: str,
        params: dict[str, str] | None = None,
        **kwargs,
    ) -> Any | bytes:
        """Perform a GET request against the Robocorp Control Room API.
        Args:
            route:
                API endpoint excluding the base URL, for example:
                `/workspaces/{workspace_id}/work-items`.
            params:
                Query parameters.
            kwargs:
                Extra keyword arguments passed to `requests.get`.
        Returns:
            The result of the GET request, either in JSON or binary form,
            depending on the `binary` parameter.
        Raises:
            RuntimeError:
                If any status code other than 200 is returned from the GET
                request.
        """

        res = self._request(
            method="GET",
            url=self._get_cr_endpoint_from_route(route),
            params=params,
            **kwargs,
        )

        body = json.loads(res.text)
        if self._is_paginated_response(body):
            body = self._collect_paginated_results(body)

        return body

    def post(
        self,
        route: str,
        params: dict[str, str] | None = None,
        body: dict | None = None,
        **kwargs,
    ) -> Any | bytes:
        """Perform a POST request against the Robocorp Control Room API.
        Args:
            route:
                API endpoint excluding the base URL, for example:
                `/workspaces/{workspace_id}/work-items`.
            params:
                Query parameters.
            kwargs:
                Extra keyword arguments passed to `requests.get`.
        Returns:
            The result of the GET request, either in JSON or binary form,
            depending on the `binary` parameter.
        Raises:
            RuntimeError:
                If any status code other than 200 is returned from the GET
                request.
        """

        res = self._request(
            method="POST",
            url=self._get_cr_endpoint_from_route(route),
            params=params,
            **kwargs,
            body=body,
        )

        body = json.loads(res.text)
        if self._is_paginated_response(body):
            body = self._collect_paginated_results(body)

        return body

    def _request(
        self,
        method: str,
        url: str,
        body: dict | None = None,
        retries: int = 3,
        retry_wait_time: int = 2,
        **kwargs,
    ) -> Any:
        """Perform a request against the Robocorp Control Room API.
        Wraps `requests.request` and automatically passes headers required
        for authentication against the CR API. Also, a retry-mechanism
        for 5xx error codes is implemented.
        Args:
            method:
                HTTP method ("GET", "POST", ...).
            url:
                Full Control Room API endpoint.
            kwargs:
                Arguments passed to `requests.request`.
            retries:
                How often the request should be retried in case of an
                unsuccessful request. A request is defined as unsuccessful
                if the status code is `5xx`.
            retry_wait_time:
                Wait time before retrying after a failed request in seconds.
        Returns:
            The return value of `requests.request`.
        Raises:
            RuntimeError:
                If the executed request returns a`5xx` status code for each
                retry specified with `retries`.
        """

        if kwargs.get("headers") is not None:
            kwargs["headers"].update(config().auth_header)
        else:
            kwargs["headers"] = config().auth_header

        for i in range(retries):
            # pylint: disable=missing-timeout
            res = requests.request(
                method=method,
                url=url,
                **kwargs,
                json=body,
            )

            if str(res.status_code).startswith("5"):
                if i == retries - 1:
                    raise RuntimeError(
                        "POST request unsuccessful, status code: "
                        f'"{res.status_code}". Error message: "{res.text}"'
                    )
                else:
                    time.sleep(retry_wait_time)
                    continue
            elif str(res.status_code).startswith("4"):
                self._raise_client_error(res)
            else:
                res.raise_for_status()
                return res

    def _is_paginated_response(self, response_json: dict) -> bool:
        """States if the given CR response implements pagination."""

        return "has_more" in response_json

    def _collect_paginated_results(self, response_json: dict) -> list:
        """Combine all paginated results of given CR response into one list."""

        collected_data = []
        while True:
            if data := response_json.get("data"):
                collected_data.extend(data)

            if not response_json.get("has_more"):
                break

            res = self._request(method="GET", url=response_json.get("next"))
            response_json = json.loads(res.text)

        return collected_data

    def _get_cr_endpoint_from_route(self, route: str) -> str:
        return urljoin(config().endpoint, route.lstrip("/"))

    def _raise_client_error(self, response: requests.Response) -> None:
        body = json.loads(response.text)

        cr_err_code = body.get("error").get("code")
        cr_err_sub_code = body.get("error").get("subCode")
        cr_err_msg = body.get("error").get("message")

        raise RuntimeError(
            "Request against CR API failed with HTTP status code "
            f"{response.status_code}!\n\n"
            f"Code: {cr_err_code} - {cr_err_sub_code}\n"
            f"Message: {cr_err_msg}\n"
        )


@functools.lru_cache
def api() -> _ControlRoomAPI:
    return _ControlRoomAPI()

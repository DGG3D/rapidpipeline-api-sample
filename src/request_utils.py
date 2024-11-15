import urllib.request
import urllib.error
import json
from typing import Dict, Optional
import time
from http.client import HTTPResponse

class RequestUtils:
    """Utility class for handling HTTP requests to the RapidPipeline API."""

    MAX_RETRIES = 3
    RETRY_DELAY = 30  # seconds

    def get_json(self, url: str, headers: Dict[str, str]) -> Optional[Dict]:
        """
        Perform a GET request and return JSON response.

        Args:
            url: The endpoint URL
            headers: Request headers

        Returns:
            Optional[Dict]: JSON response or None if request failed
        """
        request = urllib.request.Request(url, headers=headers)
        return self._execute_json_request(request)

    def post_json(
        self, url: str, headers: Dict[str, str], payload: Dict
    ) -> Optional[Dict]:
        """
        Perform a POST request with JSON payload.

        Args:
            url: The endpoint URL
            headers: Request headers
            payload: JSON payload

        Returns:
            Optional[Dict]: JSON response or None if request failed
        """
        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(url, data=data, headers=headers, method="POST")
        return self._execute_json_request(request)

    def put_binary(self, url: str, data: bytes) -> bool:
        """
        Perform a PUT request with binary data.

        Args:
            url: The endpoint URL
            data: Binary data to upload

        Returns:
            bool: True if successful, False otherwise
        """
        request = urllib.request.Request(url, data=data, method="PUT")
        response = self._execute_request(request)
        return response is not None

    def delete(self, url: str, headers: Dict[str, str]) -> bool:
        """
        Perform a DELETE request.

        Args:
            url: The endpoint URL
            headers: Request headers

        Returns:
            bool: True if successful, False otherwise
        """
        request = urllib.request.Request(url, headers=headers, method="DELETE")
        response = self._execute_request(request)
        return response is not None

    def _execute_json_request(self, request: urllib.request.Request) -> Optional[Dict]:
        """
        Execute a request and parse JSON response.

        Args:
            request: The prepared request

        Returns:
            Optional[Dict]: Parsed JSON response or None if request failed
        """
        response = self._execute_request(request)
        if not response:
            return None

        try:
            return json.loads(response.read().decode("utf-8"))
        except json.JSONDecodeError as e:
            print(f"ERROR: Failed to parse JSON response: {e}")
            return None

    def _execute_request(
        self, request: urllib.request.Request
    ) -> Optional[HTTPResponse]:
        """
        Execute an HTTP request with retry logic.

        Args:
            request: The prepared request

        Returns:
            Optional[HTTPResponse]: Response object or None if all retries failed
        """
        retries = 0
        while retries < self.MAX_RETRIES:
            try:
                return urllib.request.urlopen(request)
            except urllib.error.HTTPError as e:
                if e.code == 429:  # Too Many Requests
                    retries += 1
                    if retries < self.MAX_RETRIES:
                        print(
                            f"Rate limit exceeded. Retrying in {self.RETRY_DELAY} seconds..."
                        )
                        time.sleep(self.RETRY_DELAY)
                        continue
                self._handle_http_error(e)
                return None
            except urllib.error.URLError as e:
                self._handle_url_error(e)
                return None
            except Exception as e:
                print(f"ERROR: Unexpected error occurred: {e}")
                return None

    def _handle_http_error(self, error: urllib.error.HTTPError) -> None:
        """
        Handle HTTP errors and print relevant information.

        Args:
            error: The HTTP error
        """
        print("=" * 50)
        print(f"ERROR: The server returned HTTP {error.code}")
        print(f"Reason: {error.reason}")

        try:
            error_body = error.read().decode("utf-8")
            error_json = json.loads(error_body)
            print(f"Server message: {error_json.get('message', 'No message provided')}")
            if "errors" in error_json:
                print("Detailed errors:")
                print(json.dumps(error_json["errors"], indent=2))
        except (json.JSONDecodeError, AttributeError):
            print(
                f"Raw error response: {error_body if 'error_body' in locals() else 'No response body'}"
            )
        print("=" * 50)

    def _handle_url_error(self, error: urllib.error.URLError) -> None:
        """
        Handle URL errors and print relevant information.

        Args:
            error: The URL error
        """
        print("=" * 50)
        print("ERROR: Failed to reach the server")
        print(f"Reason: {error.reason}")
        print("=" * 50)

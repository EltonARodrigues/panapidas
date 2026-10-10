import json
import time
import typing

import gi
gi.require_version("Soup", "3.0")
from gi.repository import GObject, GLib, Soup

from urllib.parse import urlencode


class Response(GObject.GObject):
    __gtype_name__ = "Response"

    url: str
    body: str
    _status: str
    _headers: Soup.MessageHeaders
    _time_seconds: int = 0
    _response_size: int = 0

    def __init__(self, url: str, body, status: str, headers: Soup.MessageHeaders, time_seconds, response_size):
        super().__init__()
        self.url = url
        self.body = body
        self._status = status
        self._headers = headers
        self._time_seconds = time_seconds
        self._response_size = response_size

    @staticmethod
    def convert_json(body) -> typing.Any:
        try:
            output = json.loads(body)
            return output
        except json.JSONDecodeError:
            pass
        return body

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value: int):
        self._status = value

    @property
    def time_seconds(self) -> str:
        if not self._time_seconds:
            return "0 s"
        if self._time_seconds < 0.001:
            return f"{self._time_seconds * 1_000_000:.2f} µs"
        elif self._time_seconds < 1:
            return f"{self._time_seconds * 1000:.2f} ms"
        elif self._time_seconds < 60:
            return f"{self._time_seconds:.2f} s"

        minutes = self._time_seconds / 60
        return f"{minutes:.2f} min ({self._time_seconds:.2f} s)"

    @time_seconds.setter
    def time_seconds(self, value: int):
        self._time_seconds = value

    @property
    def response_size(self) -> str:
        if not self._response_size:
            return "0 s"
        for unidade in ["bytes", "KB", "MB", "GB"]:
            if self._response_size < 1024.0:
                return f"{self._response_size:.2f} {unidade}"
            self._response_size /= 1024.0
        return f"{self._response_size:.2f} TB"

    @response_size.setter
    def response_size(self, value: int):
        self._response_size = value

    @property
    def headers(self) -> dict:
        result = {}
        it = Soup.MessageHeadersIter()
        if not self._headers:
            return None

        it.init(self._headers)

        while True:
            has_next, it, name, value  = it.next(it)
            if not has_next:
                break
            if name in result:
                result[name].append(value)
            else:
                result[name] = [value]

        return result

    @headers.setter
    def headers(self, headers):
        self._headers = headers

def request(
    body_type: str,
    url: str,
    body: str = None,
    params: dict = None,
    headers: dict = None,
    method: str = "GET",
    data_as_json: bool = True,
):
    session = Soup.Session()
    base = GLib.Uri.parse(url, GLib.UriFlags.NONE)

    uri = GLib.Uri.build(
        GLib.UriFlags.NONE,
        base.get_scheme(),
        base.get_userinfo(),
        base.get_host(),
        base.get_port(),
        base.get_path(),
        urlencode(params) if params else None,
        base.get_fragment(),
    )

    if body["type"] == "form_data" and method == "POST":
        multipart = Soup.Multipart.new("multipart/form-data")

        for key in body["form_data"]:
            multipart.append_form_string(key, body["form_data"][key])

        message = Soup.Message.new_from_multipart(url, multipart)
    else:
        message = Soup.Message.new(method, uri.to_string())

    request_headers = message.get_request_headers()

    if headers:
        for chave, valor in headers.items():
            request_headers.append(chave, valor)

    if body_type == "form_urlencoded":
        request_headers.append("Content-Type", "application/x-www-form-urlencoded")

    if body_type == "form_data":
        request_headers.append("Content-Type", "multipart/form-data; boundary=<>")

    if data_as_json:
        request_headers.append("Content-Type", "application/json")

    if body["type"] == "urlencoded":
        encoded = Soup.form_encode_hash(body["urlencoded"])
        message.set_request_body_from_bytes(
            request_headers.get_content_type()[0], GLib.Bytes.new(encoded.encode("utf-8"))
        )

    if body["type"] == "raw":
        message.set_request_body_from_bytes(
            request_headers.get_content_type()[0], GLib.Bytes.new(body["raw"].encode("utf-8"))
        )

    try:
        time_start_count = time.perf_counter()
        body_bytes = session.send_and_read(message, None)
        time_ttfb = (time.perf_counter() - time_start_count) * 1000

        status = message.get_status()  # na 3.0 é get_status(), não status_code
        reason = message.get_reason_phrase()

        response_headers = message.get_response_headers()
        headers_dict = {}
        response_headers.foreach(
            lambda name, value, _: headers_dict.__setitem__(name, value), None
        )

        body = ""
        if body_bytes is not None:
            body = body_bytes.get_data().decode("utf-8", errors="replace")

        return Response(
            url=message.get_uri().to_string(),
            body=body,
            headers=response_headers,
            status=f"{status} {reason}",
            time_seconds=time_ttfb,
            response_size=len(body),
        )

    except GLib.Error as e:
        print(f"Connection failed. {e}")
        return Response(
            url=None,
            body="Connection failed",
            headers=None,
            status=None,
            time_seconds=None,
            response_size=None,
        )

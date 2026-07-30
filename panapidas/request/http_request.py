import json
import time
import typing
import urllib3

from urllib.parse import urlencode, urlsplit

class Response(typing.NamedTuple):
    body: str
    headers: str
    status: int
    time_seconds: int = 0
    response_size: int = 0

    def json(self) -> typing.Any:
        try:
            output = json.loads(self.body)
            return output
        except json.JSONDecodeError:
            pass
        return self.body

    @property
    def time_seconds(self) -> str:
        if self.time_seconds < 0.001:
            return f"{self.time_seconds * 1_000_000:.2f} µs"
        elif self.time_seconds < 1:
            return f"{self.time_seconds * 1000:.2f} ms"
        elif self.time_seconds < 60:
            return f"{self.time_seconds:.2f} s"

        minutes = self.time_seconds / 60
        return f"{minutes:.2f} min ({self.time_seconds:.2f} s)"

    @property
    def response_size(bytes) -> str:
        for unidade in ['bytes', 'KB', 'MB', 'GB']:
            if bytes < 1024.0:
                return f"{bytes:.2f} {unidade}"
            bytes /= 1024.0
        return f"{bytes:.2f} TB"

def request(
    body_type: str,
    url: str,
    body: dict = None,
    params: dict = None,
    headers: dict = {},
    method: str = "GET",
    data_as_json: bool = True,
    error_count: int = 0,
):
    print(type(headers))
    if body_type == "form_urlencoded":
        headers["Content-Type"] = "application/x-www-form-urlencoded"

    if body_type == "form_data":
        headers["Content-Type"] = "multipart/form-data; boundary=<calculated when request is sent>"

    if data_as_json:
        headers["Content-Type"] = "application/json"

    fields = None
    if method in ["GET", "DELETED", "HEAD"] or body_type == "form_data":
        fields = params

    if params is not None and (method in ["POST", "PUT"] or body_type == "form_urlencoded"):
        print(params)
        encoded_args = urlencode(params)
        url = url + encoded_args

    json_body = body if data_as_json else None

    teste = {
        "method":method,
        "url":url,
        "json":json_body,
        "fields": fields,
        "headers":headers,
        "preload_content":False
    }
    print(teste)

    try:
        http = urllib3.PoolManager()

        time_start_count = time.perf_counter()
        resp = http.request(
            method=method,
            url=urlsplit(url).geturl(),
            json=json_body,
            fields= fields,
            headers=headers,
            preload_content=False
        )
        time_ttfb = time.perf_counter() - time_start_count

        dados = resp.read()
        time_total = time.perf_counter() - time_start_count
        resp.release_conn()

        print(f"⏱️  TTFB (Server Processing + Network): {time_ttfb:.4f} segundos")
        print(f"⏱️  Tempo Total (Usuário esperou):      {time_total:.4f} segundos")
        print(f"📦 Tempo gasto apenas baixando o JSON:  {time_total - time_ttfb:.4f} segundos")

        return Response(
            body= dados.decode('utf-8'),
            headers= resp.headers,
            status= resp.status,
            time_seconds= time_ttfb,
            response_size=len(dados)
        )

    except urllib3.exceptions.NewConnectionError:
        print("Connection failed.")

    except urllib3.exceptions.TimeoutError:
        print("A API demorou muito. Tente novamente mais tarde.")
        return None
    except urllib3.exceptions.NewConnectionError:
        print("Sem internet ou servidor inacessível.")

    except ValueError as e:
        return Response(
            body= str(e),
            headers= None,
            status= None,
            # time= time_ttfb,
        )

    except Exception as e:
        print(e)
        return Response(
            body= "",
            headers= None,
            status= None,
            # time= time_ttfb,
        )

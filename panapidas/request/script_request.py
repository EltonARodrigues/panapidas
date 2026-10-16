import json

import dukpy

from panapidas.model.env_object import ActiveEnvs
from panapidas.model.requests import Request
from panapidas.request.http_request import Response

class PanapidasRequestObject():
    def __init__(self, request):
        self.request = request

    def get_method(self) -> str:
        return self.request.method

    def get_url(self) -> str:
        return self.request.url

    def set_url(self, url: str) -> None:
        self.request.url = url

    def get_body(self) -> dict:
        return Request.convert_body_to_dict(self.request.body)

    def get_params(self) -> str:
        # Retorna JSON (string) para o JS poder reconstruir
        return json.dumps([ param.to_dict() for param in self.request.params])

    def get_headers(self) -> str:
        return json.dumps([ header.to_dict() for header in self.request.headers])

    def set_body(self, b: str) -> None:
        self.request.body = b

    def header_get(self, key: str) -> str:
        return self.request.headers.get(key, "")

    def header_add(self, key: str, value: str) -> None:
        self.request.headers[key] = value

    def header_remove(self, key: str) -> None:
        self.request.headers.pop(key, None)

    def param_add(self, key: str, value: str) -> None:
        self.request.params[key] = value

    def param_remove(self, key: str) -> None:
        self.request.params.pop(key, None)

class PanapidasResponseObject():
    def __init__(self, response):
        self.response = response

    def get_url(self) -> str:
        return self.response.url

    def get_body(self) -> str:
        return self.response.body

    def get_headers(self) -> str:
        return json.dumps(self.response.headers) if self.response.headers is not None else []

    def header_get(self, key: str) -> str:
        return self.response.headers.get(key, "")

class PanapidaObject:
    def __init__(self, variables: ActiveEnvs):
        self._variables = variables or {}

    def get(self, var_name: str):
        return self._variables.get_env(var_name)

    def set(self, var_name: str, value):
        self._variables.set_env(var_name, value)

class ScriptRequest:
    def __init__(self, request, variables: ActiveEnvs):
        self.request = request
        self.pa = PanapidaObject(variables)
        self.request = PanapidasRequestObject(request)


    def setup_interpreter(self, response: Response = None):
        interpreter = dukpy.JSInterpreter()

        interpreter.export_function("__pa_var_get",   self.pa.get)
        interpreter.export_function("__pa_var_set",   self.pa.set)


        has_response = response is not None
        interpreter.export_function("__pa_has_response",  lambda: has_response)
        
        if (has_response):
            self.response = PanapidasResponseObject(response)
            interpreter.export_function("__pa_resp_get_url",     self.response.get_url)
            interpreter.export_function("__pa_resp_get_body",    self.response.get_body)
            interpreter.export_function("__pa_resp_get_headers", self.response.get_headers)
            interpreter.export_function("__pa_resp_header_get",  self.response.header_get)

        interpreter.export_function("__pa_req_get_url",   self.request.get_url)
        interpreter.export_function("__pa_req_set_url",   self.request.set_url)
        interpreter.export_function("__pa_req_get_method",  self.request.get_method)
        interpreter.export_function("__pa_req_get_url",     self.request.get_url)
        interpreter.export_function("__pa_req_set_url",     self.request.set_url)
        interpreter.export_function("__pa_req_get_body",    self.request.get_body)
        interpreter.export_function("__pa_req_set_body",    self.request.set_body)
        interpreter.export_function("__pa_req_get_headers", self.request.get_headers)
        interpreter.export_function("__pa_req_get_params",  self.request.get_params)
        interpreter.export_function("__pa_req_header_get",  self.request.header_get)


        interpreter.export_function("__py_print", lambda *a: print(*a))

        interpreter.evaljs("""
            var console = {
                log: function(){
                    call_python('__py_print', Array.prototype.slice.call(arguments).map(String).join(' '));
                }
            };
        """)

        interpreter.evaljs("""
            has_response = call_python('__pa_has_response');
            console.log(has_response);
            const pa = {
                variable: {
                    get:   function(name)        { return call_python('__pa_var_get', name); },
                    set:   function(name, value) { call_python('__pa_var_set', name, value); },
                },
                request: {
                    url: call_python('__pa_req_get_url'),
                    set_url: function(value) { call_python('__pa_req_set_url', value); },
                    method: call_python('__pa_req_get_method'),
                    body: call_python('__pa_req_get_body'),
                    set_body: function(value) { call_python('__pa_req_set_body', value); },
                    headers: call_python('__pa_req_get_headers'),
                    params: call_python('__pa_req_get_params'),
                },
                response: {
                    url: has_response ? call_python('__pa_resp_get_url') : null,
                    body: has_response ? call_python('__pa_resp_get_body') : null,
                    headers: has_response ? call_python('__pa_resp_get_headers') : null,
                    header_get: function(key) { return has_response ? call_python('__pa_resp_header_get', key) : null; },
                }
            }
        """)

        return interpreter

    def run(self, code, response: Response = None):
        interpreter = self.setup_interpreter(response)
        interpreter.evaljs(code)

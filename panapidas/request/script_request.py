import dukpy

class ScriptRequest:
    def __init__(self, request=None, response=None, variables=None):
        self.variables = variables
        self.request = request
        self.response = response

    def _get_var(self, var_name):
        for env in self.variables:
            if env.get('key') == var_name:
                return env.get('value')
        return None

    def _set_var(self, var_name, value):
        if self.variables is not None:
            for env in self.variables:
                if env.get('key') == var_name:
                    env['value'] = value
                    return
            self.variables.append({'key': var_name, 'value': value})

    def setup_interpreter(self):
        interpreter = dukpy.JSInterpreter()
        interpreter.export_function("pa_get_var", self._get_var)
        interpreter.export_function("pa_set_var", self._set_var)
        interpreter.export_function("__py_print", lambda *a: print(*a))

        interpreter.evaljs("""
            var console = {
                log: function(){
                    call_python('__py_print', Array.prototype.slice.call(arguments).map(String).join(' '));
                }
            };
        """)

        interpreter.evaljs("""
            function pa_get_var(var_name) {
                return call_python('pa_get_var', var_name);
            }
        """)

        interpreter.evaljs("""
            function pa_set_var(var_name, value) {
                call_python('pa_set_var', var_name, value);
            }
        """)

        return interpreter

    def run(self, code):
        interpreter = self.setup_interpreter()
        interpreter.evaljs(code)

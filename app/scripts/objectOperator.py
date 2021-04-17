class ObjectOperator:
    def __init__(self, params):
        self.params = params

    def set_param(self, param, value):
        self.params[param].value = value
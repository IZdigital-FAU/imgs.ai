class Parameterized:
    def __init__(self, params):
        self.params = params

    def set(self, params):
        for key, value in params.items():
            self.params[key].value = value
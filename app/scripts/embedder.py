from .objectOperator import ObjectOperator
from .parameters import ParameterCollection
from .reducer import Reducer


class Embedder(ObjectOperator):
    def __init__(self, params):
        super().__init__(params)
        self.reducer = None

    def hasReducer(self):
        return bool(self.reducer)

    def make_payload(self):
        payload = {
            'name': self.__class__.__name__,
            'params': {name: obj.__dict__ for name, obj in self.params.items()},
        }

        if (self.hasReducer()): payload['reducer']: self.reducer.make_payload()

        return payload


    def __str__(self):
        return self.__class__.__name__ + '(' + ', '.join([f'{key}={val}' for key, val in self.__dict__.items()]) + ')'
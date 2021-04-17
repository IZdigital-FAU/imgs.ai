from .objectOperator import ObjectOperator
from .parameters import ParameterCollection
from .reducer import Reducer


class Embedder(ObjectOperator):
    def __init__(self, params):
        super().__init__(params)
        self.reducer = Reducer()

    def make_payload(self):
        return {
            'name': self.__class__.__name__,
            'params': {name: obj.__dict__ for name, obj in self.params.items()},
            'active': False,
            'reducer': self.reducer.make_payload()
        }

    def __str__(self):
        return self.__class__.__name__ + '(' + ', '.join([f'{key}={val}' for key, val in self.__dict__.items()]) + ')'
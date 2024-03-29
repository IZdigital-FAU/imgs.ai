from .parameterized import Parameterized
from .parameters import ParameterCollection

from sklearn.decomposition import PCA
from sklearn.manifold import TSNE


class Reducer(Parameterized):
    def __init__(self, name, params=ParameterCollection.get('n_components')):
        super().__init__(params)
        self.name = name

    def make_payload(self):
        return {'name': self.name, 'params': {name: obj.__dict__ for name, obj in self.params.items()}}


class ReducerFactory:

    @staticmethod
    def create(reducer, params):
        result = False

        params = {key:int(val) for key,val in params.items()}

        if reducer.lower() == 'pca':
            result = PCA(**params)
        elif reducer.lower() == 'tsne':
            result = TSNE(**params)

        return result
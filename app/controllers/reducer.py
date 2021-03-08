from .objectOperator import ObjectOperator
from .parameters import ParameterCollection

from sklearn.decomposition import PCA
from sklearn.manifold import TSNE


class Reducer(ObjectOperator):
    def __init__(self, params=ParameterCollection.get('n_components')):
        super().__init__(params)
        self.active = False

    def make_payload(self):
        return {'name': None, 'params': {name: obj.__dict__ for name, obj in self.params.items()}, 'active': self.active}


class ReducerFactory:

    @staticmethod
    def create(reducer, params):
        result = False

        if reducer.lower() == 'pca':
            result = PCA(**params)
        elif reducer.lower() == 'tsne':
            result = TSNE(**params)

        return result
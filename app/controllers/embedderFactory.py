from .embedders.Raw import Raw
from .embedders.VGG19 import VGG19
from .embedders.Face import Face
from .embedders.Poses import Poses


class EmbedderFactory:

    names = ['raw', 'vgg19', 'face', 'poses']

    @staticmethod
    def create(embedder):
        result = False

        if embedder.lower() == 'raw':
            result = Raw()
        elif embedder.lower() == 'vgg19':
            result = VGG19()
        elif embedder.lower() == 'face':
            result = Face()
        elif embedder.lower() == 'poses':
            result = Poses()

        return result
# imgs.ai
*imgs.ai* is a fast, dataset-agnostic, visual search engine for digital art history based on neural network embeddings. Its main feature is the concept of "re-search": results from a search can immediately form the basis of another search. This allows the intuitive exploration of an image corpus, while results are continuously refined.

*imgs.ai* utilizes modern approximate k-NN algorithms via [Spotify's Annoy library](https://github.com/spotify/annoy) to deliver fast search results even for very large datasets in low-resource environments.
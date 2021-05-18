# imgs.ai
*imgs.ai* is a fast, dataset-agnostic, visual search engine for digital art history based on neural network embeddings. Its main feature is the concept of "re-search": results from a search can immediately form the basis of another search. This allows the intuitive exploration of an image corpus, while results are continuously refined.

*imgs.ai* utilizes modern approximate k-NN algorithms via [Spotify's Annoy library](https://github.com/spotify/annoy) to deliver fast search results even for very large datasets in low-resource environments.

## Requirements
| sw | version |
| :-: | :-: |
| MongoDB | 4.4.3 |
| Redis | 5.0.3 |

## Installation
~~~sh
    $ apt-get update
    $ apt-get -y install gcc g++
~~~

~~~sh
    $ pip install -r reqs.txt
~~~

## Setup
- add `config.ini`:
~~~
    MONGODB_DB=imgsai
    MONGODB_HOST=
    MONGODB_PORT=27017
    MONGO_USERNAME=
    MONGODB_PASSWORD=

    REDIS_HOST=
    REDIS_PORT=
    REDIS_PW=
~~~


## Run
use either `run.sh` or run [gunicorn](https://docs.gunicorn.org/en/latest/settings.html#settings) directly:
# imgs.ai

## Installation on remote sever

- Follow https://www.digitalocean.com/community/tutorials/initial-server-setup-with-ubuntu-18-04
- Download and install Miniconda
- (`conda install -c conda-forge jupyterlab`)
- `conda create -n imgs.ai python=3.8`
- `conda activate imgs.ai`
- `conda install pytorch torchvision cpuonly -c pytorch` (with GPU: `conda install pytorch torchvision cudatoolkit=10.1 -c pytorch`)
- `conda install -c conda-forge flask flask-cors flask-wtf flask-login flask-migrate flask-sqlalchemy email-validator nptyping`
- `conda install requests tqdm scikit-learn h5py gunicorn`
- `sudo apt install cmake` (required by face_recognition)
- `pip install pybase64 annoy face_recognition bootstrap-flask` (don't use flask-bootstrap, https://bootstrap-flask.readthedocs.io/en/latest/migrate.html)
- Install Caddy: https://caddyserver.com/docs/download
- `sudo ufw allow 80`
- `sudo ufw allow 443`
- `caddy reverse-proxy --from fau.critical.vision --to localhost:5000` (or set up Caddyfile and run with systemd service)
- Run with: `LRU_CACHE_CAPACITY=1 gunicorn -b 0.0.0.0:5000 app:app`
- Access via: https://server/user/model/neighbors

### Optional build with jemalloc

- `sudo apt install build-essential`
- Dowload jemalloc from https://github.com/jemalloc/jemalloc/releases
- Install like https://github.com/jemalloc/jemalloc/blob/dev/INSTALL.md (see also https://zapier.com/engineering/celery-python-jemalloc/)
- Run with: `LD_PRELOAD=/usr/local/lib/libjemalloc.so LRU_CACHE_CAPACITY=1 gunicorn -b 0.0.0.0:5000 app:app`

### Initialize database

- `flask db init`
- `flask db migrate`
- `flask db upgrade`

## Resources
- https://www.oreilly.com/library/view/practical-deep-learning/9781492034858/ch04.html
- https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.NearestNeighbors.html
- https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html
- https://github.com/h5py/h5py
- https://github.com/spotify/annoy
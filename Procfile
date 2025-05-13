web: gunicorn src.app:app.server --workers 4 --threads 4 --worker-tmp-dir /dev/shm
api: gunicorn api.main:app --workers 2 --threads 2 --worker-tmp-dir /dev/shm --bind 0.0.0.0:$PORT_API

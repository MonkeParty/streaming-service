# streaming-service

Докер образ MINIO (S3-хранилище)


```sh
sudo docker run -p 9000:9000 -p 9001:9001 --name minio \
    -e "MINIO_ROOT_USER=admin" \
    -e "MINIO_ROOT_PASSWORD=admin123" \
    quay.io/minio/minio server /data --console-address ":9001"
```

# How to run
```sh
uvicorn app.main:app
```
# streaming-service

# How to run
```sh
docker compose up -d
uvicorn app.main:app
```

## Convert all videos from `./full-videos` to `./hls-videos` (from `.mp4` to `.m3u8` and `.ts`)
```sh
chmod +x ./convert-mp4-to-hls.sh
./convert-mp4-to-hls.sh
```


## Load all videos from `./hls-videos` to minio

```sh
python3 ./app/load.py
```
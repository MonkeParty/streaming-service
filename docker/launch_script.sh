#!/bin/sh
python3 ./app/load.py &&
uvicorn app.main:app --reload --host ${HOST} --port ${PORT} --proxy-headers
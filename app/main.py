from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from app.config import settings

import boto3


app = FastAPI()

s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.minio_root_user,
    aws_secret_access_key=settings.minio_root_password,
    endpoint_url=settings.minio_endpoint_url,
)

MINIO_BUCKET = settings.minio_bucket


class StreamRequest(BaseModel):
    media_id: str


@app.get('/stream/{media_id}')
async def stream_media(media_id: str):
    '''
    Эндпоинт для стриминга видео по ID
    '''
    try:
        return RedirectResponse(url=s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': MINIO_BUCKET, 'Key': f'{media_id}/output.m3u8'},
        ))
    except Exception as e:
        raise HTTPException(status_code=404, detail=f'Media not found: {str(e)}')

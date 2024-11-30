from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
import boto3
import os

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    )

    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    S3_ENDPOINT_URL: str
    S3_BUCKET: str


settings = Settings()


app = FastAPI()

s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    endpoint_url=settings.S3_ENDPOINT_URL,
)
S3_BUCKET = settings.S3_BUCKET


class StreamRequest(BaseModel):
    media_id: str


@app.get('/stream/{media_id}')
async def stream_media(media_id: str):
    '''
    Эндпоинт для стриминга видео по ID
    '''
    try:
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET, 'Key': f'{media_id}/output.m3u8'},
            EXpiresIn=3600,
        )
        return RedirectResponse(url=presigned_url)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f'Media not found: {str(e)}')

    
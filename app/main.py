from fastapi import FastAPI, HTTPException, UploadFile
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


@app.get('/stream/{video_id}')
async def stream_video(video_id: int):
    '''
    Get `.m3u8` file for streaming
    '''
    try:
        return RedirectResponse(url=s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': MINIO_BUCKET, 'Key': f'{video_id}/output.m3u8'},
        ))
    except Exception as e:
        raise HTTPException(status_code=404, detail=f'Media not found: {str(e)}')

@app.get('/segment/{video_id}/{segment_name}')
async def stream_segment(video_id: int, segment_name: str):
    '''
    Get a segment named `segment_name` at video with id `video_id`
    '''
    try:
        return RedirectResponse(url=s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': MINIO_BUCKET, 'Key': f'{video_id}/{segment_name}'},
        ))
    except Exception as e:
        raise HTTPException(status_code=404, detail=f'Media not found: {str(e)}')



@app.post('/upload/{video_id}')
async def upload_video(video_id: int, file: UploadFile):
    '''
    Upload a new `.m3u8` file to MinIO under the specified media ID
    '''
    key = f'{video_id}/{file.filename}'

    try:
        s3_client.upload_fileobj(file.file, MINIO_BUCKET, key)
        return {'message': 'File uploaded successfully', 'key': key}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Failed to upload file: {str(e)}')

@app.post('/upload/{video_id}/{segment_name}')
async def upload_segment(video_id: int, segment_name: str, file: UploadFile):
    '''
    Upload a new segment file to MinIO under the specified media ID

    `file`'s name and `segment_name` must match
    '''
    if segment_name != file.filename:
        raise HTTPException(status_code=400, detail=f'file name and segment name don\'t match')

    key = f'{video_id}/{segment_name}'

    try:
        s3_client.upload_fileobj(file.file, MINIO_BUCKET, key)
        return {'message': 'File uploaded successfully', 'key': key}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Failed to upload file: {str(e)}')
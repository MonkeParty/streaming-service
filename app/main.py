import os
import subprocess
from tempfile import TemporaryDirectory

from fastapi import FastAPI, HTTPException, UploadFile, Depends, status, Response
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import boto3


from app.auth import can_user_action_on_movie, get_current_user_id
from app.config import settings



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


@app.get('/{movie_id}')
async def stream_video(
    response: Response,
    movie_id: int,
):
    '''
    Get `.m3u8` file for streaming
    '''
    if not can_user_action_on_movie(user_id, 'view', movie_id):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return

    try:
        return RedirectResponse(url=s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': MINIO_BUCKET, 'Key': f'{movie_id}/output.m3u8'},
        ))
    except Exception as e:
        raise HTTPException(status_code=404, detail=f'Media not found: {str(e)}')

@app.get('/{movie_id}/{segment_name}')
async def stream_segment(
    response: Response,
    movie_id: int,
    segment_name: str,
    user_id: int = Depends(get_current_user_id),
):
    '''
    Get a segment named `segment_name` for movie with id `movie_id`
    '''
    if not can_user_action_on_movie(user_id, 'view', movie_id):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return

    try:
        return RedirectResponse(url=s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': MINIO_BUCKET, 'Key': f'{movie_id}/{segment_name}'},
        ))
    except Exception as e:
        raise HTTPException(status_code=404, detail=f'Media not found: {str(e)}')



@app.post('/{movie_id}')
async def upload_video(
    response: Response,
    movie_id: int,
    video: UploadFile,
    user_id: int = Depends(get_current_user_id),
):
    '''
    Upload a video file, convert it to an HLS format: `.m3u8` and `.ts` and upload them to minio with id `movie_id`
    '''
    if not can_user_action_on_movie(user_id, 'edit', movie_id):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return

    with TemporaryDirectory() as temp_dir:
        input_file_path = os.path.join(temp_dir, video.filename)
        
        # save the uploaded file temporarily for further ffmpeg conversion
        with open(input_file_path, 'wb') as temp_file:
            temp_file.write(await video.read())

        output_dir = os.path.join(temp_dir, 'hls_output')
        os.makedirs(output_dir, exist_ok=True)

        output_m3u8_path = os.path.join(output_dir, 'output.m3u8')
        segment_path_pattern = os.path.join(output_dir, 'segment%d.ts')

        print(input_file_path)

        # ffmpeg command to convert to hls + ts
        ffmpeg_command = [
            'ffmpeg',
            '-i', input_file_path,
            '-c', 'copy',
            '-start_number', '0',
            '-hls_time', '10',
            '-hls_list_size', '0',
            '-hls_segment_filename', segment_path_pattern,
            '-f', 'hls',
            output_m3u8_path
        ]

        try:
            # convert to hls + ts
            subprocess.run(ffmpeg_command, check=True)
        except subprocess.CalledProcessError as e:
            raise HTTPException(status_code=500, detail=f'FFmpeg error: {e}')

        # upload m3u8 and the segments to S3
        try:
            # m3u8
            m3u8_key = f'{movie_id}/output.m3u8'
            with open(output_m3u8_path, 'rb') as m3u8_file:
                s3_client.upload_fileobj(m3u8_file, MINIO_BUCKET, m3u8_key)

            # segments
            for segment_file in os.listdir(output_dir):
                if segment_file.endswith('.ts'):
                    segment_path = os.path.join(output_dir, segment_file)
                    segment_key = f'{movie_id}/{segment_file}'
                    with open(segment_path, 'rb') as ts_file:
                        s3_client.upload_fileobj(ts_file, MINIO_BUCKET, segment_key)

            return {'msg': 'File and segments uploaded successfully'}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f'Failed to upload HLS files: {e}')

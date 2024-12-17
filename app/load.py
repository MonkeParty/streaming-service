from config import settings

import boto3
import os

s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.minio_root_user,
    aws_secret_access_key=settings.minio_root_password,
    endpoint_url=settings.minio_endpoint_url,
)

BUCKET_NAME = settings.minio_bucket
VIDEO_FOLDER = './video'


try:
    s3_client.create_bucket(Bucket=BUCKET_NAME)
    print(f'Bucket {BUCKET_NAME} created.')
except s3_client.exceptions.BucketAlreadyOwnedByYou:
    print(f'Bucket {BUCKET_NAME} already exists.')


media_id = 0

for root, dirs, files in os.walk(VIDEO_FOLDER):
    for file in files:
        file_path = os.path.join(root, file)
        key = f'{media_id}/{file}'
        s3_client.upload_file(file_path, BUCKET_NAME, key)
        media_id += 1
        print(f'File {file_path} uploaded to s3://{BUCKET_NAME}/{key}')


response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix=str(media_id))
for obj in response.get('Contents', []):
    print(obj['Key'])

response = s3_client.list_objects_v2(Bucket='movies', Prefix='12345/')
print(response)

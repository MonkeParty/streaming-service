'''
Upload local files from ./video folder to minio
'''

from config import settings

import boto3
import os

print('Loading films')

s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.minio_root_user,
    aws_secret_access_key=settings.minio_root_password,
    endpoint_url=settings.minio_endpoint_url,
)

MINIO_BUCKET = settings.minio_bucket

try:
    s3_client.create_bucket(Bucket=MINIO_BUCKET)
    print(f'Bucket \'{MINIO_BUCKET}\' created.')
except s3_client.exceptions.BucketAlreadyOwnedByYou:
    print(f'Bucket \'{MINIO_BUCKET}\' already exists.')

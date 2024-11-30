from config import settings

import boto3
import os

s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    endpoint_url=settings.S3_ENDPOINT_URL,
)

BUCKET_NAME = settings.S3_BUCKET
MEDIA_ID = "12345" 
LOCAL_DIR = "video"  

for root, dirs, files in os.walk(LOCAL_DIR):
    for file in files:
        file_path = os.path.join(root, file)
        key = f"{MEDIA_ID}/{file}"
        s3_client.upload_file(file_path, BUCKET_NAME, key)
        print(f"Загружен файл: {file_path} -> s3://{BUCKET_NAME}/{key}")


response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix=MEDIA_ID)
for obj in response.get('Contents', []):
    print(obj['Key'])

response = s3_client.list_objects_v2(Bucket="movies", Prefix="12345/")
print(response)


'''
import boto3

s3_client = boto3.client(
    "s3",
    aws_access_key_id="admin",
    aws_secret_access_key="admin123",
    endpoint_url="http://localhost:9000",
)
s3_client.create_bucket(Bucket="movies")
s3_client.put_object(
    Bucket="movies", Key="12345/output.m3u8", Body="test m3u8 content"
)
s3_client.put_object(
    Bucket="movies", Key="12345/segment0.ts", Body="test segment data"
)
'''

from fastapi.testclient import TestClient
from main import app
from moto import mock_aws
import boto3
import pytest

client = TestClient(app)

# Мокинг S3
@pytest.fixture(autouse=True)
def setup_s3():
    with mock_aws():
        s3 = boto3.client("s3")
        s3.create_bucket(Bucket="movies")

        s3.put_object(
            Bucket="movies",
            Key="12345/output.m3u8",
            Body="fake m3u8 data",
        )
        yield

def test_stream_media_success():
    response = client.get("/stream/12345")
    assert response.status_code == 200
    assert "http" in response.headers["location"]


def test_stream_media_not_found():
    response = client.get("/stream/99999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Media not found: An error occurred (NoSuchKey) when calling the GetObject operation: The specified key does not exist."}

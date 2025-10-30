import os
from google.cloud import storage
from datetime import timedelta

BUCKET = os.environ.get("GCS_BUCKET")

_client = None


def client():
    global _client
    if _client is None:
        _client = storage.Client(project=os.environ.get("GCP_PROJECT_ID"))
    return _client


def upload_file(fileobj, dest_path: str, content_type: str | None = None) -> str:
    bucket = client().bucket(BUCKET)
    blob = bucket.blob(dest_path)
    blob.upload_from_file(fileobj, content_type=content_type)
    # blob.make_private()  # keep private by default
    return f"gs://{BUCKET}/{dest_path}"


def download_to_path(gcs_uri: str, local_path: str):
    assert gcs_uri.startswith("gs://"), "Expect gs:// URI"
    _, rest = gcs_uri.split("gs://", 1)
    bucket_name, blob_name = rest.split("/", 1)
    bucket = client().bucket(bucket_name)
    blob = bucket.blob(blob_name)
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    blob.download_to_filename(local_path)


def generate_signed_url(gcs_uri: str, minutes: int = 15) -> str:
    assert gcs_uri.startswith("gs://")
    _, rest = gcs_uri.split("gs://", 1)
    bucket_name, blob_name = rest.split("/", 1)
    bucket = client().bucket(bucket_name)
    blob = bucket.blob(blob_name)
    return blob.generate_signed_url(expiration=timedelta(minutes=minutes), method="GET")

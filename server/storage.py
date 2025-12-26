import os
from google.cloud import storage
from datetime import timedelta

# Bucket name from environment variable
BUCKET = os.environ.get("GCS_BUCKET")

_client = None


def client():
    """
    Returns a singleton GCS client.
    """
    global _client
    if _client is None:
        _client = storage.Client(project=os.environ.get("GCP_PROJECT_ID"))
    return _client


def upload_file(fileobj, dest_path: str, content_type: str | None = None) -> str:
    """
    Uploads a file object to Google Cloud Storage.
    Returns a gs:// URI.
    """
    bucket = client().bucket(BUCKET)
    blob = bucket.blob(dest_path)
    blob.upload_from_file(fileobj, content_type=content_type)

    # Keep private by default
    # blob.make_private()

    return f"gs://{BUCKET}/{dest_path}"


def download_to_path(gcs_uri: str, local_path: str):
    """
    Downloads a GCS file to a local path.
    """
    assert gcs_uri.startswith("gs://"), "Expect gs:// URI"

    _, rest = gcs_uri.split("gs://", 1)
    bucket_name, blob_name = rest.split("/", 1)

    bucket = client().bucket(bucket_name)
    blob = bucket.blob(blob_name)

    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    blob.download_to_filename(local_path)


def generate_signed_url(gcs_uri: str, minutes: int = 15) -> str:
    """
    Generates a V4 signed URL for secure access to a private GCS object.
    This version fixes:
    - PDF.js loading errors
    - Signature corruption (%253D)
    - Browser iframe encoding issues
    """
    assert gcs_uri.startswith("gs://"), "Invalid GCS URI"

    # Extract bucket + blob path
    _, rest = gcs_uri.split("gs://", 1)
    bucket_name, blob_name = rest.split("/", 1)

    bucket = client().bucket(bucket_name)
    blob = bucket.blob(blob_name)

    # ⭐ Use V4 signing – required for iframe/pdf.js and modern GCS auth
    url = blob.generate_signed_url(
        version="v4",
        expiration=timedelta(minutes=minutes),
        method="GET",
    )

    return url

# Replace these with your values

PROJECT_ID="your-gcp-project-id"
BUCKET_NAME="smart-ocr-bucket"
REGION="us-central1"

gcloud auth login
gcloud config set project $PROJECT_ID

gcloud storage buckets create gs://$BUCKET_NAME \
    --project=$PROJECT_ID \
 --location=$REGION \
 --uniform-bucket-level-access

gcloud iam service-accounts create ocr-service-account \
 --display-name="OCR Service Account"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:ocr-service-account@$PROJECT_ID.iam.gserviceaccount.com" \
 --role="roles/storage.objectAdmin"

gcloud iam service-accounts keys create ./secrets/gcp-sa.json \
 --iam-account=ocr-service-account@$PROJECT_ID.iam.gserviceaccount.com

export GOOGLE_APPLICATION_CREDENTIALS=./secrets/gcp-sa.json
gsutil ls -p $PROJECT_ID gs://$BUCKET_NAME

and download screts folder

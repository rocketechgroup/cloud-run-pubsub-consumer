# Cloud Run PubSub Consumer

A repo to test out using Cloud Run Job as PubSub Consumer

## Global vars

```
export PROJECT_ID=[PROJECT_ID]
export REGION=[REGION]
export CONSUMER_SA_NAME=[CONSUMER_SA_NAME]
export TOPIC_NAME=[TOPIC_NAME]
export SUBSCRIPTION_ID=[SUBSCRIPTION_ID]
```

## Create PubSub Resource

Topic

```
gcloud pubsub topics create ${TOPIC_NAME} --project=${PROJECT_ID}
```

Subscription

```
gcloud pubsub subscriptions create ${SUBSCRIPTION_ID} --topic=${TOPIC_NAME} --project=${PROJECT_ID}
```

## Create Service Account and assign roles
## Create Service Account and assign roles
> `roles/pubsub.subscriber` is just for convenience, for PROD do not use project level permissions, grant permission to the specific Subscription

```
gcloud iam service-accounts create ${CONSUMER_SA_NAME}
gcloud projects add-iam-policy-binding ${PROJECT_ID} --member "serviceAccount:${CONSUMER_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" --role "roles/pubsub.subscriber"
gcloud projects add-iam-policy-binding ${PROJECT_ID} --member "serviceAccount:${CONSUMER_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" --role "roles/logging.logWriter"
```

## Build & Deploy the consumer to Cloud Run

Additional Env vars required
```
export AF_REPO_NAME=[AF_REPO_NAME]
export IMAGE_NAME=[IMAGE_NAME]
export COMMIT_SHA=$(git rev-parse --short=8 HEAD)
```

### Create Artifact Registry repo

```
gcloud artifacts repositories create ${AF_REPO_NAME} --repository-format=docker --location=${REGION}
```

### Build & Deploy

#### Build Image

```
gcloud builds submit --config cloudbuild_build_image.yaml --substitutions _PROJECT_ID=${PROJECT_ID},_REPO_NAME=${AF_REPO_NAME},_IMAGE_NAME=${IMAGE_NAME},_COMMIT_SHA=${COMMIT_SHA}
```

#### Deploy Cloud Run Job

Additional Env vars required
```
export NUM_TASKS=3
```

Create
```
gcloud builds submit --config cloudbuild_deploy_job.yaml --substitutions _PROJECT_ID=${PROJECT_ID},_REPO_NAME=${AF_REPO_NAME},_IMAGE_NAME=${IMAGE_NAME},_COMMIT_SHA=${COMMIT_SHA},_SUBSCRIPTION_ID=${SUBSCRIPTION_ID},_NUM_TASKS=${NUM_TASKS},_REGION=${REGION},_SA=${CONSUMER_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com
```

Update
```
gcloud builds submit --config cloudbuild_update_job.yaml --substitutions _PROJECT_ID=${PROJECT_ID},_REPO_NAME=${AF_REPO_NAME},_IMAGE_NAME=${IMAGE_NAME},_COMMIT_SHA=${COMMIT_SHA},_SUBSCRIPTION_ID=${SUBSCRIPTION_ID},_NUM_TASKS=${NUM_TASKS},_REGION=${REGION},_SA=${CONSUMER_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com
```

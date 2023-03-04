# Cloud Run PubSub Consumer

A repo to test out using Cloud Run Job as PubSub Consumer

## Global vars

export PROJECT_ID=${PROJECT_ID}

## Create PubSub Resource

Topic

```
gcloud pubsub topics create [TOPIC_NAME] --project=${PROJECT_ID}
```

Subscription

```
gcloud pubsub subscriptions create [SUBSCRIPTION_NAME] --topic=[TOPIC_NAME] --project=${PROJECT_ID}
```

## Create Service Account and assign roles

```
gcloud iam service-accounts create cloud-run-job-pubsub-consumer
gcloud projects add-iam-policy-binding ${PROJECT_ID} --member "serviceAccount:[SERVICE_ACCOUNT_EMAIL]" --role "roles/pubsub.subscriber"
gcloud projects add-iam-policy-binding ${PROJECT_ID} --member "serviceAccount:[SERVICE_ACCOUNT_EMAIL]" --role "roles/logging.logWriter"
```

## Build & Deploy

Create Artifact Registry repo

```
gcloud artifacts repositories create pubsub-consumers --repository-format=docker --location=europe-west2
```

Build & Deploy

```
gcloud builds submit --config cloudbuild.yaml --substitutions _PROJECT_ID=${PROJECT_ID},_REPO_NAME=[AF_REPO_NAME],_IMAGE_NAME=[IMAGE_NAME],_COMMIT_SHA=${git rev-parse --short=8 HEAD}
```
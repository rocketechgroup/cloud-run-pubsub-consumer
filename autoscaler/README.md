# The Auto Scaler
The auto Scaler is designed to track the oldest unacked message to determine if the consumer needs to be scaled up or not, 
if it does, the autoscaler will adjust the total number of tasks in the Cloud Run Job to the max task set, otherwise it will revert to the default.

The consumer will function without the autoscaler

## Global vars
```
export PROJECT_ID=[PROJECT_ID]
export PROJECT_NUMBER=[PROJECT_NUMBER]
export REGION=[REGION]
export AUTOSCALER_SA_NAME=[AUTOSCALER_SERVICE_ACCOUNT_NAME]
export SUBSCRIPTION_ID=[SUBSCRIPTION_ID]
```

## Create Service Account and assign roles

```
gcloud iam service-accounts create ${AUTOSCALER_SA_NAME}
gcloud projects add-iam-policy-binding ${PROJECT_ID} --member "serviceAccount:${AUTOSCALER_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" --role "roles/monitoring.viewer"
gcloud projects add-iam-policy-binding ${PROJECT_ID} --member "serviceAccount:${AUTOSCALER_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" --role "roles/logging.logWriter"
gcloud projects add-iam-policy-binding ${PROJECT_ID} --member "serviceAccount:${AUTOSCALER_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" --role "roles/run.developer"
```

## Build & Deploy the autoscaler to Cloud Function
Give cloudbuild permission to build and deploy cloud function
```
gcloud projects add-iam-policy-binding ${PROJECT_ID} --member=serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com --role=roles/cloudfunctions.developer

```
Build & deploy
```
gcloud builds submit --config cloudbuild.yaml --substitutions _PROJECT_ID=${PROJECT_ID},_SUBSCRIPTION_ID=${SUBSCRIPTION_ID},_REGION=${REGION},_AUTOSCALER_SERVICE_ACCOUNT=${AUTOSCALER_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com
```
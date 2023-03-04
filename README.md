# Cloud Run PubSub Consumer
A repo to test out using Cloud Run Job as PubSub Consumer

## Create PubSub 
Topic
```
gcloud pubsub topics create [TOPIC_NAME] --project=[PROJECT_ID]
```

Subscription
```
gcloud pubsub subscriptions create [SUBSCRIPTION_NAME] --topic=[TOPIC_NAME] --project=[PROJECT_ID]
```

## Build & Deploy
gcloud builds submit --config cloudbuild.yaml --substitutions _PROJECT_ID=MY_PROJECT_ID,FOO=bar
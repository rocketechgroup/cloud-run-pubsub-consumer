import os
import time

import requests
import json

from google.cloud import logging
from google.auth import default
from google.cloud import monitoring_v3
from google.auth.transport.requests import Request

logging_client = logging.Client()
logger = logging_client.logger(name='cloud-run-pubsub-consumer-autoscaler')

PROJECT_ID = os.environ.get('PROJECT_ID')
SUBSCRIPTION_ID = os.environ.get('SUBSCRIPTION_ID')
LOCATION = 'europe-west2'
default_task_count = 10
max_task_count = 100


# This function use the seconds of the oldest unacked message to measure if there are not enough resources
def subscription_delay_is_high(max_seconds=150):
    client = monitoring_v3.MetricServiceClient()
    metric_type = 'pubsub.googleapis.com/subscription/oldest_unacked_message_age'
    now = time.time()
    seconds = int(now)
    nanos = int((now - seconds) * 10 ** 9)
    interval = monitoring_v3.TimeInterval(
        {
            "end_time": {"seconds": seconds, "nanos": nanos},
            "start_time": {"seconds": (seconds - 120), "nanos": nanos},
        }
    )
    query_params = {
        'name': f'projects/{PROJECT_ID}',
        "filter": f'metric.type = "{metric_type}" AND resource.labels.subscription_id = "{SUBSCRIPTION_ID}"',
        'interval': interval
    }

    # Make the API request
    response = client.list_time_series(**query_params)

    try:
        latency = response.time_series[0].points[0].value.int64_value
        logger.log_struct(
            {
                "message": f"Current latency of oldest message is: {latency}s."
            },
            severity="INFO"
        )

        if latency > max_seconds:
            return True
    except IndexError:
        logger.log_struct(
            {
                "message": "Metric doesn't exist."
            },
            severity="WARNING"
        )
    return False


def autoscale(job):
    # Obtain the default credentials
    credentials, project_id = default()

    # Refresh the credentials if necessary
    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())

    # Obtain the access token from the credentials
    access_token = credentials.token

    # Define the URL of the Cloud Run service
    job_name = f'projects/{PROJECT_ID}/locations/{LOCATION}/jobs/{job}'
    job_url = f'https://europe-west2-run.googleapis.com/v2/{job_name}'

    # Define the access token
    headers = {'Authorization': f'Bearer {access_token}'}

    # Get the existing job
    response = requests.get(job_url, headers=headers)
    response.raise_for_status()

    job_entity = json.loads(response.content.decode('utf-8'))

    if subscription_delay_is_high():
        target_task_count = max_task_count
    else:
        target_task_count = default_task_count

    if job_entity['template']['taskCount'] == target_task_count:
        logger.log_struct(
            {
                "message": "Resource is sufficient, no nothing."
            },
            severity="INFO"
        )
    else:
        # Autoscale up or down by updating task count
        job_entity['template']['taskCount'] = target_task_count

        # Update the task count (scale up or down)
        response = requests.patch(job_url, json=job_entity, headers=headers)
        response.raise_for_status()
        logger.log_struct(
            {
                "message": f"Changed task count to: {target_task_count}"
            },
            severity="INFO"
        )


autoscale(job='cloud-run-pubsub-consumer')

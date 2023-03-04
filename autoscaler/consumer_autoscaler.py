import os
import requests
import json

from google.auth import default
from google.auth.transport.requests import Request

PROJECT_ID = os.environ.get('PROJECT_ID')
LOCATION = 'europe-west2'
new_task_count = 10

# Obtain the default credentials
credentials, project_id = default()

# Refresh the credentials if necessary
if credentials.expired and credentials.refresh_token:
    credentials.refresh(Request())

# Obtain the access token from the credentials
access_token = credentials.token

# Define the URL of the Cloud Run service
job = 'cloud-run-pubsub-consumer'
job_name = f'projects/{PROJECT_ID}/locations/{LOCATION}/jobs/{job}'
job_url = f'https://europe-west2-run.googleapis.com/v2/{job_name}'

# Define the access token
headers = {'Authorization': f'Bearer {access_token}'}

# Get the existing job
response = requests.get(job_url, headers=headers)
response.raise_for_status()

job_entity = json.loads(response.content.decode('utf-8'))

# Update task count
job_entity['template']['taskCount'] = new_task_count

# Update the task count (scale up or down)
response = requests.patch(job_url, json=job_entity, headers=headers)
response.raise_for_status()

import os

from concurrent.futures import TimeoutError
from google.cloud import pubsub_v1
from google.cloud import logging

PROJECT_ID = os.environ.get('PROJECT_ID')
SUBSCRIPTION_ID = os.environ.get('SUBSCRIPTION_ID')

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_ID)

logging_client = logging.Client()
logger = logging_client.logger(name='cloud-run-pubsub-consumer')


def callback(message) -> None:
    message.ack()


# Limit the subscriber to only have ten outstanding messages at a time.
flow_control = pubsub_v1.types.FlowControl(max_messages=50)

streaming_pull_future = subscriber.subscribe(
    subscription_path, callback=callback, flow_control=flow_control
)
logger.log_struct(
    {
        "message": f'Listening for messages on {subscription_path}'
    },
    severity="INFO"
)

# Wrap subscriber in a 'with' block to automatically call close() when done.
with subscriber:
    try:
        # set timeout to 5 minutes
        streaming_pull_future.result(timeout=60 * 2)
    except TimeoutError:
        streaming_pull_future.cancel()  # Trigger the shutdown.

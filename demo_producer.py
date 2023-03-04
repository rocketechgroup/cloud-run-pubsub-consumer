import os
import logging
import json

from concurrent import futures
from google.cloud import pubsub_v1

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

PROJECT_ID = os.environ.get('PROJECT_ID')
TOPIC_ID = os.environ.get('TOPIC_ID')
publish_futures = []


# Resolve the publish future in a separate thread.
def callback(future) -> None:
    message_id = future.result()
    logging.info(f"Message ID: {message_id}")


batch_settings = pubsub_v1.types.BatchSettings(
    max_bytes=2048000,  # One kilobyte
    max_latency=5,  # One second
)

publisher_options = pubsub_v1.types.PublisherOptions(
    flow_control=pubsub_v1.types.PublishFlowControl(
        message_limit=500,
        byte_limit=2 * 1024 * 1024,
        limit_exceeded_behavior=pubsub_v1.types.LimitExceededBehavior.BLOCK,
    ),
)

publisher = pubsub_v1.PublisherClient(batch_settings=batch_settings, publisher_options=publisher_options)
topic_name = 'projects/{project_id}/topics/{topic}'.format(
    project_id=PROJECT_ID,
    topic=TOPIC_ID,
)
for i in range(1, 1000):
    msg = json.dumps({'name': f'Message count: {i}'}).encode('utf-8')
    publish_future = publisher.publish(topic_name, msg)

    # Non-blocking. Allow the publisher client to batch multiple messages.
    publish_future.add_done_callback(callback)
    publish_futures.append(publish_future)

futures.wait(publish_futures, return_when=futures.ALL_COMPLETED)

print(f"Published messages with batch settings to {topic_name}.")

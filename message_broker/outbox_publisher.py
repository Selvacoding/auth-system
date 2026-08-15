import time

from db.database import (
    get_unpublished_events,
    mark_event_as_published
)

from message_broker.producer import publish_event


def process_outbox():
    events = get_unpublished_events()
    for event in events:
        try:
            publish_event(event_id=event["id"], event_type=event["event_type"], payload=event["payload"])
            mark_event_as_published(event["id"])
            print(f"Outbox event {event['id']} published successfully.")

        except Exception as e:
            print(f"Failed to publish outbox event {event['id']}: {e}")

if __name__ == "__main__":
    print("Outbox publisher started...")
    while True:
        process_outbox()
        time.sleep(5)
    
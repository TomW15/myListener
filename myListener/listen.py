import json
from loguru import logger
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from myDb.postgres import engines

from myListener.actions import batch
from myListener import notifications


def listen_for_updates(database: str) -> None:
    """
    Listens for database notifications on a PostgreSQL channel and executes scripts based on the payload.

    Args:
        database (str): The name of the PostgreSQL database to connect to.
    """

    notifications.push_bullet.send(
        title=f"Listening to {database!r} updates",
        body=f"Listening to {database!r} updates",
    )

    try:
        # Connect to the database

        logger.info("Connecting to the database...")
        connection = engines.connect_to_database(database=database)
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = connection.cursor()

        # Listen for the notification
        logger.info("Setting up LISTEN on channel 'value_updated'.")
        cursor.execute("LISTEN value_updated;")
        logger.info("Listening for updates on the channel 'value_updated'...")

        try:
            while True:

                # Poll for notifications
                connection.poll()
                while connection.notifies:

                    notify = connection.notifies.pop(0)
                    payload = notify.payload

                    logger.info(f"Notification received: {payload}")

                    # Parse the JSON payload
                    try:
                        data = json.loads(payload)
                    except (json.JSONDecodeError, KeyError) as e:
                        logger.error(f"Failed to parse payload: {payload}. Error: {e}")
                        continue

                    if batch.is_type(data=data):
                        logger.info("Received payload with bat files to run")
                        batch.run(data=data)
                    else:
                        continue

                    # Send notifaction/acknowledgment to requester
                    # i.e. email / push notification
                    username = data.get("run_user")
                    if username is None:
                        continue

                    try:
                        notifier, kwargs = notifications.get(database=database, username=username)
                    except Exception as e:
                        logger.exception(e)
                        continue

                    if notifier is None:
                        logger.warning(f"No notification settings for {username!r} on {database!r}.")
                        continue
                    elif not hasattr(notifications, notifier):
                        logger.warning(f"'notifications' does not have attribute {notifier!r}")
                        continue

                    getattr(notifications, notifier).send(
                        title=f"Received order to run {data.get('name')!r} from {username!r}",
                        body=f"Received payload={data} from {username!r}.",
                        **kwargs,
                    )

                    logger.info("Notification handled.")

        except KeyboardInterrupt:
            logger.info("Stopped listening due to KeyboardInterrupt.")
        finally:
            cursor.close()
            connection.close()
            logger.info("Database connection closed.")

    except Exception as e:
        logger.error(f"Failed to connect to the database or set up listener. Error: {e}")

    return


def main():

    # Entry point for the script
    database_name = "trading"  # Replace with your actual database name
    logger.info(f"Starting listener for database: {database_name}")
    listen_for_updates(database=database_name)

    return


if __name__ == "__main__":
    main()

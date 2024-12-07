import configparser
from pushbullet import Pushbullet

from myDb import credential_loader

SECTION: str = "pushbullet"
KEY: str = "api_key"


def send(title: str, body: str, nickname: str = None) -> None:

    def get_api_key() -> str:
        try:

            return credential_loader.load(section=SECTION, key=KEY)
        except KeyError:
            config = configparser.ConfigParser()
            config.read(f"{SECTION}.ini")
            return config["api_keys"][KEY]

    # Fetch API Key
    api_key = get_api_key()

    # Initialize Push Bullet
    pb = Pushbullet(api_key)

    # Send a push notification
    pb.push_note(
        title=title,
        body=body,
        device=None if nickname is None else pb.get_device(nickname=nickname),
    )

    return


def main():

    send(
        title="Test",
        body="Testing sending a notification",
        nickname="pixel",
    )

    return


if __name__ == "__main__":
    main()

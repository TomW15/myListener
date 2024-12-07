import typing as t
from myDb.postgres import Read


def get(database: str, username: str) -> t.Tuple[str | t.Dict[str, t.Any]] | None:

    df = Read(database=database).select(table="notifications", username=username)

    if df.shape[0] == 0:
        return None, None # noqa

    notifier: str = df.loc[username, "notifier"]
    data: t.Dict[str, t.Any] = df.loc[username, "data"]

    return notifier, data # noqa


if __name__ == '__main__':
    get(database="trading", username="pixel")

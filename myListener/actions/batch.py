from loguru import logger
import subprocess
import typing as t

PATH: str = "path"
FILE: str = "file"
BAT_FILE_EXTENSION: str = ".bat"


def is_type(data: t.Dict) -> bool:
    if PATH not in data:
        return False
    if FILE not in data:
        return False
    return BAT_FILE_EXTENSION in data[FILE]


def run(data: t.Dict) -> None:

    def get_processes() -> t.List[str]:

        # Get paths and files from json
        paths = data[PATH]
        files = data["file"]

        # Split on ,
        paths = paths.split(",")
        files = files.split(",")

        # If length of paths and files match: zip, combine and return
        if len(paths) == len(files):
            return [fr"{path}/{file}" for path, file in zip(paths, files)]
        assert (len(paths) == 1) or (len(files) == 1), "Size of paths and files unequal and neither are 1"
        paths = paths * len(files)
        files = files * len(paths)
        return [fr"{path}/{file}" for path, file in zip(paths, files)]

    logger.info(f"Attempting to run batch files.")
    processes = get_processes()
    logger.info(f"Received {len(processes)} to run.")

    for process in processes:

        if not process.endswith(BAT_FILE_EXTENSION):
            logger.info(f"Received process without Batch File Extension ({BAT_FILE_EXTENSION!r})")
            continue

        logger.info(f"Running {process!r}")
        try:
            subprocess.run(f'start cmd /k "{process}"', shell=True)
        except Exception as e:
            logger.warning(f"Error raised when trying to run {process=!r} - {e}")

    logger.info(f"Finished starting batch files.")

    return


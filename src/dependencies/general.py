"""General utility functions."""


import json
import os
from functools import wraps
from typing import Callable, Union, Dict
from time import time


def read_json_local(path: str):
    """Read JSON from local path."""
    with open(path, "r") as f:
        file = json.load(f)
    return file


def load_configuration_file(path: str) -> Union[bool, Dict[str, Union[str, int]]]:
    """
    Checks if the file that's searched (specifically options in JSON)
    and reads the file to memory if found and content is correct.
    """
    if os.path.isfile(path):
        optionsFile = read_json_local(path)
        if len(optionsFile) == 0:
            print("*\nEmpty options file.")
            return False
        else:
            return optionsFile
    else:
        print("*\nMissing or wrongly named options file.")
        return False


def timing(f: Callable) -> None:
    """Timing decorator for funcctions."""

    @wraps(f)
    def wrap(*args, **kw):
        ts = time()
        result = f(*args, **kw)
        te = time()
        print(f"Elapsed time: {round((te - ts)/ 60, 2):,} min")
        return result

    return wrap

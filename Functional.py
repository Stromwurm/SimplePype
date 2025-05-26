from typing import Union
from multiprocessing.connection import Connection, PipeConnection


def _to_pipe_connection(obj: Union[Connection, int, str], *, readable: bool, writable: bool) -> Connection:
    """
    Normalize a Connection object or raw handle (int or str) into a PipeConnection.
    On Windows, wrap the raw handle into a PipeConnection with correct read/write flags.
    """
    if isinstance(obj, Connection):
        return obj
    try:
        handle = int(obj)
    except ValueError:
        raise TypeError(f"Invalid pipe handle: {obj}")
    # Reconstruct a PipeConnection from a raw OS handle
    return PipeConnection(handle, readable, writable)

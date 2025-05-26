
import uuid

_handle_registry = {}

def _register_handle(conn):
    handle_id = str(uuid.uuid4())
    _handle_registry[handle_id] = conn
    return handle_id


def _get_handle(conn_id):
    try:
        return _handle_registry[conn_id]
    except KeyError:
        raise ValueError(f"Invalid pipe handle: {conn_id}")


def _unregister_handle(conn_id):
    if conn_id in _handle_registry:
        del _handle_registry[conn_id]

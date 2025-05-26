import sys
import time
sys.path.append(R".\SimplePype")

from ClientMessage import ClientMessage
from LocalClient import LocalClient
from Functional import _register_handle, _unregister_handle, _get_handle

import threading
from multiprocessing import Pipe

class LocalServer:
    def __init__(self):
        # Create two unidirectional pipes: server->client and client->server
        self._pipe_out_client, self._pipe_out_server = Pipe(duplex=False)
        self._pipe_in_server, self._pipe_in_client = Pipe(duplex=False)

        self.NewMessage = []  # Handlers: (sender, ClientMessage)
        self.ServerMessage = []  # Handlers: (sender, message:str)
        self._stop_event = threading.Event()
        self._listen_thread = None

    @property
    def IsConnected(self):
        return not (self._pipe_out_server.closed or self._pipe_in_server.closed)

    def Listen(self):
        if not self.IsConnected:
            raise RuntimeError("Client is not connected!")
        def _run():
            self._invoke_event(self.ServerMessage, "Server listening...")
            while not self._stop_event.is_set():
                try:
                    if self._pipe_in_server.poll():
                        msg = self._pipe_in_server.recv()
                        cmsg = ClientMessage(msg)
                        self._invoke_event(self.NewMessage, cmsg)
                except Exception as ex:
                    self._invoke_event(self.ServerMessage, f"SERVER {ex}")
                time.sleep(0.025)
        self._listen_thread = threading.Thread(target=_run, daemon=True)
        self._listen_thread.start()

    def Write(self, msg: str):
        if not self.IsConnected:
            raise RuntimeError("No client connected!")
        self._pipe_out_server.send(msg)

    def GetPipeHandles(self):
        """
        Returns a tuple of string handles: (client_recv_handle, client_send_handle)
        """
        recv_id = _register_handle(self._pipe_out_client)
        send_id = _register_handle(self._pipe_in_client)
        return recv_id, send_id

    def DisposeLocalCopyOfClientHandle(self, recv_id, send_id):
        _unregister_handle(recv_id)
        _unregister_handle(send_id)

    def GetClient(self, recv_handle_id: str = None, send_handle_id: str = None):
        """
        Create LocalClient from string handle IDs. If none provided, use fresh GetPipeHandles.
        """
        if recv_handle_id is None or send_handle_id is None:
            recv_handle_id, send_handle_id = self.GetPipeHandles()
        conn_recv = _get_handle(recv_handle_id)
        conn_send = _get_handle(send_handle_id)
        client = LocalClient(recv_handle_id, send_handle_id, conn_recv, conn_send)
        # Once client is set up, server can drop its local copy
        client.HandleDisposeReady.append(lambda sender: self.DisposeLocalCopyOfClientHandle(recv_handle_id, send_handle_id))
        return client

    def Dispose(self):
        self._stop_event.set()
        if self._listen_thread:
            self._listen_thread.join()
        self._pipe_out_server.close()
        self._pipe_in_server.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.Dispose()

    def _invoke_event(self, handlers, *args):
        for h in handlers:
            try:
                h(self, *args)
            except Exception:
                pass



import time
import sys
sys.path.append(R".\SimplePype")

from ServerMessage import ServerMessage
import threading

class LocalClient:
    def __init__(self, handle_in, handle_out):
        self._pipe_in = handle_in
        self._pipe_out = handle_out
        self.NewMessage = []  # Handlers: (sender, ServerMessage)
        self.ClientMessage = []  # Handlers: (sender, message:str)
        self.HandleDisposeReady = []  # Handlers: (sender)
        self._stop_event = threading.Event()
        self._listen_thread = None

    @property
    def IsConnected(self):
        return not (self._pipe_in.closed or self._pipe_out.closed)

    def Listen(self):
        # Notify server that handles can be disposed
        self._invoke_event(self.HandleDisposeReady)
        if not self.IsConnected:
            raise RuntimeError("Client is not connected!")
        def _run():
            self._invoke_event(self.ClientMessage, "Client listening...")
            while not self._stop_event.is_set():
                try:
                    if self._pipe_in.poll():
                        msg = self._pipe_in.recv()
                        smsg = ServerMessage(msg)
                        self._invoke_event(self.NewMessage, smsg)
                except Exception as ex:
                    self._invoke_event(self.ClientMessage, f"CLIENT {ex}")
                time.sleep(0.025)
        self._listen_thread = threading.Thread(target=_run, daemon=True)
        self._listen_thread.start()

    def Write(self, msg: str):
        if not self.IsConnected:
            raise RuntimeError("Client is not connected!")
        self._pipe_out.send(msg)

    def Dispose(self):
        self._stop_event.set()
        if self._listen_thread:
            self._listen_thread.join()
        self._pipe_out.close()

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
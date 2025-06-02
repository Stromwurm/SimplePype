import time
import sys
import io
import os
sys.path.append(R".\ServerMessage.py")

from .ServerMessage import ServerMessage

import threading
import msvcrt

class LocalClient:

    def __init__(self, server_in: int, server_out: int):

        hIn = msvcrt.open_osfhandle(server_in, os.O_TEXT)
        hOut = msvcrt.open_osfhandle(server_out, os.O_TEXT)
        self.pipe_out = open(hIn, 'w', closefd=False, newline="\n", encoding="UTF-8")
        self.pipe_in = open(hOut, 'r', closefd=False, newline="\n", encoding="UTF-8")

        self.NewMessage = []
        self.ClientMessage = []
        self.stop_event = threading.Event()
        self.listen_thread = None

    @property
    def IsConnected(self):
        return not (self.pipe_out.closed or self.pipe_in.closed)
    
    def _ClientMessage(self, msg: str) -> None:
        for handlers in self.ClientMessage:
            handlers(f"CLIENT SAID: {msg}")

    def _NewMessage(self, msg: str) -> None:
        srvmsg = ServerMessage(msg)
        for h in self.NewMessage:
            h(srvmsg)

    def Listen(self):

        while (not self.IsConnected):
            self._ClientMessage("Not connected to the server...")
            time.sleep(0.25)
        
        def run():
            self._ClientMessage("Client connected, listening...")

            while (not self.stop_event.is_set()):

                time.sleep(0.025)

                try:
                    pipe_content = self.pipe_in.readline()
                    self._NewMessage(pipe_content)

                except Exception as ex:
                    self._ClientMessage(str(ex))
        
        self.listen_thread = threading.Thread(target=run, daemon=True)
        self.listen_thread.start()

    def Write(self, msg: str) -> None:
        self.pipe_out.write(msg)
        self.pipe_out.flush()
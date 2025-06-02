import sys
import time
import os
file_dir = os.path.dirname(__file__)
sys.path.append(Rf"{file_dir}")

from .ClientMessage import ClientMessage
from .LocalClient import LocalClient

import threading
from multiprocessing import Pipe
import io
import msvcrt

class LocalServer:

    def __init__(self):
        r, w = os.pipe()
        self.pipe_out = open(w, 'w', closefd=False, newline="\n", encoding="UTF-8")
        self.pipe_in = open(r, 'r', closefd=False, newline="\n", encoding="UTF-8")
        self.NewMessage = []
        self.ServerMessage = []
        self.stop_event = threading.Event()
        self.listen_thread = None

        os.set_inheritable(r, True)
        os.set_inheritable(w, True)


    @property
    def IsConnected(self):
        return not (self.pipe_out.closed or self.pipe_in.closed)
    
    def _ClientMessage(self, msg: str) -> None:
        for handlers in self.ServerMessage:
            handlers(f"CLIENT SAID: {msg}")

    def _NewMessage(self, msg: str) -> None:
        srvmsg = ClientMessage(msg)
        for h in self.NewMessage:
            h(srvmsg)

    def Listen(self):

        while (not self.IsConnected):
            self._ClientMessage("No client connected...")
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
        
    def GetPipeHandles(self) -> tuple[int, int]:
        pOut = msvcrt.get_osfhandle(self.pipe_out.fileno())
        pIn = msvcrt.get_osfhandle(self.pipe_in.fileno())
        return (pOut, pIn)
from datetime import datetime

class ClientMessage:
    def __init__(self, message: str):
        self.ReceivedAt = datetime.now()
        self.MessageType = int(message[:6])
        self.Message = message[6:]
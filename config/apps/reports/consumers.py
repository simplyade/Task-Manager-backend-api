import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ReportConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send(json.dumps({"message": "Connected to report updates"}))

    async def disconnect(self, close_code):
        print(f"Disconnected with code {close_code}")

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message", "No message received")
        
        await self.send(text_data=json.dumps({"response": f"You said: {message}"}))

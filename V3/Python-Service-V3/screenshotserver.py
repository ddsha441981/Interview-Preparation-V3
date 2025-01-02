import asyncio
import websockets

async def handle_connection(websocket, path):
    async for message in websocket:
        with open('screenshot.png', 'wb') as f:
            f.write(message)
        print("Screenshot received and saved.")

start_server = websockets.serve(handle_connection, "localhost", 8000)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

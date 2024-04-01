import asyncio
import logging
import websockets
import names
from websockets import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosedOK

from logger import add_logging
from request import send_request

logging.basicConfig(level=logging.INFO)


class Server:
    clients = set()

    async def register(self, ws: WebSocketServerProtocol):
        ws.name = names.get_full_name()
        self.clients.add(ws)
        logging.info(f'{ws.remote_address} connects')

    async def unregister(self, ws: WebSocketServerProtocol):
        self.clients.remove(ws)
        logging.info(f'{ws.remote_address} disconnects')

    async def send_to_clients(self, message: str):
        if self.clients:
            [await client.send(message) for client in self.clients]

    async def ws_handler(self, ws: WebSocketServerProtocol):
        await self.register(ws)
        try:
            await self.distrubute(ws)
        except ConnectionClosedOK:
            pass
        finally:
            await self.unregister(ws)

    async def distrubute(self, ws: WebSocketServerProtocol):
        async for message in ws:
            if message.startswith("exchange"):
                if not message.endswith("exchange"):
                    days = int(message.split(' ')[1])
                    response = await send_request(days)
                else:
                    response = await send_request()
                formatted_response = await self.format_response(response)
                await self.send_to_clients(formatted_response)
                await add_logging()
            else:
                await self.send_to_clients(f"{ws.name}: {message}")

    async def format_response(self, response: dict):
        records = ''

        for k, v in response.items():
            for i, j in v.items():
                records += '|{:^10}|{:^20}|{:^15}|{:^15}|{:^10}|{:^10}|{:^10}|{:^10}|\n'.format('Date', k, 'Currency', i, 'Sale', j[0]['saleRate'], 'Purchase', j[0]['purchaseRate'])

        return records


async def main():
    server = Server()
    async with websockets.serve(server.ws_handler, 'localhost', 8080):
        await asyncio.Future()


if __name__ == '__main__':
    asyncio.run(main())

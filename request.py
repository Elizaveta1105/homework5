import argparse
from datetime import datetime, timedelta

import aiohttp
import asyncio


async def get_request(url: str):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    text = await resp.json()
                    return text
                else:
                    print(f"Error status: {resp.status} for {url}")
        except aiohttp.ClientConnectorError as err:
            print(f'Connection error: {url}', str(err))


async def send_request(diff_days: int = None, curr: str = None):
    shift = 0 if diff_days is None else int(diff_days)
    date_time = datetime.now() - timedelta(days=shift)
    date = datetime.strftime(date_time, '%d.%m.%Y')
    url = f'https://api.privatbank.ua/p24api/exchange_rates?date={date}'
    try:
        response = await get_request(url)
        return await format_data(response, curr)
    except Exception as err:
        print(f'Error: ', str(err))


async def format_data(resp: dict, c: str):
    date = resp['date']
    if c is not None:
        curr_to_display = [x for x in resp['exchangeRate'] if x['currency'] == c]
        return {date: {str(c): curr_to_display}}
    else:
        usd = [x for x in resp['exchangeRate'] if x['currency'] == 'USD']
        eur = [x for x in resp['exchangeRate'] if x['currency'] == 'EUR']
        return {date: {'USD': usd, 'EUR': eur}}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--days', '-d')
    parser.add_argument('--currency', '-c')
    args = vars(parser.parse_args())
    days = args.get('days')
    currency = args.get('currency')

    r = asyncio.run(send_request(days, currency))

    print(r)

import asyncio

# from websockets_proxy import Proxy, proxy_connect
from websockets import connect
from simple_py_config import Config

conf = Config()
conf.from_dot_env_file('./.env')

# this script is written with the above checker server in mind
CHECKER_URL = 'ws://127.0.0.1:8000/ws/connect'


async def main():
    print('in async def main():')
    async with connect(CHECKER_URL) as ws:
        async for msg in ws:
            ip_no_proxy = msg
            print("Your IP:", ip_no_proxy)
    print('.')
    # be sure to create your "Proxy" objects inside an async function
    # proxy = Proxy.from_url(conf.get('VZL_PROXY'))
    # async with proxy_connect(CHECKER_URL, proxy=proxy) as ws:
    #     async for msg in ws:
    #         ip_with_proxy = msg
    #         print("(async with) Proxy IP", ip_with_proxy)
    # print('.')

    # ws = await proxy_connect(CHECKER_URL, proxy=proxy)
    # async for msg in ws:
    #     ip_with_proxy = msg
    #     print("(await) Proxy IP", ip_with_proxy)
    # await ws.close()
    # print('.')


if __name__ == "__main__":
    asyncio.run(main())
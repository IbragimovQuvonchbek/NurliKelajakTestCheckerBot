import aiohttp


async def check_test(name, solution, telegram_id, pk):
    url = f"http://13.60.228.133/api/v1/testchecker/check-test/{pk}/"
    payload = {
        "solution": solution,
        "telegram_id": telegram_id,
        "name": name
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            return await response.json()


async def get_all_tests():
    url = "http://13.60.228.133/api/v1/testchecker/all-tests/"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()


async def get_test_by_id(pk):
    url = f"http://13.60.228.133/api/v1/testchecker/all-tests/{pk}/"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()


async def user_solved(pk, telegram_id):
    url = f"http://13.60.228.133/api/v1/testchecker/user-solved/{pk}/?telegram_id={telegram_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

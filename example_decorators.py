# example_decorators.py
import requests
import asyncio
import aiohttp
from circuit_breaker.decorators import circuit_breaker


# Sync function with circuit breaker
@circuit_breaker(
    name="github_api",
    failure_threshold=3,
    recovery_timeout=20,
    expected_exception=(requests.RequestException,)
)
def get_github_user(username: str):
    """Get GitHub user information"""
    response = requests.get(f"https://api.github.com/users/{username}")
    response.raise_for_status()
    return response.json()


# Async function with circuit breaker
@circuit_breaker(
    name="async_api",
    failure_threshold=2,
    recovery_timeout=15,
    expected_exception=(aiohttp.ClientError,)
)
async def get_user_async(session: aiohttp.ClientSession, username: str):
    """Get user information asynchronously"""
    async with session.get(f"https://api.github.com/users/{username}") as response:
        response.raise_for_status()
        return await response.json()


# Test functions
def test_sync_decorator():
    print("Testing sync decorator:")
    users = ["octocat", "invalid-user-xyz", "torvalds"]

    for user in users * 2:
        try:
            result = get_github_user(user)
            print(f"✅ User {user}: {result['name']}")
        except Exception as e:
            print(f"❌ User {user}: {type(e).__name__}")


async def test_async_decorator():
    print("\nTesting async decorator:")
    users = ["octocat", "invalid-user-xyz", "gvanrossum"]

    async with aiohttp.ClientSession() as session:
        for user in users * 2:
            try:
                result = await get_user_async(session, user)
                print(f"✅ Async user {user}: {result['name']}")
            except Exception as e:
                print(f"❌ Async user {user}: {type(e).__name__}")


if __name__ == "__main__":
    test_sync_decorator()
    asyncio.run(test_async_decorator())
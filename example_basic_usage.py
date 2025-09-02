# example_basic_usage.py
import requests
import time
from circuit_breaker.circuit_breaker_manager import CircuitBreakerManager
from circuit_breaker.custom_circuit_breaker import CircuitBreakerConfig

# Initialize manager
manager = CircuitBreakerManager()

# Register circuit breaker for API service
api_config = CircuitBreakerConfig(
    name="external_api",
    failure_threshold=3,
    recovery_timeout=30,
    expected_exception=(requests.RequestException, ConnectionError)
)
api_cb = manager.register_circuit_breaker(api_config)


def call_external_api(url: str):
    """Function that calls external API"""
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    return response.json()


# Use circuit breaker
def test_api_calls():
    urls = [
        "https://api.github.com/users/octocat",  # Valid URL
        "https://invalid-url-that-will-fail.com",  # Invalid URL
        "https://httpbin.org/status/500",  # Returns 500 error
    ]

    for i, url in enumerate(urls * 3):  # Repeat URLs to trigger circuit breaker
        try:
            result = api_cb.call(call_external_api, url)
            print(f"Call {i + 1}: Success - {result.get('login', 'No login field')}")
        except Exception as e:
            print(f"Call {i + 1}: Failed - {type(e).__name__}: {e}")

        # Print current state
        print(f"Circuit breaker state: {api_cb.current_state}")
        print(f"Failure count: {api_cb.failure_count}")
        print("-" * 50)
        time.sleep(1)


if __name__ == "__main__":
    test_api_calls()
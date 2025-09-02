# example_config_file.py
from circuit_breaker.circuit_breaker_manager import CircuitBreakerManager
from circuit_breaker.decorators import with_circuit_breaker
import requests

# Load circuit breakers from config file
manager = CircuitBreakerManager()
manager.load_from_config_file('circuit_breaker_config.yaml', 'yaml')


@with_circuit_breaker("database_service")
def database_operation():
    """Simulate database operation"""
    import random
    if random.random() < 0.3:  # 30% failure rate
        raise ConnectionError("Database connection failed")
    return "Database operation successful"


@with_circuit_breaker("payment_api")
def process_payment(amount: float):
    """Simulate payment processing"""
    import random
    if random.random() < 0.4:  # 40% failure rate
        raise requests.RequestException("Payment API error")
    return f"Payment of ${amount} processed successfully"


def test_config_based_circuit_breakers():
    print("Testing configuration-based circuit breakers:")

    # Test database operations
    print("\n--- Database Operations ---")
    for i in range(10):
        try:
            result = database_operation()
            print(f"Operation {i + 1}: ✅ {result}")
        except Exception as e:
            print(f"Operation {i + 1}: ❌ {type(e).__name__}: {e}")

    # Test payment operations
    print("\n--- Payment Operations ---")
    for i in range(8):
        try:
            result = process_payment(100.0 + i * 10)
            print(f"Payment {i + 1}: ✅ {result}")
        except Exception as e:
            print(f"Payment {i + 1}: ❌ {type(e).__name__}: {e}")


if __name__ == "__main__":
    test_config_based_circuit_breakers()
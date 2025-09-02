# example_monitoring.py
import json
from .circuit_breaker_manager import CircuitBreakerManager
from .custom_circuit_break_wrapper import CircuitBreakerConfig


def setup_circuit_breakers():
    """Setup multiple circuit breakers"""
    manager = CircuitBreakerManager()

    # Service configurations
    services = [
        {"name": "auth_service", "failure_threshold": 3, "recovery_timeout": 20},
        {"name": "user_service", "failure_threshold": 5, "recovery_timeout": 30},
        {"name": "order_service", "failure_threshold": 2, "recovery_timeout": 45},
    ]

    for service in services:
        config = CircuitBreakerConfig(**service)
        manager.register_circuit_breaker(config)

    return manager


def simulate_service_calls(manager: CircuitBreakerManager):
    """Simulate various service calls"""
    import random
    import time

    def failing_service():
        if random.random() < 0.6:  # 60% failure rate
            raise Exception("Service temporarily unavailable")
        return "Service call successful"

    services = ["auth_service", "user_service", "order_service"]

    for round_num in range(3):
        print(f"\n=== Round {round_num + 1} ===")

        for service_name in services:
            cb = manager.get_circuit_breaker(service_name)
            print(f"\nTesting {service_name}:")

            for i in range(5):
                try:
                    result = cb.call(failing_service)
                    print(f"  Call {i + 1}: ✅ {result}")
                except Exception as e:
                    print(f"  Call {i + 1}: ❌ {type(e).__name__}")

                time.sleep(0.5)

            # Print circuit breaker stats
            stats = cb.get_stats()
            print(f"  State: {stats['current_state']}")
            print(f"  Failures: {stats['failure_count']}")
            print(f"  Total calls: {stats['stats']['total_calls']}")

        time.sleep(2)  # Wait between rounds


def print_comprehensive_stats(manager: CircuitBreakerManager):
    """Print comprehensive statistics"""
    print("\n" + "=" * 60)
    print("COMPREHENSIVE CIRCUIT BREAKER STATISTICS")
    print("=" * 60)

    all_stats = manager.get_all_stats()

    for service_name, stats in all_stats.items():
        print(f"\n📊 {service_name.upper()}")
        print("-" * 40)
        print(f"Current State: {stats['current_state'].upper()}")
        print(f"Failure Threshold: {stats['config']['failure_threshold']}")
        print(f"Recovery Timeout: {stats['config']['recovery_timeout']}s")
        print(f"Current Failure Count: {stats['failure_count']}")

        service_stats = stats['stats']
        print(f"Total Calls: {service_stats['total_calls']}")
        print(f"Successful Calls: {service_stats['successful_calls']}")
        print(f"Failed Calls: {service_stats['failed_calls']}")
        print(f"Blocked Calls: {service_stats['blocked_calls']}")

        if service_stats['last_failure_time']:
            import datetime
            last_failure = datetime.datetime.fromtimestamp(service_stats['last_failure_time'])
            print(f"Last Failure: {last_failure.strftime('%Y-%m-%d %H:%M:%S')}")

        if service_stats['state_changes']:
            print("Recent State Changes:")
            for change in service_stats['state_changes'][-3:]:  # Show last 3 changes
                timestamp = datetime.datetime.fromtimestamp(change['timestamp'])
                print(f"  {change['from']} → {change['to']} at {timestamp.strftime('%H:%M:%S')}")


def main():
    """Main function to demonstrate circuit breaker functionality"""
    manager = setup_circuit_breakers()

    print("🚀 Starting Circuit Breaker Demo")
    simulate_service_calls(manager)
    print_comprehensive_stats(manager)

    # Save stats to file
    with open('circuit_breaker_stats.json', 'w') as f:
        json.dump(manager.get_all_stats(), f, indent=2, default=str)
    print(f"\n💾 Statistics saved to circuit_breaker_stats.json")


if __name__ == "__main__":
    main()
# decorators.py
import asyncio
from functools import wraps
from typing import Optional, Union
from .circuit_breaker_manager import CircuitBreakerManager
from .custom_circuit_break_wrapper import CircuitBreakerConfig


def circuit_breaker(
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 30,
        expected_exception: tuple = (Exception,),
        auto_register: bool = True
):
    """Decorator for applying circuit breaker to functions"""

    def decorator(func):
        # Get or create circuit breaker
        manager = CircuitBreakerManager()
        cb = manager.get_circuit_breaker(name)

        if cb is None and auto_register:
            config = CircuitBreakerConfig(
                name=name,
                failure_threshold=failure_threshold,
                recovery_timeout=recovery_timeout,
                expected_exception=expected_exception
            )
            cb = manager.register_circuit_breaker(config)
        elif cb is None:
            raise ValueError(f"Circuit breaker '{name}' not found. Set auto_register=True or register manually.")

        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await cb.call_async(func, *args, **kwargs)

            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                return cb.call(func, *args, **kwargs)

            return sync_wrapper

    return decorator


def with_circuit_breaker(circuit_breaker_name: str):
    """Decorator to use existing circuit breaker by name"""

    def decorator(func):
        manager = CircuitBreakerManager()
        cb = manager.get_circuit_breaker(circuit_breaker_name)

        if cb is None:
            raise ValueError(f"Circuit breaker '{circuit_breaker_name}' not found")

        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await cb.call_async(func, *args, **kwargs)

            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                return cb.call(func, *args, **kwargs)

            return sync_wrapper

    return decorator
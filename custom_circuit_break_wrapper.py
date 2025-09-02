# custom_circuit_breaker.py
import pybreaker
import logging
import threading
from typing import Dict, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import time
import json


class CircuitBreakerState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half-open"


@dataclass
class CircuitBreakerConfig:
    """Configuration class for circuit breaker settings"""
    name: str
    failure_threshold: int = 5
    recovery_timeout: int = 30
    expected_exception: tuple = (Exception,)
    listeners: list = field(default_factory=list)
    state_storage: Optional[Any] = None
    reset_timeout: int = 60


class CustomCircuitBreakerWrapper:
    """Custom wrapper around pybreaker with additional functionality"""

    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.logger = logging.getLogger(f"CircuitBreaker-{config.name}")

        # Initialize pybreaker circuit breaker
        self._breaker = pybreaker.CircuitBreaker(
            fail_max=config.failure_threshold,
            reset_timeout=config.recovery_timeout,
            exclude=self._get_excluded_exceptions(),
            listeners=self._setup_listeners(),
            state_storage=config.state_storage,
            name=config.name
        )

        # Additional tracking
        self._stats = {
            'total_calls': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'blocked_calls': 0,
            'last_failure_time': None,
            'last_success_time': None,
            'state_changes': []
        }
        self._lock = threading.RLock()

    def _get_excluded_exceptions(self) -> tuple:
        """Get exceptions that should not trigger circuit breaker"""
        all_exceptions = (Exception,)
        return tuple(exc for exc in all_exceptions if exc not in self.config.expected_exception)

    def _setup_listeners(self) -> list:
        """Setup listeners for circuit breaker events"""
        listeners = []

        # Add state change listener
        def state_change_listener(cb, old_state, new_state):
            with self._lock:
                self._stats['state_changes'].append({
                    'from': old_state.name.lower() if hasattr(old_state, 'name') else str(old_state),
                    'to': new_state.name.lower() if hasattr(new_state, 'name') else str(new_state),
                    'timestamp': time.time()
                })
                self.logger.info(f"Circuit breaker {self.config.name} changed from {old_state} to {new_state}")

        listeners.append(state_change_listener)

        # Add custom listeners from config
        listeners.extend(self.config.listeners)

        return listeners

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        with self._lock:
            self._stats['total_calls'] += 1

        try:
            result = self._breaker(func)(*args, **kwargs)

            with self._lock:
                self._stats['successful_calls'] += 1
                self._stats['last_success_time'] = time.time()

            return result

        except pybreaker.CircuitBreakerError as e:
            with self._lock:
                self._stats['blocked_calls'] += 1
            self.logger.warning(f"Circuit breaker {self.config.name} blocked call: {e}")
            raise

        except Exception as e:
            with self._lock:
                self._stats['failed_calls'] += 1
                self._stats['last_failure_time'] = time.time()

            if isinstance(e, self.config.expected_exception):
                self.logger.error(f"Circuit breaker {self.config.name} recorded failure: {e}")
            raise

    async def call_async(self, func: Callable, *args, **kwargs) -> Any:
        """Execute async function with circuit breaker protection"""
        with self._lock:
            self._stats['total_calls'] += 1

        try:
            async_func = self._breaker(func)
            result = await async_func(*args, **kwargs)

            with self._lock:
                self._stats['successful_calls'] += 1
                self._stats['last_success_time'] = time.time()

            return result

        except pybreaker.CircuitBreakerError as e:
            with self._lock:
                self._stats['blocked_calls'] += 1
            self.logger.warning(f"Circuit breaker {self.config.name} blocked async call: {e}")
            raise

        except Exception as e:
            with self._lock:
                self._stats['failed_calls'] += 1
                self._stats['last_failure_time'] = time.time()

            if isinstance(e, self.config.expected_exception):
                self.logger.error(f"Circuit breaker {self.config.name} recorded async failure: {e}")
            raise

    @property
    def current_state(self) -> str:
        """Get current state of circuit breaker"""
        state = self._breaker.current_state
        if hasattr(state, 'name'):
            return state.name.lower()
        return str(state).lower()

    @property
    def failure_count(self) -> int:
        """Get current failure count"""
        return self._breaker._failure_count

    @property
    def last_failure_time(self) -> Optional[float]:
        """Get last failure time"""
        return self._breaker._last_failure

    def get_stats(self) -> Dict[str, Any]:
        """Get detailed statistics"""
        with self._lock:
            return {
                'name': self.config.name,
                'current_state': self.current_state,
                'failure_count': self.failure_count,
                'last_failure_time': self.last_failure_time,
                'config': {
                    'failure_threshold': self.config.failure_threshold,
                    'recovery_timeout': self.config.recovery_timeout,
                    'expected_exceptions': [exc.__name__ for exc in self.config.expected_exception]
                },
                'stats': self._stats.copy()
            }

    def reset(self):
        """Manually reset the circuit breaker"""
        self._breaker._reset()
        self.logger.info(f"Circuit breaker {self.config.name} manually reset")

    def force_open(self):
        """Manually force circuit breaker to open state"""
        self._breaker._state = pybreaker.STATE_OPEN
        self._breaker._last_failure = time.time()
        self.logger.warning(f"Circuit breaker {self.config.name} manually forced to OPEN state")
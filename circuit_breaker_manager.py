# circuit_breaker_manager.py
import threading
from typing import Dict, Optional, Any
from .custom_circuit_break_wrapper import CustomCircuitBreakerWrapper, CircuitBreakerConfig
import json
import yaml


class CircuitBreakerManager:
    """Singleton manager for multiple circuit breakers"""

    _instance = None
    _lock = threading.RLock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'circuit_breakers'):
            self.circuit_breakers: Dict[str, CustomCircuitBreakerWrapper] = {}
            self._initialized = True

    def register_circuit_breaker(self, config: CircuitBreakerConfig) -> CustomCircuitBreakerWrapper:
        """Register a new circuit breaker"""
        with self._lock:
            if config.name in self.circuit_breakers:
                raise ValueError(f"Circuit breaker '{config.name}' already exists")

            circuit_breaker = CustomCircuitBreakerWrapper(config)
            self.circuit_breakers[config.name] = circuit_breaker
            return circuit_breaker

    def get_circuit_breaker(self, name: str) -> Optional[CustomCircuitBreakerWrapper]:
        """Get circuit breaker by name"""
        return self.circuit_breakers.get(name)

    def remove_circuit_breaker(self, name: str) -> bool:
        """Remove circuit breaker by name"""
        with self._lock:
            if name in self.circuit_breakers:
                del self.circuit_breakers[name]
                return True
            return False

    def get_all_circuit_breakers(self) -> Dict[str, CustomCircuitBreakerWrapper]:
        """Get all registered circuit breakers"""
        return self.circuit_breakers.copy()

    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all circuit breakers"""
        return {name: cb.get_stats() for name, cb in self.circuit_breakers.items()}

    def reset_all(self):
        """Reset all circuit breakers"""
        with self._lock:
            for cb in self.circuit_breakers.values():
                cb.reset()

    def load_from_config_file(self, file_path: str, file_type: str = 'yaml'):
        """Load circuit breakers from configuration file"""
        if file_type.lower() == 'yaml':
            with open(file_path, 'r') as f:
                config_data = yaml.safe_load(f)
        elif file_type.lower() == 'json':
            with open(file_path, 'r') as f:
                config_data = json.load(f)
        else:
            raise ValueError("Unsupported file type. Use 'yaml' or 'json'")

        for name, config in config_data.items():
            # Convert exception names to actual exception classes
            if 'expected_exception' in config:
                exceptions = []
                for exc_name in config['expected_exception']:
                    try:
                        exceptions.append(eval(exc_name))
                    except:
                        exceptions.append(Exception)
                config['expected_exception'] = tuple(exceptions)

            cb_config = CircuitBreakerConfig(name=name, **config)
            self.register_circuit_breaker(cb_config)
from typing import Callable, Dict, Type, TypeVar

from fcg.config.settings import Settings

T = TypeVar("T")


class ServiceContainer:
    """Simple dependency injection container"""

    def __init__(self, settings: Settings):
        self.settings = settings
        self._services: Dict[Type, object] = {}
        self._factories: Dict[Type, Callable[[Settings], object]] = {}

    def register_factory(self, interface: Type, factory: Callable[[Settings], object]):
        """Register a factory function for an interface"""
        self._factories[interface] = factory

    def register_instance(self, interface: Type, instance: object):
        """Register a singleton instance for an interface"""
        self._services[interface] = instance

    def get(self, interface: Type[T]) -> T:
        """Get an instance of the requested interface"""
        if interface in self._services:
            return self._services[interface]  # type: ignore

        if interface in self._factories:
            instance = self._factories[interface](self.settings)
            self._services[interface] = instance
            return instance  # type: ignore

        raise ValueError(f"No registration found for {interface}")

    def get_settings(self) -> Settings:
        """Get application settings"""
        return self.settings

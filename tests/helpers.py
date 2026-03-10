import importlib
from types import ModuleType


def reload_module(module: ModuleType) -> None:
    """
    Reload a module to ensure that environment changes are reflected.

    :param module: The module to reload
    :type module: ModuleType
    """
    importlib.reload(module)


def fake_method_call(method: str, return_value):
    def method_call(*args, **kwargs):
        return type("Dummy", (), {method: lambda self: return_value})()

    return method_call

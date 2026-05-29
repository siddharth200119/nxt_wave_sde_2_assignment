import importlib
import inspect
from pathlib import Path
from starlette.middleware.base import BaseHTTPMiddleware
from src.utils import logger as sys_logger

current_dir = Path(__file__).parent

middlewares_to_apply = []

for item in current_dir.iterdir():
    module_name = None
    module_path = None

    if item.is_file() and item.suffix == ".py" and not item.name.startswith("_"):
        module_name = item.stem
        module_path = f"{__package__}.{module_name}"

    if module_path:
        try:
            module = importlib.import_module(module_path)
            
            # Find all classes in the module that inherit from BaseHTTPMiddleware
            for name, obj in inspect.getmembers(module, inspect.isclass):
                # Don't grab BaseHTTPMiddleware itself, only its subclasses defined in the module
                if issubclass(obj, BaseHTTPMiddleware) and obj is not BaseHTTPMiddleware and getattr(obj, "__module__", "") == module_path:
                    middlewares_to_apply.append(obj)
                    sys_logger.info(f"Discovered middleware: {name}")

        except Exception as e:
            sys_logger.error(f"Could not import middleware from {module_path}: {e}")

# Note: In FastAPI, the LAST middleware added runs FIRST for incoming requests.
# If order matters, we'd need a priority system. For now, they are applied in discovery order.


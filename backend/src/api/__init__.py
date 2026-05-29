import importlib
import os
from pathlib import Path
from typing import Set, Tuple
from fastapi import APIRouter, Depends
from src.utils import logger
from src.models import Route
from src.middlewares.rbac import RoleChecker

main_router = APIRouter(prefix="/api")
REGISTERED_ROUTES: Set[Tuple[str, str]] = set()


def discover_routes(directory: Path, module_prefix: str, url_prefix: str):
    """
    Recursively discover Route objects in the given directory.
    """
    for item in directory.iterdir():
        if item.name.startswith("_"):
            continue

        if item.is_file() and item.suffix == ".py":
            module_name = item.stem
            module_path = f"{module_prefix}.{module_name}"

            # Convert file name to path segment (e.g., create_user -> create-user)
            # But skip if it's __init__.py (already handled by folder logic)
            if module_name == "__init__":
                continue

            path_segment = module_name.replace("_", "-")
            full_url_path = f"{url_prefix}/{path_segment}"

            register_module_routes(module_path, full_url_path, url_prefix)

        elif item.is_dir():
            module_name = item.name
            module_path = f"{module_prefix}.{module_name}"
            path_segment = module_name.replace("_", "-")

            # Check for __init__.py in the directory
            init_file = item / "__init__.py"
            if init_file.exists():
                # Discover routes in the directory first (init file maps to the folder path itself)
                register_module_routes(module_path, url_prefix if url_prefix else "/", url_prefix)

            # Recursively discover in subdirectories
            discover_routes(item, module_path, f"{url_prefix}/{path_segment}")


def register_module_routes(module_path: str, default_path: str, url_prefix: str):
    """
    Import a module and register any Route or list[Route] objects found.
    """
    try:
        module = importlib.import_module(module_path)

        # Look for 'route' (single) or 'routes' (list)
        found_routes = []
        route_obj = getattr(module, "route", None)
        if isinstance(route_obj, Route):
            found_routes.append(route_obj)

        routes_obj = getattr(module, "routes", None)
        if isinstance(routes_obj, list):
            for r in routes_obj:
                if isinstance(r, Route):
                    found_routes.append(r)

        for r in found_routes:
            # Use path from Route object (prefixed with folder url_prefix) if provided,
            # otherwise use default_path (which includes the filename segment)
            if r.path:
                path = f"{url_prefix}{r.path}" if r.path.startswith("/") else f"{url_prefix}/{r.path}"
            else:
                path = default_path

            method = r.method.upper()

            
            # Ensure path starts with / and doesn't end with / unless it's just /
            if not path.startswith("/"):
                path = f"/{path}"
            if len(path) > 1 and path.endswith("/"):
                path = path[:-1]

            # Check for collisions
            route_key = (method, path)
            if route_key in REGISTERED_ROUTES:
                logger.warning(f"⚠️ Route collision detected: {method} {path} (defined in {module_path})")
            else:
                REGISTERED_ROUTES.add(route_key)
                
                # Build route-level dependencies for RBAC
                dependencies = []
                if r.required_roles:
                    dependencies.append(Depends(RoleChecker(r.required_roles)))
                
                # Add to FastAPI router
                main_router.add_api_route(
                    path=path,
                    endpoint=r.function,
                    methods=[method],
                    summary=r.summary,
                    description=r.description,
                    tags=r.tags,
                    dependencies=dependencies
                )
                logger.debug(f"✅ Registered route: {method} {path} -> {module_path}.{r.function.__name__}")

    except Exception as e:
        logger.error(f"❌ Could not import or register routes from {module_path}: {e}")


# Start discovery from the current directory
discover_routes(Path(__file__).parent, __package__, "")

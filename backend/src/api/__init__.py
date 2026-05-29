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


def discover_routes(directory: Path, module_prefix: str, url_prefix: str) -> list[dict]:
    """
    Recursively discover Route objects in the given directory.
    Returns a list of dictionaries with route configurations.
    """
    routes = []
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

            routes.extend(collect_module_routes(module_path, full_url_path, url_prefix))

        elif item.is_dir():
            module_name = item.name
            module_path = f"{module_prefix}.{module_name}"
            path_segment = module_name.replace("_", "-")

            # Check for __init__.py in the directory
            init_file = item / "__init__.py"
            if init_file.exists():
                # Discover routes in the directory first (init file maps to the folder path itself)
                routes.extend(collect_module_routes(module_path, url_prefix if url_prefix else "/", url_prefix))

            # Recursively discover in subdirectories
            routes.extend(discover_routes(item, module_path, f"{url_prefix}/{path_segment}"))
            
    return routes


def collect_module_routes(module_path: str, default_path: str, url_prefix: str) -> list[dict]:
    """
    Import a module and return any Route or list[Route] objects found.
    """
    collected = []
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

            collected.append({
                "module_path": module_path,
                "route_obj": r,
                "path": path,
                "method": method
            })

    except Exception as e:
        logger.error(f"❌ Could not import or register routes from {module_path}: {e}")

    return collected


# 1. Discover and collect all routes recursively
all_routes = discover_routes(Path(__file__).parent, __package__, "")

# 2. Sort routes so that static routes (e.g., without "{") are registered BEFORE dynamic routes (e.g., with "{")
# This prevents Starlette routing wildcard matching conflicts (e.g. /api/user/list matching /api/user/{id})
all_routes.sort(key=lambda r: 1 if "{" in r["path"] else 0)

# 3. Register routes to the main FastAPI router in the sorted order
for r in all_routes:
    module_path = r["module_path"]
    route_obj = r["route_obj"]
    path = r["path"]
    method = r["method"]

    route_key = (method, path)
    if route_key in REGISTERED_ROUTES:
        logger.warning(f"⚠️ Route collision detected: {method} {path} (defined in {module_path})")
    else:
        REGISTERED_ROUTES.add(route_key)
        
        # Build route-level dependencies for RBAC
        dependencies = []
        if route_obj.required_roles:
            dependencies.append(Depends(RoleChecker(route_obj.required_roles)))
        
        # Add to FastAPI router
        main_router.add_api_route(
            path=path,
            endpoint=route_obj.function,
            methods=[method],
            summary=route_obj.summary,
            description=route_obj.description,
            tags=route_obj.tags,
            dependencies=dependencies
        )
        logger.debug(f"✅ Registered route: {method} {path} -> {module_path}.{route_obj.function.__name__}")

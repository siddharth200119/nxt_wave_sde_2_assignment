import importlib
import os
from pathlib import Path
from typing import Set, Tuple
from fastapi import APIRouter
from src.utils import logger
from src.models import Route

main_router = APIRouter(prefix="/sse")
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
            
            if module_name == "__init__":
                continue
                
            path_segment = module_name.replace("_", "-")
            full_url_path = f"{url_prefix}/{path_segment}"
            
            register_module_routes(module_path, full_url_path)

        elif item.is_dir():
            module_name = item.name
            module_path = f"{module_prefix}.{module_name}"
            path_segment = module_name.replace("_", "-")
            
            init_file = item / "__init__.py"
            if init_file.exists():
                register_module_routes(module_path, url_prefix if url_prefix else "/")
            
            discover_routes(item, module_path, f"{url_prefix}/{path_segment}")


def register_module_routes(module_path: str, default_path: str):
    """
    Import a module and register any Route or list[Route] objects found.
    """
    try:
        module = importlib.import_module(module_path)
        
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
            path = r.path if r.path else default_path
            method = r.method.upper()
            
            if not path.startswith("/"):
                path = f"/{path}"
            if len(path) > 1 and path.endswith("/"):
                path = path[:-1]

            route_key = (method, path)
            if route_key in REGISTERED_ROUTES:
                logger.warning(f"⚠️ SSE Route collision detected: {method} {path} (defined in {module_path})")
            else:
                REGISTERED_ROUTES.add(route_key)
                
                main_router.add_api_route(
                    path=path,
                    endpoint=r.function,
                    methods=[method],
                    summary=r.summary,
                    description=r.description,
                    tags=r.tags
                )
                logger.debug(f"✅ Registered SSE route: {method} {path} -> {module_path}.{r.function.__name__}")

    except Exception as e:
        logger.error(f"❌ Could not import or register SSE routes from {module_path}: {e}")


discover_routes(Path(__file__).parent, __package__, "")

from .logger import Logger
from .hasher import hash_string
import os

logger = Logger(service_name=os.environ.get("SERVICE_NAME", "NAMELESS_SERVICE"))

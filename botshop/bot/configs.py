TOKEN = ""
DEBUG = False

try:
    from .local_config import *
except ImportError:
    print("Running in prodaction mode")
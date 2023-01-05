"""
    This file contains all the configuration parameters for the project.
"""
# Camera configuration
WINDOW_TITLE = "CSI Camera"
WIDTH = 640
HEIGHT = 480
# Model configuration
PLUGIN_LIBRARY = "libmyplugins.so"
ENGINE_FILE_PATH = "aceluya_n.engine"

CONF_THRESH = 0.5
IOU_THRESHOLD = 0.4
CATEGORIES = ["trash"]

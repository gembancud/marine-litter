"""
    This file contains all the configuration parameters for the project.
"""
# Camera configuration
WINDOW_TITLE = "CSI Camera"
WIDTH = 640
HEIGHT = 480
# Model configuration
YOLOV5_PLUGIN_LIBRARY = "models/yolov5/libmyplugins.so"
YOLOV5_ENGINE_FILE_PATH = "models/yolov5/aceluya_n.engine"

CONF_THRESH = 0.5
IOU_THRESHOLD = 0.4
CATEGORIES = ["trash"]

# Tracking configuration
TRACK_POINTS = "iou"  # "iou" or "bbox"

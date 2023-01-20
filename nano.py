"""
An example that uses TensorRT's Python api to make inferences.
"""
import ctypes
import os
import shutil
import sys
import argparse
import cv2
import pycuda.autoinit
import pycuda.driver as cuda

from camera.camera import gstreamer_pipeline
from models.yolov5.yolov5_trt import YoLov5TRT, warmUpThread
import config


if __name__ == "__main__":
    # Add argparser
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model",
        type=str,
        choices=["yolov5", "yolov7"],
        default="yolov5",
        help="model architecture",
    )
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")

    parser.add_argument(
        "--camera",
        type=str,
        choices=["module", "depth"],
        default="module",
        help="Choose camera to use",
    )
    parser.add_argument("--gps", action="store_true", help="Use GPS")
    parser.add_argument("--save-video", action="store_true", help="Save video")
    parser.add_argument("--track", action="store_true", help="Track objects")
    parser.add_argument("--save-frames", action="store_true", help="Save frames")
    parser.add_argument("--save-csv", action="store_true", help="Save csv")
    args = parser.parse_args()
    if args.headless:
        print("Headless mode")

    if args.model == "yolov7":
        PLUGIN_LIBRARY = config.YOLOV5_PLUGIN_LIBRARY
        ENGINE_FILE_PATH = config.YOLOV5_ENGINE_FILE_PATH
    elif args.model == "yolov5":
        # load custom plugin and engine
        PLUGIN_LIBRARY = config.YOLOV5_PLUGIN_LIBRARY
        ENGINE_FILE_PATH = config.YOLOV5_ENGINE_FILE_PATH

    ctypes.CDLL(PLUGIN_LIBRARY)

    video_capture = cv2.VideoCapture(
        gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER
    )
    # load coco labels

    categories = config.CATEGORIES

    if os.path.exists("output/"):
        shutil.rmtree("output/")
    os.makedirs("output/")
    # a YoLov5TRT instance
    yolov5_wrapper = YoLov5TRT(ENGINE_FILE_PATH)
    try:
        print("batch size is", yolov5_wrapper.batch_size)

        for i in range(10):
            # create a new thread to do warm_up
            thread1 = warmUpThread(yolov5_wrapper)
            thread1.start()
            thread1.join()

            WINDOW_TITLE = config.WINDOW_TITLE

            if video_capture.isOpened():
                try:
                    window_handle = cv2.namedWindow(WINDOW_TITLE, cv2.WINDOW_AUTOSIZE)
                    while True:
                        ret_val, frame = video_capture.read()
                        if (
                            cv2.getWindowProperty(WINDOW_TITLE, cv2.WND_PROP_AUTOSIZE)
                            >= 0
                        ):
                            frame, t, label = yolov5_wrapper.infer([frame])
                            print(label)
                            cv2.imshow(WINDOW_TITLE, frame[0])
                        # out.write(frame)

                        else:
                            break
                        keyCode = cv2.waitKey(10) & 0xFF
                        # Stop the program on the ESC key or 'q'
                        if keyCode == 27 or keyCode == ord("q"):
                            break
                finally:
                    video_capture.release()
                    # 		        out.release()
                    cv2.destroyAllWindows()
            else:
                print("Error: Unable to open camera")

    finally:
        # destroy the instance
        yolov5_wrapper.destroy()

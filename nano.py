"""
An example that uses TensorRT's Python api to make inferences.
"""
import ctypes
import os
import shutil
import sys
import cv2
import pycuda.autoinit
import pycuda.driver as cuda

from camera.camera import gstreamer_pipeline
from models.yolov5_trt import YoLov5TRT, warmUpThread
import config


if __name__ == "__main__":
    # load custom plugin and engine
    PLUGIN_LIBRARY = config.PLUGIN_LIBRARY
    ENGINE_FILE_PATH = config.ENGINE_FILE_PATH

    if len(sys.argv) > 1:
        ENGINE_FILE_PATH = sys.argv[1]
    if len(sys.argv) > 2:
        PLUGIN_LIBRARY = sys.argv[2]

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

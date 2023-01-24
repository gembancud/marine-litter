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
        yolov5_wrapper = YoLov5TRT(ENGINE_FILE_PATH)

    ctypes.CDLL(PLUGIN_LIBRARY)

    if args.camera == "module":
        from camera.camera import gstreamer_pipeline

        VIDEO_CAPTURE = cv2.VideoCapture(
            gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER
        )
    else:
        from camera.depth import pipeline
        import numpy as np

    # load coco labels

    categories = config.CATEGORIES

    if os.path.exists("output/"):
        shutil.rmtree("output/")
    os.makedirs("output/")
    # a YoLov5TRT instance
    try:
        print("batch size is", yolov5_wrapper.batch_size)

        for i in range(10):
            # create a new thread to do warm_up
            thread1 = warmUpThread(yolov5_wrapper)
            thread1.start()
            thread1.join()

        WINDOW_TITLE = config.WINDOW_TITLE
        if args.camera == "module":
            if VIDEO_CAPTURE.isOpened():
                try:
                    window_handle = cv2.namedWindow(WINDOW_TITLE, cv2.WINDOW_AUTOSIZE)
                    while True:
                        ret_val, frame = VIDEO_CAPTURE.read()
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
                    VIDEO_CAPTURE.release()
                    # 		        out.release()
                    cv2.destroyAllWindows()
            else:
                print("Error: Unable to open camera")
        else:
            try:
                while True:

                    # Wait for a coherent pair of frames: depth and color
                    frames = pipeline.wait_for_frames()
                    depth_frame = frames.get_depth_frame()
                    color_frame = frames.get_color_frame()
                    if not depth_frame or not color_frame:
                        continue

                    # Convert images to numpy arrays
                    depth_image = np.asanyarray(depth_frame.get_data())
                    color_image = np.asanyarray(color_frame.get_data())

                    # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
                    depth_colormap = cv2.applyColorMap(
                        cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET
                    )

                    depth_colormap_dim = depth_colormap.shape
                    color_colormap_dim = color_image.shape

                    # If depth and color resolutions are different, resize color image to match depth image for display
                    if depth_colormap_dim != color_colormap_dim:
                        resized_color_image = cv2.resize(
                            color_image,
                            dsize=(depth_colormap_dim[1], depth_colormap_dim[0]),
                            interpolation=cv2.INTER_AREA,
                        )
                        images = np.hstack((resized_color_image, depth_colormap))
                    else:
                        images = np.hstack((color_image, depth_colormap))

                    # Show images
                    cv2.namedWindow("RealSense", cv2.WINDOW_AUTOSIZE)
                    cv2.imshow("RealSense", images)
                    cv2.waitKey(1)

            finally:

                # Stop streaming
                pipeline.stop()

    finally:
        # destroy the instance
        yolov5_wrapper.destroy()

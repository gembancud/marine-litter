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
    parser.add_argument("--no-detect", action="store_true", help="Do not use detection")
    parser.add_argument("--gps", action="store_true", help="Use GPS")
    parser.add_argument("--track", action="store_true", help="Track objects")
    parser.add_argument("--save-video", action="store_true", help="Save video")
    parser.add_argument("--save-frames", action="store_true", help="Save frames")
    parser.add_argument("--save-csv", action="store_true", help="Save csv")
    args = parser.parse_args()
    if args.headless:
        print("Headless mode")

    if args.model == "yolov7":
        pass
    elif args.model == "yolov5":
        # load custom plugin and engine
        PLUGIN_LIBRARY = config.YOLOV5_PLUGIN_LIBRARY
        ENGINE_FILE_PATH = config.YOLOV5_ENGINE_FILE_PATH
        ctypes.CDLL(PLUGIN_LIBRARY)
        model_wrapper = YoLov5TRT(ENGINE_FILE_PATH)

    if args.camera == "module":
        from camera.camera import gstreamer_pipeline

        VIDEO_CAPTURE = cv2.VideoCapture(
            gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER
        )
        # a lambda function calling video_capture.read()
        read = lambda: VIDEO_CAPTURE.read()[1]
    else:
        from camera.depth import pipeline
        import numpy as np

        read = lambda: np.asanyarray(
            pipeline.wait_for_frames().get_color_frame().get_data()
        )
    # load coco labels

    if args.gps:
        from gps.main import GPS
        import multiprocessing

        gps = GPS()
        gps.start()

    if args.track:
        from misc.tracker import MyTracker

        tracker = MyTracker()

    categories = config.CATEGORIES

    # if os.path.exists("output/"):
    #     shutil.rmtree("output/")
    # os.makedirs("output/")
    # a YoLov5TRT instance
    try:
        print("batch size is", model_wrapper.batch_size)

        if not args.no_detect:
            for i in range(10):
                # create a new thread to do warm_up
                thread1 = warmUpThread(model_wrapper)
                thread1.start()
                thread1.join()

        WINDOW_TITLE = config.WINDOW_TITLE
        window_handle = cv2.namedWindow(WINDOW_TITLE, cv2.WINDOW_AUTOSIZE)
        try:
            while True:
                frame = read()
                # frame, t, label = yolov5_wrapper.infer([frame])
                # print(label)
                # cv2.imshow(WINDOW_TITLE, frame[0])

                if args.gps:
                    # lon, lat = gps.lon.value, gps.lat.value
                    cv2.putText(
                        frame,
                        f"GPS: {gps.lon.value}, {gps.lat.value}",
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 0, 255),
                        1,
                        2,
                    )
                if (
                    cv2.getWindowProperty(config.WINDOW_TITLE, cv2.WND_PROP_AUTOSIZE)
                    >= 0
                ):
                    if not args.no_detect:
                        (
                            frame,
                            t,
                            result_boxes,
                            result_scores,
                            result_ids,
                        ) = model_wrapper.infer([frame])

                        if args.track:
                            frame = tracker.update(
                                frame, result_boxes, result_scores, result_ids
                            )

                    cv2.imshow(WINDOW_TITLE, frame)
                # write text at the top left of the frame
                # out.write(frame)

                keyCode = cv2.waitKey(10) & 0xFF
                # Stop the program on the ESC key or 'q'
                if keyCode == 27 or keyCode == ord("q"):
                    break
        finally:
            if args.camera == "module":
                VIDEO_CAPTURE.release()
            elif args.camera == "depth":
                pipeline.stop()
            # out.release()
            cv2.destroyAllWindows()

    finally:
        # destroy the instance
        if args.model == "yolov7":
            pass
        elif args.model == "yolov5":
            model_wrapper.destroy()

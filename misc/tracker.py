import sys

sys.path.append("..")

from typing import List, Optional, Union

import norfair
import numpy as np
import torch
from norfair import Detection, Tracker

import config

DISTANCE_THRESHOLD_BBOX: float = 0.7
DISTANCE_THRESHOLD_CENTROID: int = 30
MAX_DISTANCE: int = 10000
# max_distance_between_points: int = 30
max_distance_between_points: int = 60


# def yolo_detections_to_norfair_detections(
#     yolo_detections: torch.tensor, track_points: str = "centroid"  # bbox or centroid
# ) -> List[Detection]:
#     """convert detections_as_xywh to norfair detections"""
#     norfair_detections: List[Detection] = []

#     if track_points == "centroid":
#         detections_as_xywh = yolo_detections.xywh[0]
#         for detection_as_xywh in detections_as_xywh:
#             centroid = np.array(
#                 [detection_as_xywh[0].item(), detection_as_xywh[1].item()]
#             )
#             scores = np.array([detection_as_xywh[4].item()])
#             norfair_detections.append(Detection(points=centroid, scores=scores))
#     elif track_points == "bbox":
#         detections_as_xyxy = yolo_detections.xyxy[0]
#         for detection_as_xyxy in detections_as_xyxy:
#             bbox = np.array(
#                 [
#                     [detection_as_xyxy[0].item(), detection_as_xyxy[1].item()],
#                     [detection_as_xyxy[2].item(), detection_as_xyxy[3].item()],
#                 ]
#             )
#             scores = np.array(
#                 [detection_as_xyxy[4].item(), detection_as_xyxy[4].item()]
#             )
#             norfair_detections.append(Detection(points=bbox, scores=scores))

#     return norfair_detections


class MyTracker:
    tracker = None

    def __init__(self):
        distance_function = "iou" if config.TRACK_POINTS == "bbox" else "euclidean"
        distance_threshold = (
            DISTANCE_THRESHOLD_BBOX
            if config.TRACK_POINTS == "bbox"
            else DISTANCE_THRESHOLD_CENTROID
        )

        self.tracker = Tracker(
            distance_function=distance_function,
            distance_threshold=distance_threshold,
        )

    def update(self, frame, yolo_detections, scores, ids):
        detections = self.yolo_detections_to_norfair_detections(
            yolo_detections, scores, ids
        )
        tracked_objects = self.tracker.update(detections=detections)

        norfair.draw_points(frame, detections)
        norfair.draw_tracked_objects(frame, tracked_objects)

        return frame

    @staticmethod
    def yolo_detections_to_norfair_detections(
        yolo_detections, scores, ids
    ) -> List[Detection]:
        """convert detections_as_xyxy to norfair detections"""
        norfair_detections: List[Detection] = []
        for yolo_detection, score, class_id in zip(yolo_detections, scores, ids):
            bbox = np.array(
                [
                    [yolo_detection[0], yolo_detection[1]],
                    [yolo_detection[2], yolo_detection[3]],
                ]
            )
            scores = np.array([score[0], score[1]])
            norfair_detections.append(
                Detection(points=bbox, scores=scores, label=int(class_id))
            )

        return norfair_detections


# Sample
# for input_path in args.files:
#     video = Video(input_path=input_path)
#     tracker = Tracker(
#         distance_function=euclidean_distance,
#         distance_threshold=max_distance_between_points,
#     )

#     for frame in video:
#         yolo_detections = model(
#             frame,
#             conf_threshold=args.conf_thres,
#             iou_threshold=args.iou_thresh,
#             image_size=args.img_size,
#             classes=args.classes,
#         )
#         detections = yolo_detections_to_norfair_detections(
#             yolo_detections, track_points=args.track_points
#         )
#         tracked_objects = tracker.update(detections=detections)
#         if args.track_points == "centroid":
#             norfair.draw_points(frame, detections)
#         elif args.track_points == "bbox":
#             norfair.draw_boxes(frame, detections)
#         norfair.draw_tracked_objects(frame, tracked_objects)
#         norfair.draw_debug_metrics(frame, tracked_objects)
#         video.write(frame)

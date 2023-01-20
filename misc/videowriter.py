import cv2
import config

fourcc = cv2.VideoWriter_fourcc(*"XVID")
videowriter = cv2.VideoWriter("output.avi", fourcc, 20.0, (config.WIDTH, config.HEIGHT))

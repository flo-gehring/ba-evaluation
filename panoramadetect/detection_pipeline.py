"""
Disclaimer: Code Taken from this Tutorial: https://www.pyimagesearch.com/2018/11/19/mask-r-cnn-with-opencv/
"""

# USAGE
# python mask_rcnn_video.py --input videos/cats_and_dogs.mp4 --output output/cats_and_dogs_output.avi --mask-rcnn mask-rcnn-coco

# import the necessary packages
import numpy as np
import argparse
import imutils
import time
import cv2
import os
import json
from setup_tracker_directories import get_filename

# construct the argument parse and parse the arguments

mask_rcnn_base_path = "\\".join([ "mask-rcnn", "mask-rcnn-coco"])


print(cv2.getBuildInformation())
labelsPath = os.path.sep.join([mask_rcnn_base_path, "object_detection_classes_coco.txt"])


LABELS = open(labelsPath).read().strip().split("\n")

VIDEO_PATH = "/home/flo/Videos/TS_10_5.mp4"
WIN_VID_PATH = "C:\\Users\\Florian Gehring\\Workspace\\Uni\\Videos\\TS_10_5.mp4"
VIDEO_PATH = WIN_VID_PATH

MASK_RCNN_CONF_THRESHOLD = 0.6
DETECTION_RCNN_CONF_THRESHOLD = 0.6

# initialize a list of colors to represent each possible class label
np.random.seed(42)
COLORS = np.random.randint(0, 255, size=(len(LABELS), 3),
	dtype="uint8")

# derive the paths to the Mask R-CNN weights and model configuration
# load the COCO class labels our Mask R-CNN was trained on
weightsPath = os.path.sep.join([mask_rcnn_base_path, "frozen_inference_graph.pb"])
configPath = os.path.sep.join([mask_rcnn_base_path, "mask_rcnn_inception_v2_coco_2018_01_28.pbtxt"])

# load our Mask R-CNN trained on the COCO dataset (90 classes)
# from disk
print("[INFO] loading Mask R-CNN from disk...")
net = cv2.dnn.readNetFromTensorflow(weightsPath, configPath)

# initialize the video stream and pointer to output video file
vs = cv2.VideoCapture(VIDEO_PATH)
writer = None

detection_file = open("detections.json", "w")
detection_file.write("[")
# try to determine the total number of frames in the video file
try:
	prop = cv2.cv.CV_CAP_PROP_FRAME_COUNT if imutils.is_cv2() \
		else cv2.CAP_PROP_FRAME_COUNT
	total = int(vs.get(prop))
	print("[INFO] {} total frames in video".format(total))

# an error occurred while trying to determine the total
# number of frames in the video file
except:
	print("[INFO] could not determine # of frames in video")
	total = -1

WINDOW_NAME = "MaskRCNN"
# cv2.namedWindow(WINDOW_NAME)

# loop over frames from the video file stream
frame_counter = -1
while True:
	frame_counter += 1
	# read the next frame from the file
	(grabbed, frame) = vs.read()

	# if the frame was not grabbed, then we have reached the end
	# of the stream
	if not grabbed:
		break

	# construct a blob from the input frame and then perform a
	# forward pass of the Mask R-CNN, giving us (1) the bounding box
	# coordinates of the objects in the image along with (2) the
	# pixel-wise segmentation for each specific object
	blob = cv2.dnn.blobFromImage(frame, swapRB=True, crop=False)
	net.setInput(blob)
	start = time.time()
	(boxes, masks) = net.forward(["detection_out_final",
		"detection_masks"])
	end = time.time()

	# loop over the number of detected objects
	frame_obj_list = list()
	for i in range(0, boxes.shape[2]):
		# extract the class ID of the detection along with the
		# confidence (i.e., probability) associated with the
		# prediction
		classID = int(boxes[0, 0, i, 1])
		confidence = boxes[0, 0, i, 2]

		# filter out weak predictions by ensuring the detected
		# probability is greater than the minimum probability
		if confidence > DETECTION_RCNN_CONF_THRESHOLD:
			# scale the bounding box coordinates back relative to the
			# size of the frame and then compute the width and the
			# height of the bounding box
			(H, W) = frame.shape[:2]
			box = boxes[0, 0, i, 3:7] * np.array([W, H, W, H])
			(startX, startY, endX, endY) = box.astype("int")
			boxW = endX - startX
			boxH = endY - startY

			# extract the pixel-wise segmentation for the object,
			# resize the mask such that it's the same dimensions of
			# the bounding box, and then finally threshold to create
			# a *binary* mask
			mask = masks[i, classID]
			mask = cv2.resize(mask, (boxW, boxH),
				interpolation=cv2.INTER_NEAREST)
			mask = (mask > MASK_RCNN_CONF_THRESHOLD)

			# extract the ROI of the image but *only* extracted the
			# masked region of the ROI
			roi = frame[startY:endY, startX:endX][mask]

			# grab the color used to visualize this particular class,
			# then create a transparent overlay by blending the color
			# with the ROI
			color = COLORS[classID]
			blended = ((0.4 * color) + (0.6 * roi)).astype("uint8")

			frame_obj_list.append({
				"classID": int(classID),
				"confidence": float(confidence),
				"x": float(startX),
				"y": float(startY),
				"width": float(boxW),
				"height": float(boxH)
			})

			# store the blended ROI in the original frame
			frame[startY:endY, startX:endX][mask] = blended

			# draw the bounding box of the instance on the frame
			color = [int(c) for c in color]
			cv2.rectangle(frame, (startX, startY), (endX, endY),
				color, 2)

			# draw the predicted label and associated probability of
			# the instance segmentation on the frame
			text = "{}: {:.4f}".format(LABELS[classID], confidence)
			cv2.putText(frame, text, (startX, startY - 5),
				cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

	# check if the video writer is None
	frame_detections = {"frame": frame_counter,
						"detections": frame_obj_list
						}
	json_string = json.dumps(frame_detections)
	detection_file.write(json_string)
	detection_file.write(", \n")
	print(json_string)

	if writer is None:
		# initialize our video writer
		fourcc = cv2.VideoWriter_fourcc(*"MJPG")
		writer = cv2.VideoWriter("./" + get_filename(VIDEO_PATH) + ".mp4", fourcc, 30,
			(frame.shape[1], frame.shape[0]), True)

		# some information on processing single frame
		if total > 0:
			elap = (end - start)
			print("[INFO] single frame took {:.4f} seconds".format(elap))
			print("[INFO] estimated total time to finish: {:.4f}".format(
				elap * total))

	# write the output frame to disk
	#writer.write(frame)
	#cv2.imshow(WINDOW_NAME, frame)
detection_file.write("]")
# release the file pointers
print("[INFO] cleaning up...")
writer.release()
vs.release()
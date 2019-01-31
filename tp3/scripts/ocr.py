""" OCR implementation

Uses OpenCV's EAST Detector to detect regions of an image that contain words and processes
them using Tesseract to obtain text.

The path to the image must be passed as parameter to the script, as well as the .pb file
used to train OpenCV's EAST detector.

Usage: python3 ocr.py --east [PATH_TO_PB_FILE] --image [PATH_TO_IMAGE]

This is an adaptation of a tutorial that can be found at
https://www.pyimagesearch.com/2018/09/17/opencv-ocr-and-text-recognition-with-tesseract/.
"""

import sys
import argparse
import numpy as np
import pytesseract
from imutils.object_detection import non_max_suppression
import cv2


def cmp_to_key(function):
    """
    Converts a cmp= function into a key= function
    """
    class Key():
        """
        Key class
        """
        def __init__(self, obj):
            self.obj = obj

        def __lt__(self, other):
            return function(self.obj, other.obj) < 0

        def __gt__(self, other):
            return function(self.obj, other.obj) > 0

        def __eq__(self, other):
            return function(self.obj, other.obj) == 0

        def __le__(self, other):
            return function(self.obj, other.obj) <= 0

        def __ge__(self, other):
            return function(self.obj, other.obj) >= 0

        def __ne__(self, other):
            return function(self.obj, other.obj) != 0
    return Key


def my_cmp(x_1, x_2):
    """
    Compare function used to sort the result coordinates in natural order (from top to
    bottom and left to right).
    """
    if x_1[0][1] - x_2[0][1] < 10:  # margin of 10 units
        return x_1[0][0] - x_2[0][0]

    return x_1[0][1] - x_2[0][1]


def decode_predictions(scores, geometry, args):
    """
    Uses a deep learning-based text detector to detect (not recognize) regions of text in
    an image. The text detector produces two arrays, one containing the probability of a
    given area containing text, and another that maps the score to a bounding box location
    in the input image.
    """
    # grab the number of rows and columns from the scores volume, then
    # initialize our set of bounding box rectangles and corresponding
    # confidence scores
    (num_rows, num_cols) = scores.shape[2:4]
    rects = []
    confidences = []

    # loop over the number of rows
    for y_coord in range(0, num_rows):
        # extract the scores (probabilities), followed by the
        # geometrical data used to derive potential bounding box
        # coordinates that surround text
        scores_data = scores[0, 0, y_coord]
        x_data0 = geometry[0, 0, y_coord]
        x_data1 = geometry[0, 1, y_coord]
        x_data2 = geometry[0, 2, y_coord]
        x_data3 = geometry[0, 3, y_coord]
        angles_data = geometry[0, 4, y_coord]

        # loop over the number of columns
        for x_coord in range(0, num_cols):
            # if our score does not have sufficient probability,
            # ignore it
            if scores_data[x_coord] < args["min_confidence"]:
                continue

            # compute the offset factor as our resulting feature
            # maps will be 4x smaller than the input image
            (offset_x, offset_y) = (x_coord * 4.0, y_coord * 4.0)

            # extract the rotation angle for the prediction and
            # then compute the sin and cosine
            angle = angles_data[x_coord]
            cos = np.cos(angle)
            sin = np.sin(angle)

            # use the geometry volume to derive the width and height
            # of the bounding box
            height = x_data0[x_coord] + x_data2[x_coord]
            width = x_data1[x_coord] + x_data3[x_coord]

            # compute both the starting and ending (x, y)-coordinates
            # for the text prediction bounding box
            end_x = int(offset_x + (cos * x_data1[x_coord]) + (sin * x_data2[x_coord]))
            end_y = int(offset_y - (sin * x_data1[x_coord]) + (cos * x_data2[x_coord]))
            start_x = int(end_x - width)
            start_y = int(end_y - height)

            # add the bounding box coordinates and probability score
            # to our respective lists
            rects.append((start_x, start_y, end_x, end_y))
            confidences.append(scores_data[x_coord])

    # return a tuple of the bounding boxes and associated confidences
    return rects, confidences


def arg_parser():
    """
    Construct the argument parser and parse the arguments
    """
    arg_parse = argparse.ArgumentParser()
    arg_parse.add_argument("-i", "--image", type=str,
                           help="path to input image")
    arg_parse.add_argument("-east", "--east", type=str,
                           help="path to input EAST text detector")
    arg_parse.add_argument("-c", "--min-confidence", type=float, default=0.5,
                           help="min probability required to inspect a region")
    arg_parse.add_argument("-w", "--width", type=int, default=320,
                           help="nearest multiple of 32 for resized width")
    arg_parse.add_argument("-e", "--height", type=int, default=320,
                           help="nearest multiple of 32 for resized height")
    arg_parse.add_argument("-p", "--padding", type=float, default=0.0,
                           help="amount of padding to add to each border of ROI")
    args = vars(arg_parse.parse_args())

    return args


def load_img(args):
    """
    Loads the image
    """
    # load the input image and grab the image dimensions
    image = cv2.imread(args["image"])
    orig = image.copy()
    (orig_h, orig_w) = image.shape[:2]

    # set the new width and height and then determine the ratio in change
    # for both the width and height
    (new_w, new_h) = (args["width"], args["height"])
    r_w = orig_w / float(new_w)
    r_h = orig_h / float(new_h)

    # resize the image and grab the new image dimensions
    image = cv2.resize(image, (new_w, new_h))
    (height, width) = image.shape[:2]

    return args, image, width, height, r_w, r_h, orig_w, orig_h, orig


def east_detector(args, image, width, height):
    """
    Detects the location of the words in the image using OpenCV's EAST Detector
    """
    # define the two output layer names for the EAST detector model that
    # we are interested -- the first is the output probabilities and the
    # second can be used to derive the bounding box coordinates of text
    layer_names = [
        "feature_fusion/Conv_7/Sigmoid",
        "feature_fusion/concat_3"
    ]

    # load the pre-trained EAST text detector
    print("[INFO] loading EAST text detector...", file=sys.stderr)
    net = cv2.dnn.readNet(args["east"])

    # construct a blob from the image and then perform a forward pass of
    # the model to obtain the two output layer sets
    blob = cv2.dnn.blobFromImage(image, 1.0, (width, height),
                                 (123.68, 116.78, 103.94), swapRB=True, crop=False)
    net.setInput(blob)
    (scores, geometry) = net.forward(layer_names)

    # decode the predictions, then  apply non-maxima suppression to
    # suppress weak, overlapping bounding boxes
    (rects, confidences) = decode_predictions(scores, geometry, args)
    boxes = non_max_suppression(np.array(rects), probs=confidences)

    return boxes, args


def build_results(boxes, r_w, r_h, args, orig_w, orig_h, orig):
    """
    Builds results
    """
    # initialize the list of results
    results = []

    # loop over the bounding boxes
    for (start_x, start_y, end_x, end_y) in boxes:
        # scale the bounding box coordinates based on the respective
        # ratios
        start_x = int(start_x * r_w)
        start_y = int(start_y * r_h)
        end_x = int(end_x * r_w)
        end_y = int(end_y * r_h)

        # in order to obtain a better OCR of the text we can potentially
        # apply a bit of padding surrounding the bounding box -- here we
        # are computing the deltas in both the x and y directions
        d_x = int((end_x - start_x) * args["padding"])
        d_y = int((end_y - start_y) * args["padding"])

        # apply padding to each side of the bounding box, respectively
        start_x = max(0, start_x - d_x)
        start_y = max(0, start_y - d_y)
        end_x = min(orig_w, end_x + (d_x * 2))
        end_y = min(orig_h, end_y + (d_y * 2))

        # extract the actual padded ROI
        roi = orig[start_y:end_y, start_x:end_x]

        # in order to apply Tesseract v4 to OCR text we must supply
        # (1) a language, (2) an OEM flag of 4, indicating that the we
        # wish to use the LSTM neural net model for OCR, and finally
        # (3) an OEM value, in this case, 7 which implies that we are
        # treating the ROI as a single line of text
        config = "-l por --oem 1 --psm 7"
        text = pytesseract.image_to_string(roi, config=config)

        # add the bounding box coordinates and OCR'd text to the list
        # of results
        results.append(((start_x, start_y, end_x, end_y), text))

    return results


def print_results(results):
    """
    Prints results
    """
    # Results

    text = ""

    # sorts the results in natural order (from top to bottom and left to right)
    results.sort(key=cmp_to_key(my_cmp), reverse=False)

    # for each result gets the text obtained (r[-1]) and joins them all
    for res in results:
        text += "".join([c if ord(c) < 128 else "" for c in res[-1]]) + " "

    print(text)


ARGS = arg_parser()

ARG, IMAGE, W, H, R_W, R_H, ORIG_W, ORIG_H, ORIG = load_img(ARGS)

BOXES, ARGS = east_detector(ARGS, IMAGE, W, H)

RESULTS = build_results(BOXES, R_W, R_H, ARGS, ORIG_W, ORIG_H, ORIG)

print_results(RESULTS)

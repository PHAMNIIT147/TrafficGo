'''
 # @ Author: Pham Thanh Phong
 # @ Create Time: 2020-07-17 10:24:34
 # @ Modified by:  VAA Ai Go!
 # @ Modified time: 2020-07-17 10:25:54
 # @ Description:
 - More formally, in order to apply Intersection over Union to evaluate an (arbitrary) object detector we need:

   1. The ground-truth bounding boxes (i.e., the hand labeled bounding boxes from the testing set that specify where in the image our object is).
   2. The predicted bounding boxes from our model.
 - As long as we have these two sets of bounding boxes we can apply Intersection over Union.
 * formular:
 => IoU = Area of Overlap / Area of Union
 * Notation paramater
  - bb: bounding box 
 '''
import numpy as np

# RETURN: N/A


def boundingBoxIoU(bb_test, bb_ground_truth):
    # determine the (x, y)-coordinates of the intersection rectangle
    xx1 = np.maximum(bb_test[0], bb_ground_truth[0])
    yy1 = np.maximum(bb_test[1], bb_ground_truth[1])
    xx2 = np.minimum(bb_test[2], bb_ground_truth[2])
    yy2 = np.minimum(bb_test[3], bb_ground_truth[3])

    # compute the area of intersection rectangle
    width = np.maximum(0., xx2 - xx1 + 1)
    height = np.maximum(0., yy2 - yy1 + 1)
    interArea = width * height

    # compute the area both the prediction and ground-truth
    # rectangle
    # predicted bounding box
    boxX_2X_1Area = (bb_test[2] - bb_test[0] + 1) * \
        (bb_test[3] - bb_test[1] + 1)
    # ground-truth bounding box
    boxY_2Y_1Area = (bb_ground_truth[3] - bb_ground_truth[0] + 1) * \
        (bb_ground_truth[3] - bb_ground_truth[1] + 1)
    # debug
    print(boxX_2X_1Area)
    print(boxY_2Y_1Area)

    iou = interArea / float(boxX_2X_1Area + boxY_2Y_1Area - interArea)

    return iou

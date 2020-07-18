'''
 # @ Author: Pham Thanh Phong
 # @ Create Time: 2020-07-18 10:18:04
 # @ Modified by: VAA Ai Go!
 # @ Modified time: 2020-07-18 10:18:14
 # @ Description:
  -  Assigns detections to tracked object (both represented as bounding boxes)
  -  Returns 3 lists o:
    +  matches, 
    + unmatched_detections 
    + unmatched_trackers
 '''


import numpy as np
from src.core.yolo_sort.intersection_over_union import boundingBoxIoU
from src.core.yolo_sort.linear_asignment import linearAsignment

def associateDetectionAndTracker(detections, trackers, iou_threshold = 0.5):
    if len(trackers) == 0:
        return np.empty((0,2),int), np.array(len(detections)), np.empty((0,5), int)
    iou_matrix = np.zeros((len(detections), len(trackers)), float)

    for _distance, _detection in enumerate(detections):
        for _temp, _tracker in enumerate(trackers):
            iou_matrix[_distance] = boundingBoxIoU(_detection, _tracker)
    
    if min(iou_matrix.shape) > 0:
        _associate = (iou_matrix > iou_threshold).astype(np.int32)
        if _associate.sum(1).max() == 1 and _associate.sum(0).max() == 1:
            matched_indices = np.stack(np.where(_associate), axis=1)
        else:
            matched_indices = linearAsignment(-iou_matrix)
    else:
        matched_indices = np.empty((0,2))

    unmatched_detections = []
    for _distance, _detection in enumerate(detections):
        if(_distance not in matched_indices[:,0]):
            unmatched_detections.append(_distance)
    
    unmatched_trackers = []
    for _temp, _tracker in enumerate(trackers):
        if(_temp not in matched_indices[:, 1]):
            unmatched_trackers.append(_temp)
    
    #filter out matched with low IoU
    matches = []
    for match in matched_indices:
        if(iou_matrix[match[0], match[1]] < iou_threshold):
            unmatched_detections.append(match[0])
            unmatched_trackers.append(match[1])
        else:
            matches.append(match.reshape(1,2))
        
    if(len(matches) == 0):
        matches = np.empty((0,2),int)
    else:
        matches = np.concatenate(matches, axis = 0)
    
    return matches, np.array(unmatched_detections), np.array(unmatched_trackers)




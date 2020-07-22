'''
 # @ Author: Your name
 # @ Create Time: 2020-07-17 11:24:32
 # @ Modified by: Your name
 # @ Modified time: 2020-07-17 12:09:51
 # @ Description:

    1. update(self, detections)
    - Params: 
        detections - a numpy array of detections in the format [[x,y,w,h,score],[x,y,w,h,score],...]
            Requires: this method must be called once for each frame even with empty detections.
            Returns the a similar array, where the last column is the object ID.
            NOTE: The number of objects returned may differ from the number of detections provided.
 '''

import numpy as np
from src.core.yolo_sort.associate_det_and_tracker import associateDetectionAndTracker
from src.core.yolo_sort.kalman_box_tracker import KalmanBoxTracker


class Sort(object):
    def __init__(self, max_age=1, min_hits=1):
        super().__init__()
        self.max_age = max_age
        self.min_hits = min_hits
        self.trackers = []
        self.frame_count = 0

    def update(self, detections):
        ############################################
        # PREVENT " TOO MANY INDICES FOR ARRAY" ERROR
        ############################################
        if len(detections) == 0:
            return np.empty((0, 5))

        self.frame_count += 1
        # get predicted locations from existing trackers
        trackers = np.zeros((len(self.trackers), 5))
        to_del = []
        ret = []
        for _temp, _tracker in enumerate(trackers):
            pos = self.trackers[_temp].predict()[0]
            _tracker[:] = [pos[0], pos[1], pos[2], pos[3], 0]
            if np.array(np.isnan(pos)):
                to_del.append(_temp)
        trackers = np.ma.compress_rows(np.ma.masked_invalid(trackers))
        for _temp in reversed(to_del):
            self.trackers.pop(_temp)
        matched, unmatched_detections, unmatched_trackers = associateDetectionAndTracker(
            detections, trackers)

        # update matched trackers with assigned detections
        for match in matched:
            self.trackers[match[1]].update(detections[match[0], :])

        # create and initialise new trackers for unmatched detections
        for i in unmatched_detections:
            tracker = KalmanBoxTracker(detections[i, :])
            self.trackers.append(tracker)
        i = len(self.trackers)
        for tracker in reversed(self.trackers):
            distance = tracker.get_state()[0]
            if((tracker.time_since_update < 1) and (tracker.hit_streak >= self.min_hits or self.frame_count <= self.min_hits)):
                ret.append(np.concatenate(
                    (distance, [tracker.id+1])).reshape(1, -1))  # if +1 as MOT
            i -= 1
            # remove dead tracklet
            if (tracker.time_since_update > self.max_age):
                self.trackers.pop(i)
        if(len(ret) > 0):
            return np.concatenate(ret)
        return np.empty((0, 5))

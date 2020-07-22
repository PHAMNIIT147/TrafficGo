'''
 # @ Author: Pham Thanh Phong
 # @ Create Time: 2020-07-18 11:16:31
 # @ Modified by: VAA Ai Go!
 # @ Modified time: 2020-07-18 11:16:34
 # @ Description:
 - Kalman filtering, also known as linear quadratic estimation (LQE), is an algorithm that uses a series of measurements observed over time, containing statistical noise and other inaccuracies, and produces estimates of unknown variables that tend to be more accurate than those based on a single measurement alone, by estimating a joint probability distribution over the variables for each timeframe

 class:
    + This class represents the internal state of individual tracked objects observed as bbox.
 '''

import numpy as np
from filterpy.kalman import KalmanFilter
from src.core.yolo_sort.convert_bounding_box import *


class KalmanBoxTracker(object):
    count = 0

    def __int__(self, bbox):
        ####################################################
        # INITIALISE A TRACKER USING INITALISE BOUNDING BOX
        ####################################################

        # define constant velocity model
        self.kf = KalmanFilter(dim_x=7, dim_z=4)
        self.kf.F = np.array([
            [1, 0, 0, 0, 1, 0, 0],
            [0, 1, 0, 0, 0, 1, 0],
            [0, 0, 1, 0, 0, 0, 1],
            [0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 1]])
        self.kf.H = np.array([
            [1, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0]])

        self.kf.R[2:, 2:] *= 10.
        self.kf.P[4:, 4:] *= 1000.  # give high uncertainty to the unobservable initial velocities
        self.kf.P *= 10.
        self.kf.Q[-1, -1] *= 0.01
        self.kf.Q[4:, 4:] *= 0.01

        self.kf.x[:4] = convert_bb_to_z(bbox)
        self.time_since_update = 0
        # define id object
        self.id = KalmanBoxTracker.count
        KalmanBoxTracker.count += 1

        # storage identify each object
        self.history = []
        self.hits = 0
        self.hit_streak = 0
        self.age = 0

    def update(self, bbox):
        #####################################################
        # UPDATE THE STATE VECTOR WITH OBSERVED BOUNDING BOX
        #####################################################
        self.time_since_update = 0
        self.history = []
        self.hits += 1
        self.hit_streak += 1
        self.age = 0

    def predict(self):
        ############################################################################
        # ADVANCES THE STATE VECTOR AND RETURNS THE PREDICTED BOUNDING BOX ESTIMATED
        ############################################################################
        if ((self.kf.x[6] + self.kf.x[2]) <= 0):
            self.kf.x[6] *= 0.0
        self.kf.predict()
        self.age += 1
        if(self.time_since_update > 0):
           self.hit_streak = 0
        self.time_since_update += 1
        self.history.append(convert_x_to_bb(self.kf.x))

        return self.history[-1]
   
    def get_state(self):
        ##########################################
        # RETURN THE CURRENT BOUNDING BOX ESTIMATE
        ##########################################
        return convert_x_to_bb(self.kf.x)



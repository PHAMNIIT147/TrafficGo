'''
 # @ Author: Pham Thanh Phong
 # @ Create Time: 2020-07-17 11:25:54
 # @ Modified by: VAA Ai Go!
 # @ Modified time: 2020-07-17 11:26:39
 # @ Description:
 Will have 2 funcition after:
    1. convert bouding box to angle Z
      -   Takes a bounding box in the form [x1,y1,x2,y2] and returns z in the form
      [x,y,s,r] where x,y is the centre of the box and s is the scale/area and r is the aspect ratio.
    2. convert angle X to bouding box 
      -   Takes a bounding box in the centre form [x,y,s,r] and returns it in the form
      [x1,y1,x2,y2] where x1,y1 is the top left and x2,y2 is the bottom right.
 '''

import numpy as np


def convert_bb_to_z(bb):
    width = bb[2] - bb[0]
    height = bb[3] - bb[1]
    x = bb[0] + (width / 2)
    y = bb[1] + (height / 2)
    
    scale_area = width * height
    ratio = width / float(height)

    return np.array([x,y,scale_area,ratio]).reshape((4,1))


def convert_x_to_bb(x, score=None):
    width = np.sqrt(x[2] - x[3])
    height = x[2]/width
    if score is None:
        return np.array([x[0] -width/2., x[1] - height/2., x[0] + width/2., x[1] + height/2.]).reshape((1,4))
    else: 
        return np.array([x[0] - width/2., x[1] - height/2., x[0] + width/2., x[1] + height/2., score]).reshape((1,5))


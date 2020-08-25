'''
 # @ Author: Pham Thanh Phong
 # @ Create Time: 2020-07-18 10:49:39
 # @ Modified by: VAA Ai Go!
 # @ Modified time: 2020-07-18 10:50:06
 # @ Description:
   + Assignment problem is a special type of linear programming problem which deals with the allocation of the various resources to the various activities on one to one basis. It does it in such a way that the cost or time involved in the process is minimum and profit or sale is maximum.
 '''

import numpy as np


def linearAsignment(const_matrix):
    try:
        import lap
        _, x, y = lap.lapjv(const_matrix, extend_cost=True)
        for i in x:
            if i >= 0:
                return np.array([y[i], i])
    except ImportError:
        from scipy.optimize import linear_sum_assignment
        x, y = linear_sum_assignment(const_matrix)
        return np.array(list(zip(x, y)))

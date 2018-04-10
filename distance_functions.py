# ----------------------------------------------------------------------------------------------
# ----------------------------------- Distance Functions----.-----------------------------------
# ----------------------------------------------------------------------------------------------
import numpy as np

def manhattan_distance(u,v): 
    return np.sum(np.abs(u - v))

def chebychev_distance(u,v):
    return np.max(np.abs(u - v))

def hamming_distance(u,v):
    return (np.array(u) == np.array(v)).sum

def eucliedian_distance(u,v):
    return np.linalg.norm(u-v)




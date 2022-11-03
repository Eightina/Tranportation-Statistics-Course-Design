import pandas as pd

import numpy as np
import matplotlib.pyplot as plt

from shapely.geometry import Point
from shapely.geometry import LineString

from utils.maputils import generate_3857_df, generate_lines,\
                            generate_buffers,generate_base_length\

from utils.routineutils import generate_routine, generate_adjusted_geometry,\
                                generate_belonging_relations, \
                                generate_cum_length, generate_correct_geometry,\
                                generate_station_status\
                                    ,generate_interpolation
            
from utils.timeutils import time_transfer

import os

def get_gpsdf(filename):
    gpsdf = pd.read_csv('./data/gps/' + filename)
    gpsdf = time_transfer(gpsdf)
    gpsdf = generate_3857_df(gpsdf)
    return gpsdf

def get_linedf(direction):
    if direction == 0:
        path = './data/map/map_up.xlsx'
    else:
        path = './data/map/map_down.xlsx'
    mapdf = pd.read_excel(path)
    mapdf = generate_3857_df(mapdf)
    linedf = generate_lines(mapdf)
    linedf = generate_buffers(linedf)
    linedf = generate_base_length(linedf)
    return linedf

def get_processed_routine(gpsdf, nidx:int, direction:int):
    routine = generate_routine(gpsdf, nidx = nidx, direction = direction)
    mapline = get_linedf(direction)
    routine = generate_belonging_relations(routine, mapline)
    routine = generate_adjusted_geometry(routine)
    routine = generate_cum_length(routine, mapline)
    routine = generate_correct_geometry(routine)
    routine = generate_interpolation(routine)
    routine = generate_station_status(routine)
    return routine
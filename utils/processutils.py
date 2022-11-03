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

def process_gpsdf(filename):
    gpsdf = pd.read_csv('./data/gps/' + filename)
    gpsdf = time_transfer(gpsdf)
    gpsdf = generate_3857_df(gpsdf)
    return gpsdf

def process_linedf(direction):
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

def preprocess_routine(gpsdf, linedfup, linedfdown):
    gpsdf.loc[gpsdf['direction'] == 0] = generate_belonging_relations(gpsdf, linedfup)
    gpsdf.loc[gpsdf['direction'] == 1] = generate_belonging_relations(gpsdf, linedfdown)
    gpsdf = generate_adjusted_geometry(gpsdf)
    gpsdf.loc[gpsdf['direction'] == 0] = generate_cum_length(gpsdf, linedfup)
    gpsdf.loc[gpsdf['direction'] == 1] = generate_cum_length(gpsdf, linedfdown)
    return gpsdf

# mapline = process_linedf(direction)

def process_routine(gpsdf, nidx:int, direction:int):
    routinedf = generate_routine(gpsdf, nidx = nidx, direction = direction)
    # routine = generate_belonging_relations(routine, linedf)
    # routine = generate_adjusted_geometry(routine)
    # routinedf = generate_cum_length(routinedf, linedf)
    routinedf = generate_correct_geometry(routinedf)
    routinedf = generate_interpolation(routinedf)
    routinedf = generate_station_status(routinedf)
    return routinedf
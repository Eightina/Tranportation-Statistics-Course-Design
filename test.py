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

from tqdm.autonotebook import tqdm

import warnings
warnings.filterwarnings("ignore")

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

# def preprocess_routine(gpsdf, linedfup, linedfdown):
#     gpsdf.loc[gpsdf['direction'] == 0] = generate_belonging_relations(gpsdf.loc[gpsdf['direction'] == 0], linedfup)
#     gpsdf.loc[gpsdf['direction'] == 1] = generate_belonging_relations(gpsdf.loc[gpsdf['direction'] == 1], linedfdown)
#     gpsdf = generate_adjusted_geometry(gpsdf)
#     gpsdf.loc[gpsdf['direction'] == 0] = generate_cum_length(gpsdf.loc[gpsdf['direction'] == 0], linedfup)
#     gpsdf.loc[gpsdf['direction'] == 1] = generate_cum_length(gpsdf.loc[gpsdf['direction'] == 1], linedfdown)
#     return gpsdf

# mapline = process_linedf(direction)

def process_routine(gpsdf, linedf, nidx:int, direction:int):
    routinedf = generate_routine(gpsdf, nidx = nidx, direction = direction)
    if len(routinedf) < 30:
        return pd.DataFrame()
    routinedf = generate_belonging_relations(routinedf, linedf)
    routinedf = generate_adjusted_geometry(routinedf)
    routinedf = generate_cum_length(routinedf, linedf)
    routinedf = generate_correct_geometry(routinedf)
    routinedf = generate_interpolation(routinedf)
    routinedf = generate_station_status(routinedf)
    return routinedf

# filename_list = os.listdir('./data/gps/')
filename_list = ['gps_0906.csv']
mapline_up = process_linedf(0)
mapline_down = process_linedf(1)
for filename in filename_list:
    # gps = process_gpsdf(filename)
    gps = process_gpsdf(filename)
    nidx_list = gps.nidx.unique()
    # nidx_list = [9,10,11]
    direction_list = [0, 1]
    res = pd.DataFrame()
    for i,nidx in enumerate(nidx_list):
        print('nidx:'+str(i)+'/'+str(len(nidx_list)-1))
        for direction in direction_list:
            print('nidx:'+str(nidx)+','+'direction:'+str(direction))
            if direction == 0:
                routine = process_routine(gps, linedf = mapline_up, nidx = nidx, direction = direction)
            else:
                routine = process_routine(gps, linedf = mapline_down, nidx = nidx, direction = direction)
            res = pd.concat([res, routine], ignore_index=True).reset_index(drop = True)
    res.to_csv('test.csv')
    


import pandas as pd

from myutils.map_utils import generate_3857_df, generate_lines,\
                            generate_buffers,generate_base_length\

from myutils.routine_utils import generate_routine, generate_adjusted_geometry,\
                                generate_belonging_relations, \
                                generate_cum_length, generate_correct_geometry,\
                                generate_station_status,\
                                generate_interpolation, remove_negative_row_end
            
from myutils.time_utils import time_transfer


from datetime import datetime as dt

import os

# from tqdm.autonotebook import tqdm



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
    if len(routinedf) < 5:
        return pd.DataFrame()
    routinedf = generate_belonging_relations(routinedf, linedf)
    routinedf = generate_adjusted_geometry(routinedf)
    routinedf = generate_cum_length(routinedf, linedf)
    routinedf = generate_correct_geometry(routinedf)
    routinedf = generate_interpolation(routinedf, linedf)
    routinedf = generate_station_status(routinedf)
    return routinedf

def post_process(routinedf, date:int):
    routinedf = remove_negative_row_end(routinedf)
    hilim = pd.Timestamp(dt(2021,9,date, hour=23,minute=59,second=59))
    lolim = pd.Timestamp(dt(2021,9,date, hour=4,minute=0,second=0))
    routinedf = routinedf.drop(routinedf.loc[(routinedf['time'] > hilim) | (routinedf['time'] < lolim)].index,
                    axis = 0
                ).reset_index(drop=True)
    return routinedf

def timetable_format(timetable_row, date:int, restriction:list):
    # if strict:
    lo_range = pd.Timedelta( minutes = restriction[0] )
    hi_range = pd.Timedelta( minutes = restriction[1] )
        
    start_time = timetable_row['start_time'].split(':')
    start_time = pd.Timestamp(dt(2021,9,date, hour=int(start_time[0]),minute=int(start_time[1]),second=int(start_time[2])))
    timetable_row['start_time'] = start_time
    timetable_row['start_time_lolim'] = start_time - lo_range
    timetable_row['start_time_hilim'] = start_time + hi_range

    end_time = timetable_row['end_time'].split(':')
    end_time = pd.Timestamp(dt(2021,9,date, hour=int(end_time[0]),minute=int(end_time[1]),second=int(end_time[2])))
    timetable_row['end_time'] = end_time
    timetable_row['end_time_lolim'] = end_time - lo_range
    timetable_row['end_time_hilim'] = end_time + hi_range
    return timetable_row

def process_timetable(timetabledf, date:int, restriction:list):
    timetabledf['start_time_lolim'] = [None for _ in range(len(timetabledf))]
    timetabledf['start_time_hilim'] = [None for _ in range(len(timetabledf))]
    timetabledf['end_time_lolim'] = [None for _ in range(len(timetabledf))]
    timetabledf['end_time_hilim'] = [None for _ in range(len(timetabledf))]
    timetabledf = timetabledf.apply(timetable_format, args=(date, restriction,), axis = 1)
    return timetabledf
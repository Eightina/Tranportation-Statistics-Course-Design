import pandas as pd
import geopandas as gpd
from myutils.routine_utils import generate_routine
from myutils.process_utils import process_timetable
import matplotlib.pyplot as plt
from datetime import datetime as dt

def load_daydf(day:int):
    res = pd.read_pickle('./data/output/gps_{}.pkl'.format(day))
    # print(res.columns)
    # print(len(res))
    return res

def load_test_daydf(day):
    res = pd.read_pickle('./data/testoutput/gps_{}.pkl'.format(day))
    # print(res.columns)
    # print(len(res))
    return res

def load_routinedf(daydf, nidx = 0, direction = 0):
    routinedf = generate_routine(daydf, nidx, direction)
    return routinedf

def map_plot(linedf, routinedf, *lim):
    plt_mapline = gpd.GeoDataFrame(linedf)
    plt_routine = gpd.GeoDataFrame(routinedf)
    fig, ax = plt.subplots(1,2,figsize=(6,6),dpi=300)
    plt_mapline['rect_buffer'].plot(ax = ax[0], color = 'blue', alpha=0.3)
    plt_mapline.plot(ax = ax[0], color = 'orange',alpha=0.6)
    plt_routine.plot(ax = ax[0], color = 'red', alpha = 0.5, markersize = 5)

    plt_mapline['rect_buffer'].plot(ax = ax[1], color = 'blue', alpha=0.3)
    plt_mapline.plot(ax = ax[1], color = 'orange',alpha=0.6)
    adjusted_routine = gpd.GeoDataFrame({'geometry':plt_routine['adjusted_geometry']})
    adjusted_routine.plot(ax = ax[1], color = 'red', alpha = 0.5, markersize = 5)
    
    if lim:
        ax[0].set_xlim(lim[0])
        ax[1].set_xlim(lim[0])
        ax[0].set_ylim(lim[1])
        ax[1].set_ylim(lim[1])
    
    return ax



def time_matching(truetime_row, timetabledf):
    mintime = truetime_row['min']
    maxtime = truetime_row['max']
    start_time_lolim = timetabledf['start_time_lolim']
    start_time_hilim = timetabledf['start_time_hilim']
    end_time_lolim = timetabledf['end_time_lolim']
    end_time_hilim = timetabledf['end_time_hilim']
    
    sp_start_tar = timetabledf.loc[
                (
                    (start_time_lolim <= (maxtime - pd.Timedelta(minutes=1.5))) 
                    & (start_time_hilim >= (maxtime - pd.Timedelta(minutes=1.5)))
                )
        ].reset_index(drop = True)
    sp1_start_tar = timetabledf.loc[
                (
                    (start_time_lolim <= (maxtime - pd.Timedelta(minutes=1))) 
                    & (start_time_hilim >= (maxtime- pd.Timedelta(minutes=1)))
                )
        ].reset_index(drop = True)
    end_tar = timetabledf.loc[
                (
                    ( end_time_lolim <= mintime) 
                    & ( end_time_hilim >= mintime)
                )
        ].reset_index(drop = True)
    
    if truetime_row['direction'] == 0:
        if truetime_row['station_status'] == '菊园车站':
            if len(sp_start_tar) > 0:
                truetime_row['max'] -= pd.Timedelta(minutes=1.5)
                truetime_row['intime'] = True
                truetime_row['lolim'] = sp_start_tar['start_time_lolim'][0]
                truetime_row['hilim'] = sp_start_tar['start_time_hilim'][0]
        else:
            if len(end_tar) > 0:
                truetime_row['intime'] = True
                truetime_row['lolim'] = end_tar['end_time_lolim'][0]
                truetime_row['hilim'] = end_tar['end_time_hilim'][0]
    else:
        if truetime_row['station_status'] == '公交嘉定新城站':
            if len(sp1_start_tar) > 0:
                truetime_row['max'] -= pd.Timedelta(minutes=1)
                truetime_row['intime'] = True
                truetime_row['lolim'] = sp1_start_tar['start_time_lolim'][0]
                truetime_row['hilim'] = sp1_start_tar['start_time_hilim'][0]
        else:
            if len(end_tar) > 0:
                truetime_row['intime'] = True
                truetime_row['lolim'] = end_tar['end_time_lolim'][0]
                truetime_row['hilim'] = end_tar['end_time_hilim'][0]
    
    return truetime_row


def generate_intime(date='06', time_range=[0, 0, 23, 59], restriction = [1, 2]):
    # for date in ['06','07','08','09','10']:
    lolim = dt(2021, 9 , int(date), hour=int(time_range[0]),minute=int(time_range[1]),second=0)
    hilim = dt(2021, 9 , int(date), hour=int(time_range[2]),minute=int(time_range[3]),second=0)
    
    path_timetable = './data/timetable/'
    timetable_up = pd.read_csv(path_timetable + 'timetable_up_09' + date + '.csv')
    timetable_up = process_timetable(timetable_up, int(date), restriction)
    timetable_down = pd.read_csv(path_timetable + 'timetable_down_09' + date + '.csv')
    timetable_down = process_timetable(timetable_down, int(date), restriction)
    
    path_truetime = './data/analysis/'
    truetime_up = pd.read_pickle(path_truetime + 'truetime_up_09' + date + '.pkl')
    truetime_up = truetime_up.loc[(
            ((truetime_up['station_status'] == '公交嘉定新城站') | (truetime_up['station_status'] == '菊园车站'))
            & ((truetime_up['max'] >= lolim) & (truetime_up['max'] <= hilim))
        )]
    truetime_up['intime'] = [False for _ in range(len(truetime_up))]
    truetime_up['lolim'] = [None for _ in range(len(truetime_up))]
    truetime_up['hilim'] = [None for _ in range(len(truetime_up))]
    
    truetime_down = pd.read_pickle(path_truetime + 'truetime_down_09' + date + '.pkl')
    truetime_down = truetime_down.loc[(
            ((truetime_down['station_status'] == '公交嘉定新城站') | (truetime_down['station_status'] == '菊园车站'))
            & ((truetime_down['max'] >= lolim) & (truetime_down['max'] <= hilim))
        )]
    truetime_down['intime'] = [False for _ in range(len(truetime_down))]
    truetime_down['lolim'] = [None for _ in range(len(truetime_down))]
    truetime_down['hilim'] = [None for _ in range(len(truetime_down))]
    
    truetime_up = truetime_up.apply(
        time_matching, 
        args=(timetable_up,),
        # result_type='broadcast',
        axis = 1,
        )
    truetime_down = truetime_down.apply(
        time_matching, 
        args=(timetable_down,), 
        # result_type='broadcast',
        axis = 1,
        )
    
    return truetime_up,truetime_down

def generate_test_intime(date='06', time_range=[0, 0, 23, 59], restriction = [1, 2]):
    # for date in ['06','07','08','09','10']:
    lolim = dt(2021, 9 , int(date), hour=int(time_range[0]),minute=int(time_range[1]),second=0)
    hilim = dt(2021, 9 , int(date), hour=int(time_range[2]),minute=int(time_range[3]),second=0)
    
    path_timetable = './data/timetable/'
    timetable_up = pd.read_csv(path_timetable + 'timetable_up_09' + date + '.csv')
    timetable_up = process_timetable(timetable_up, int(date), restriction)
    timetable_down = pd.read_csv(path_timetable + 'timetable_down_09' + date + '.csv')
    timetable_down = process_timetable(timetable_down, int(date), restriction)
    
    path_truetime = './data/testanalysis/'
    truetime_up = pd.read_pickle(path_truetime + 'truetime_up_09' + date + '.pkl')
    truetime_up = truetime_up.loc[(
            ((truetime_up['station_status'] == '公交嘉定新城站') | (truetime_up['station_status'] == '菊园车站'))
            & ((truetime_up['max'] >= lolim) & (truetime_up['max'] <= hilim))
        )]
    truetime_up['intime'] = [False for _ in range(len(truetime_up))]
    truetime_up['lolim'] = [None for _ in range(len(truetime_up))]
    truetime_up['hilim'] = [None for _ in range(len(truetime_up))]
    
    truetime_down = pd.read_pickle(path_truetime + 'truetime_down_09' + date + '.pkl')
    truetime_down = truetime_down.loc[(
            ((truetime_down['station_status'] == '公交嘉定新城站') | (truetime_down['station_status'] == '菊园车站'))
            & ((truetime_down['max'] >= lolim) & (truetime_down['max'] <= hilim))
        )]
    truetime_down['intime'] = [False for _ in range(len(truetime_down))]
    truetime_down['lolim'] = [None for _ in range(len(truetime_down))]
    truetime_down['hilim'] = [None for _ in range(len(truetime_down))]
    
    truetime_up = truetime_up.apply(
        time_matching, 
        args=(timetable_up,),
        # result_type='broadcast',
        axis = 1,
        )
    truetime_down = truetime_down.apply(
        time_matching, 
        args=(timetable_down,), 
        # result_type='broadcast',
        axis = 1,
        )
    
    return truetime_up,truetime_down



import pandas as pd
import geopandas as gpd
from myutils.routine_utils import generate_routine
import matplotlib.pyplot as plt

def load_daydf(day):
    res = pd.read_pickle('./data/output/gps_{}.pkl'.format(day))
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

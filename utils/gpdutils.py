import geopandas as gpd
import pandas as pd
import numpy as np

from shapely.geometry import Point
from shapely.geometry import LineString

# mapdf = pd.read_excel('./data/map/map_down.xlsx')

# from lat and lon generate geodataframe 
# plus transfering coords sys
def generate_gpd(mapdf, if_to_xy:bool):

    if ('lat' in mapdf.columns):
        mapdf['lat'] = [float(_) for _ in mapdf['lat']]
        mapdf['lon'] = [float(_) for _ in mapdf['lon']]
        temp_lon_lat = np.array([mapdf['lon'],mapdf['lat']]).T

    else:
        print('name columns as lat and lon')
        return
    
    mapdf = gpd.GeoDataFrame(mapdf)
    mapdf['geometry'] = [Point(_) for _ in temp_lon_lat]
    mapdf = mapdf.set_crs(4326)
    if (if_to_xy):
        return mapdf.to_crs(3857)
    return mapdf

# generate a newgeodf with lines from a geodf with point
def generate_lines(mapdf):
    geo = []
    name= []
    cur = mapdf.loc[0]
    for i in range(len(mapdf) - 1):
        nxt = mapdf.loc[i + 1]
        geo.append(LineString([cur['geometry'], nxt['geometry']]))
        name.append(cur['name'] + "-" + nxt['name'])
        cur = nxt
    return gpd.GeoDataFrame({'name':name, 'geometry':geo})

def generate_buffers(linedf, width = 50):
    linedf['buffer'] = linedf.buffer(50, cap_style=2)
    return linedf

# extract a single routine from the whole gpsdf
def generate_routine(gpsdf, nidx:int, direction:int):
    return gpsdf.set_index(['nidx','direction']).loc[nidx].loc[direction].reset_index()

# detect whether a point is in the sub_buffer 
# if true then return the index of the sub_buffer
def point_in_buffer(buffer, i , point):
    sub_buffer = buffer.loc[i]
    res = int(sub_buffer.contains(point))
    if (res):
        return [i]
    return []

# find out all the sub_buffers in a buffer set that a point belongs to
# routine has the points
# buffer has all the buffers
def generate_belonging_relations(routinedf, linedf):
    routinedf["belong"] = pd.Series([[] for _ in range(len(routinedf))])
    buffer = linedf['buffer']
    for i in range(len(linedf)):
        routinedf["belong"] += pd.Series([point_in_buffer(buffer, i, _) for _ in routinedf['geometry']])
    return routinedf

def print_belonging_relations(routinedf):
    total = len(routinedf)
    well = len(routinedf.loc[[(len(_) == 1) for _ in routinedf['belong']]])
    multiple = len(routinedf.loc[[(len(_) > 1) for _ in routinedf['belong']]])
    none = len(routinedf.loc[[(len(_) == 0) for _ in routinedf['belong']]])
    print("length of routine is: {}".format(total))
    print("well matched: {}".format(well))
    print("multiple mathed: {}".format(multiple))
    print("none matched: {}".format(none))

def adjust(routinedf):
    pass


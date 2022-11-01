
import geopandas as gpd
import pandas as pd
import numpy as np

from shapely.geometry import Point, LineString
from shapely.ops import nearest_points

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
    linedf['circ_buffer'] = linedf.buffer(50, cap_style=1)
    linedf['rect_buffer'] = linedf.buffer(50, cap_style=2)
    return linedf

# extract a single routine from the whole gpsdf
def generate_routine(gpsdf, nidx:int, direction:int):
    return gpsdf.set_index(['nidx','direction'],drop=False).loc[nidx].loc[direction].reset_index(drop=True)

# detect whether a point is in the sub_buffer 
# if true then return the sub_buffer
def point_in_buffer(linedf, i, point):
    line = linedf['geometry'].loc[i]
    line_idx = linedf.index[i]
    sub_rect_buffer = linedf['rect_buffer'].loc[i]
    sub_circ_buffer = linedf['circ_buffer'].loc[i]
    in_sub_rect_buffer = sub_rect_buffer.contains(point)
    in_sub_circ_buffer = sub_circ_buffer.contains(point)
    res = []
    
    if (in_sub_rect_buffer):
        res.append([sub_rect_buffer])
    else:
        res.append([])
        
    if (in_sub_circ_buffer):
        res.append([sub_circ_buffer])
    else:
        res.append([])
        
    if (in_sub_rect_buffer or in_sub_circ_buffer):
        res.append([line])
        res.append([line_idx])
    else:
        res.append([])
        res.append([])
        
    
    return res

# find out all the sub_buffers in a buffer set that a point belongs to
# routine has the points
# buffer has all the buffers
def generate_belonging_relations(routinedf, linedf):
    
    routinedf["belong_rect_buffer"] = pd.Series([[] for _ in range(len(routinedf))])
    routinedf["belong_circ_buffer"] = pd.Series([[] for _ in range(len(routinedf))])
    routinedf["belong_line"] =  pd.Series([[] for _ in range(len(routinedf))])
    routinedf["belong_line_idx"] = pd.Series([[] for _ in range(len(routinedf))])
    
    for i in range(len(linedf)):
        relation = [point_in_buffer(linedf, i, _) for _ in routinedf['geometry']]
        belong_rect_buffer = [_[0] for _ in relation]
        belong_circ_buffer = [_[1] for _ in relation]
        belong_line = [_[2] for _ in relation]
        belong_line_idx = [_[3] for _ in relation]
        routinedf["belong_rect_buffer"] += pd.Series(belong_rect_buffer)
        routinedf["belong_circ_buffer"] += pd.Series(belong_circ_buffer)
        routinedf["belong_line"] += pd.Series(belong_line)
        routinedf["belong_line_idx"] += pd.Series(belong_line_idx)
    return routinedf

def print_belonging_relations(routinedf):
    total = len(routinedf)
    well = len(routinedf.loc[[(len(_) == 1) for _ in routinedf['belong_rect_buffer']]])
    multiple = len(routinedf.loc[[(len(_) > 1) for _ in routinedf['belong_rect_buffer']]])
    none = len(routinedf.loc[[(len(_) == 0) for _ in routinedf['belong_rect_buffer']]])
    print("length of routine is: {}".format(total))
    print("well matched: {}".format(well))
    print("multiple matched: {}".format(multiple))
    print("none matched: {}".format(none))

def adjust_one(routinedf, adjust_idx):
    routine_row = routinedf.loc[adjust_idx]
    len_rect_belong = len(routine_row['belong_rect_buffer'])
    len_circ_belong = len(routine_row['belong_circ_buffer'])
    point = routine_row['geometry']
    
    if (len_rect_belong == 0 and len_circ_belong == 0):
        return None
    
    dis = 1 << 63
    res = None
    res_idx = 0
    for (i, line) in enumerate(routine_row['belong_line']):
        possible_res = nearest_points(point,line)[1]
        possible_dis = point.distance(possible_res)
        if possible_dis < dis:
            res_idx = i
            res = possible_res
            dis = possible_dis
            
    selected_line = routine_row['belong_line'][res_idx]
    selected_line_idx = routine_row['belong_line_idx'][res_idx]
    del (routinedf.loc[adjust_idx])['belong_line'][res_idx]
    del (routinedf.loc[adjust_idx])['belong_line_idx'][res_idx]
    return res, selected_line, selected_line_idx

def generate_adjusted_geometry(routinedf):
    routinedf['selected_line'] = [None for _ in range(len(routinedf))]
    routinedf['selected_line_idx'] = [None for _ in range(len(routinedf))]
    res = [adjust_one(routinedf, i) for i in routinedf.index]
    routinedf['adjusted_geometry'] = [_[0]  if _ else None for _ in res]
    routinedf['selected_line']  = [_[1]  if _ else None for _ in res]
    routinedf['selected_line_idx']  = [_[2]  if _ else None for _ in res]
    return routinedf

def generate_base_length(linedf):
    temp = [_.length for _ in linedf['geometry']]
    temp.pop()
    temp = [0] + temp
    for i in range(1, len(temp)):
        temp[i] += temp[i - 1]
    linedf['base_length'] = temp
    return linedf
    
def generate_cum_length(routinedf, linedf):
    routinedf = routinedf.merge(linedf['base_length'], left_on='selected_line_idx', right_index=True, how='inner')
    temp = [row['adjusted_geometry'].distance(Point(row['selected_line'].coords[0])) for (i, row) in routinedf.iterrows()]
    routinedf['cum_length'] = routinedf['base_length'] + temp
    return routinedf

def 
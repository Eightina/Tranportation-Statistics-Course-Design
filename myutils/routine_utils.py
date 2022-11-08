import pandas as pd

# import modin.pandas as pd
import numpy as np

from shapely.geometry import Point, LineString
from shapely.ops import nearest_points

# from tqdm.autonotebook import tqdm

# mapdf = pd.read_excel('./data/map/map_down.xlsx')

# extract a single routine from the whole gpsdf
def generate_routine(gpsdf, nidx:int, direction:int):
    # return gpsdf.set_index(['nidx','direction'],drop=False).loc[nidxdirection].reset_index(drop=True)
    return gpsdf.loc[((gpsdf['nidx'] == nidx) & (gpsdf['direction'] == direction))].reset_index(drop=True)

# detect whether a point is in the sub_buffer 
# if true then return the sub_buffer
def point_in_buffer(routine_row, line_row, i):
    point = routine_row['geometry']
    line = line_row['geometry']
    line_idx = i

    sub_rect_buffer = line_row['rect_buffer']
    sub_circ_buffer = line_row['circ_buffer']
    in_sub_rect_buffer = sub_rect_buffer.contains(point)
    in_sub_circ_buffer = sub_circ_buffer.contains(point)
    
    if (in_sub_rect_buffer):
        routine_row["belong_rect_buffer"].append(sub_rect_buffer)

    if (in_sub_circ_buffer):
        routine_row["belong_circ_buffer"].append(sub_circ_buffer)        

        
    if (in_sub_rect_buffer or in_sub_circ_buffer):
        routine_row['belong_line'].append(line)
        routine_row['belong_line_idx'].append(line_idx)        

    return routine_row

# find out all the sub_buffers in a buffer set that a point belongs to
# routine has the points
# buffer has all the buffers

# from functools import partial
# from multiprocessing import Pool
# import multiprocessing
# def parallelize_dataframe(df, func, **kwargs):
#     CPUs = multiprocessing.cpu_count()
#     num_partitions = CPUs # number of partitions to split dataframe
#     num_cores = CPUs  # number of cores on your machine
#     df_split = np.array_split(df, num_partitions)
#     pool = Pool(num_cores)
#     func = partial(func, **kwargs)
#     df = pd.concat(pool.map(func, df_split))
#     pool.close()
#     pool.join()
#     return df

# def parall_func_0(routinedf, point_in_buffer, line_row, i):
#     routinedf = routinedf.apply(point_in_buffer, axis = 1, args = (line_row,i))
#     return routinedf

def generate_belonging_relations(routinedf, linedf):
    
    routinedf["belong_rect_buffer"] = pd.Series([[] for _ in range(len(routinedf))])
    routinedf["belong_circ_buffer"] = pd.Series([[] for _ in range(len(routinedf))])
    routinedf["belong_line"] =  pd.Series([[] for _ in range(len(routinedf))])
    routinedf["belong_line_idx"] = pd.Series([[] for _ in range(len(routinedf))])
    
    for i in range(len(linedf)):
        # relation = pd.DataFrame([point_in_buffer(linedf, i, _) for _ in routinedf['geometry']], columns=[0, 1, 2, 3])
        # print("processing belonging relations: {}".format((i+1)/(len(linedf) + 1)))
        line_row = linedf.loc[i]
        # if parallelize:
        #     routinedf = parallelize_dataframe(routinedf, parall_func_0, point_in_buffer, line_row, i)
        # else:
        # target_col = ('geometry', 'belong_rect_buffer', 'belong_circ_buffer', 'belong_line', 'belong_line_idx')
        # tqdm.pandas(desc='generate_belonging_relations')
        routinedf = routinedf.apply(point_in_buffer, axis = 1, args = (line_row,i))
        # routinedf = routinedf.swifter.apply(point_in_buffer, axis = 1, args = (line_row,i))
        
        # routinedf["belong_rect_buffer"] += relation[0]
        # routinedf["belong_circ_buffer"] += relation[1]
        # routinedf["belong_line"] += relation[2]
        # routinedf["belong_line_idx"] += relation[3]
        
    return routinedf

# def print_belonging_relations(routinedf):
#     total = len(routinedf)
#     well = len(routinedf.loc[[(len(_) == 1) for _ in routinedf['selected_line']]])
#     multiple = len(routinedf.loc[[(len(_) > 1) for _ in routinedf['selected_line']]])
#     none = len(routinedf.loc[[(len(_) == 0) for _ in routinedf['selected_line']]])
#     print("length of routine is: {}".format(total))
#     print("well matched: {}".format(well))
#     print("multiple matched: {}".format(multiple))
#     print("none matched: {}".format(none))

def adjust_one(routine_row):
    len_rect_belong = len(routine_row['belong_rect_buffer'])
    len_circ_belong = len(routine_row['belong_circ_buffer'])
    point = routine_row['geometry']
    
    if (len_rect_belong == 0 and len_circ_belong == 0):
        return routine_row
    
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
            
    routine_row['adjusted_geometry'] = res       
    routine_row['selected_line'] = routine_row['belong_line'][res_idx]
    routine_row['selected_line_idx'] = routine_row['belong_line_idx'][res_idx]
    del routine_row['belong_line'][res_idx]
    del routine_row['belong_line_idx'][res_idx]
    return routine_row


def generate_adjusted_geometry(routinedf):
    routinedf['selected_line'] = [None for _ in range(len(routinedf))]
    routinedf['selected_line_idx'] = [None for _ in range(len(routinedf))]
    routinedf['adjusted_geometry'] = [None for _ in range(len(routinedf))]
    # routinedf = routinedf.apply(adjust_one, axis = 1)
    # tqdm.pandas(desc='generate_adjusted_geometry')
    routinedf = routinedf.apply(adjust_one, axis = 1)
    
    return routinedf
    
def generate_cum_length(routinedf, linedf):
    routinedf = routinedf.merge(linedf[['base_length','end_length', 'start_is_station', 'end_is_station', 'start', 'end']],\
                                left_on='selected_line_idx', right_index=True, how='inner')

    # tqdm.pandas(desc='generate_cum_length')
    routinedf['cur_length'] = routinedf.apply(lambda x: x['adjusted_geometry'].\
                                                distance(Point(x['selected_line'].coords[0])),
                                                axis = 1,
                                                result_type = 'reduce'
                                            )
    routinedf['cum_length'] = routinedf['cur_length'] + routinedf['base_length']
    # routinedf['cum_length'] = routinedf.swifter.apply(lambda x: x['adjusted_geometry'].\
    #                                             distance(Point(x['selected_line'].coords[0]))\
    #                                             + x['base_length'],
    #                                             axis = 1
    #                                         )
    
    return routinedf.reset_index(drop=True)


def remove_negative_row(routinedf):
    pre_len = 0
    new_len = len(routinedf)
    
    while (new_len != pre_len):
        routinedf['diff_distance'] = routinedf['cum_length'].diff()
        # routinedf['temp1'] = [len(_) for _ in routinedf['belong_line']]
        routinedf = routinedf.drop(
                routinedf.loc[(( routinedf['belong_line'].apply(lambda x: len(x)) == 0)\
                    & (routinedf["diff_distance"] < 0 ))].index,
                axis = 0
            ).reset_index(drop=True)
        # routinedf = routinedf.drop(
        #         routinedf.loc[(( routinedf['belong_line'].swifter.apply(lambda x: len(x)) == 0)\
        #             & (routinedf["diff_distance"] < 0 ))].index,
        #         axis = 0
        #     ).reset_index(drop=True)
        
        pre_len = new_len
        new_len = len(routinedf)

    routinedf['diff_time'] = routinedf['time'].diff().apply(lambda x: x.seconds)
    # routinedf.fillna(0)
    routinedf.loc[routinedf['diff_time'] > 80000, 'diff_time'] = 10
    # routinedf['velocity'] = routinedf['velocity'].swifter.apply(lambda x: x.seconds)
    routinedf['velocity'] = [0] + list(routinedf['diff_distance'][1:]/routinedf['diff_time'][1:])
    routinedf = routinedf.drop(
                routinedf.loc[(routinedf['velocity'] > (80/3.6))].index,
                axis = 0 
            ).reset_index(drop=True)
    return routinedf

def remove_negative_row_end(routinedf):
    # routinedf = routinedf.reset_index(drop=True)
    pre_len = 0
    new_len = len(routinedf)
    while (new_len != pre_len):
        routinedf['diff_distance'] = routinedf['cum_length'].diff()
        routinedf = routinedf.drop(
                    routinedf.loc[(routinedf["diff_distance"] < 0 )].index,
                    axis = 0
                ).reset_index(drop=True)
        pre_len = new_len
        new_len = len(routinedf)
    return routinedf

def adjust_two(routine_row):
    # input row has diff_distance < 0 or line >0
    if routine_row['diff_distance'] >= 0:
        return routine_row
    
    point = routine_row['geometry']
    line = routine_row['belong_line'][0]
    
    routine_row['selected_line'] = line
    del routine_row['belong_line'][0]
    routine_row['adjusted_geometry'] = nearest_points(point, line)[1]
    
    return routine_row

def generate_correct_geometry(routinedf):
    routinedf = remove_negative_row(routinedf)
    pre_len = 0
    new_len = len(routinedf)
    # print(new_len)
    while (new_len != pre_len):
        routinedf.loc[1:,:] = routinedf.loc[1:,:].apply(adjust_two, axis = 1)
        # routinedf.loc[1:,:] = routinedf.loc[1:,:].swifter.apply(adjust_two, axis = 1)
        remove_negative_row(routinedf)
        pre_len = new_len
        new_len = len(routinedf)
        # print(new_len)
    routinedf = remove_negative_row_end(routinedf)
    return routinedf

def interpolate(routine_row, linedf):
    if ((routine_row['diff_distance'] > 50) or (routine_row['diff_time'] > 30)):
        # print("trying")
        # new_row = routine_row.copy(deep=True)
        routine_row['cum_length'] -= (routine_row['diff_distance'] / 2)
        # <= routine_row['end_length'])
        if not (routine_row['base_length'] <= routine_row['cum_length']):
            change_to_line = linedf.loc[routine_row['selected_line_idx'] - 1]
            # routine_row['selected_line'] = change_to_line['geometry']
            # routine_row['base_length'] = change_to_line['base_length']
            # routine_row['end_length'] = change_to_line['end_length']
            routine_row[['selected_line', 'base_length', 'end_length', 'start_is_station', 'end_is_station', 'start', 'end']] =\
                change_to_line[['geometry', 'base_length', 'end_length','start_is_station', 'end_is_station', 'start', 'end']]
            # in this way there may be data with negative cur_length, which helps a lot !! 
            # new_point = Point(x0, y0)            
        # if routine_row['selected_line'].buffer(cap_style = 2,distance = 1e-8).contains(new_point):
        # if True:
        x0, y0 = routine_row['selected_line'].coords[0]
        x1, y1 = routine_row['selected_line'].coords[1]         
        p = (routine_row['diff_distance'] / routine_row['selected_line'].length)/2
        a = (x0 - x1) * p
        b = (y0 - y1) * p
        x2, y2 = routine_row['adjusted_geometry'].coords[0]
        new_point = Point(x2 + a, y2 + b)
        routine_row['adjusted_geometry'] = new_point
        routine_row['time'] -= pd.Timedelta( seconds = int(routine_row['diff_time'] / 2) )
        # routine_row['diff_distance'] /= 2
        # routine_row['diff_time'] /= 2
        routine_row['cur_length'] = routine_row['cum_length'] - routine_row['base_length']

        return routine_row.to_list()

def generate_interpolation(routinedf, linedf):
    pre_len = 0
    new_len = len(routinedf)
    while (pre_len != new_len):
        print(new_len)
        # inter_val = pd.DataFrame(routinedf.apply(interpolate, axis = 1, args=(linedf)).dropna().to_list(), columns = routinedf.columns)
        inter_val = routinedf.apply(interpolate, axis = 1, args=(linedf,), result_type='broadcast').dropna()
        routinedf = pd.concat([routinedf, inter_val],ignore_index=True).sort_values(by = 'time').reset_index(drop = True)
        routinedf['diff_time'] = routinedf['time'].diff().apply(lambda x: x.seconds)
        routinedf['diff_distance'] = routinedf['cum_length'].diff()
        # routinedf[]
        routinedf = routinedf.drop(
                    routinedf.loc[(routinedf["diff_distance"] < 0 )].index,
                    axis = 0
                ).reset_index(drop=True)
        pre_len = new_len
        new_len = len(routinedf)
    
    return routinedf

def in_station(routine_row):
    is_low_velocity_down = (routine_row['velocity'] <= 12.5)
    is_low_velocity_up = (routine_row['velocity'] <= 6.8)
    is_up = (routine_row['direction'] == 0)
    case0 = (routine_row['cur_length'] > 25)
    case1 = (routine_row['selected_line'].length - routine_row['cur_length'] > 25)
    
    if is_up:
        if (routine_row['start'] == '菊园车站') and (is_low_velocity_up):
            return '菊园车站'
        elif (routine_row['end'] == '公交嘉定新城站') and (is_low_velocity_up):
            return '公交嘉定新城站'
    else:
        if (routine_row['start'] == '公交嘉定新城站') and (is_low_velocity_down):
            return '公交嘉定新城站'
        elif (routine_row['end'] == '菊园车站') and (is_low_velocity_down):
            return '菊园车站'
        
    if routine_row['start_is_station']:
        if (case0):
            return 0
        else:
            return routine_row['start']
    elif routine_row['end_is_station']:
        if (case1):
            return 0
        else:
            return routine_row['end']
    return 0
        
def generate_station_status(routinedf):
    routinedf['station_status'] = routinedf.apply(in_station, axis = 1)
    return routinedf
import pandas as pd

import warnings
warnings.filterwarnings("ignore")

from myutils.process_utils import process_gpsdf, process_routine, process_linedf

filename_list = [
                    'gps_0906.csv',
                    # 'gps_0907.csv',
                    # 'gps_0908.csv',
                    # 'gps_0909.csv',
                    # 'gps_0910.csv',
                ]
# filename_list = ['gps_0906.csv']
mapline_up = process_linedf(0)
mapline_down = process_linedf(1)
# print()
cnt = 6
for filename in filename_list:
    # gps = process_gpsdf(filename)
    gps = process_gpsdf(filename)
    nidx_list = gps.nidx.unique()
    # nidx_list = [9,10,11]
    direction_list = [0, 1]
    res = pd.DataFrame()
    for i,nidx in enumerate(nidx_list):
        print(filename+'nidx:'+str(i)+'/'+str(len(nidx_list)-1))
        for direction in direction_list:
            print('nidx:'+str(nidx)+','+'direction:'+str(direction))
            if direction == 0:
                routine = process_routine(gps, linedf = mapline_up, nidx = nidx, direction = direction)
            else:
                routine = process_routine(gps, linedf = mapline_down, nidx = nidx, direction = direction)
            res = pd.concat([res, routine], ignore_index=True).reset_index(drop = True)
    res.to_pickle(path='gps_{}.pkl'.format(cnt))
    cnt += 1 


# /root/log/run_7370.log
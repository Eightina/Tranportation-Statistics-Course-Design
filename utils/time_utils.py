import pandas as pd
# import modin.pandas as mpd

def time_transfer(gps):
    gps['time'] = pd.to_datetime(gps['time'])
    gps['month'] = [_.month for _ in gps['time']]
    gps['day'] = [_.day for _ in gps['time']]
    gps = gps.drop(['date'], axis=1)
    return gps

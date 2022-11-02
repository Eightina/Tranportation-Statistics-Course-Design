import geopandas as gpd
import pandas as pd
# import modin.pandas as pd
import numpy as np

from shapely.geometry import Point, LineString
from shapely.ops import nearest_points


# from lat and lon generate geodataframe 
# plus transfering coords sys
def generate_3857_df(mapdf):

    if not ('lat' in mapdf.columns):
        # mapdf['lat'] = [float(_) for _ in mapdf['lat']]
        # mapdf['lon'] = [float(_) for _ in mapdf['lon']]
        # temp_lon_lat = np.array([mapdf['lon'],mapdf['lat']]).T
        print('name columns as lat and lon')
        return
    
    mapdf = gpd.GeoDataFrame(mapdf)
    # mapdf['geometry'] = [Point(_) for _ in temp_lon_lat]
    mapdf['geometry'] = mapdf.apply(lambda x: Point(x['lon'], x['lat']), axis = 1)
    # mapdf['geometry'] = mapdf.swifter.apply(lambda x: Point(x['lon'], x['lat']), axis = 1)

    # mapdf['geometry'] = mapdf.apply(lambda x: Point(x[2], x[3]), axis = 1)
    mapdf = mapdf.set_crs(4326)

    return pd.DataFrame(mapdf.to_crs(3857))


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
    linedf = gpd.GeoDataFrame(linedf)
    linedf['circ_buffer'] = linedf.buffer(50, cap_style=1)
    linedf['rect_buffer'] = linedf.buffer(50, cap_style=2)
    return pd.DataFrame(linedf)

def generate_base_length(linedf):
    temp = [_.length for _ in linedf['geometry']]
    temp.pop()
    temp = [0] + temp
    for i in range(1, len(temp)):
        temp[i] += temp[i - 1]
    linedf['base_length'] = temp
    return linedf
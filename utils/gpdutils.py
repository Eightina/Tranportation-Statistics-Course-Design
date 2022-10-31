import geopandas as gpd
import pandas as pd
import numpy as np

from shapely.geometry import Point
from shapely.geometry import LineString

# mapdf = pd.read_excel('./data/map/map_down.xlsx')

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


import rasterio
from rasterio.plot import show
import numpy as np
from PIL import Image
import ee
import pandas as pd
import geemap
import ee
import requests
import zipfile
from datetime import datetime, timedelta
import os
import geemap
import json
import os
import requests
from geemap import geojson_to_ee, ee_to_geojson
from ipyleaflet import GeoJSON
import geopandas as gpd
import matplotlib.pyplot as plt
import math

# Distances are measured in kilometers.
# Longitudes and latitudes are measured in degrees.
# Earth is assumed to be perfectly spherical.
class SquareCoords:
    earth_radius = 6271.0
    degrees_to_radians = math.pi/180.0
    radians_to_degrees = 180.0/math.pi


    def change_in_latitude(self, kms):
        "Given a distance north, return the change in latitude."
        return (kms/self.earth_radius)*self.radians_to_degrees

    def change_in_longitude(self, latitude, kms):
        "Given a latitude and a distance west, return the change in longitude."
        # Find the radius of a circle around the earth at given latitude.
        r = self.earth_radius*math.cos(latitude*self.degrees_to_radians)
        return (kms/r)*self.radians_to_degrees

    def ten_km_square(self, latitude, longitude):
        slat, nlat = latitude+self.change_in_latitude(-3.5), latitude+self.change_in_latitude(3.5)
        wlon = longitude+self.change_in_longitude(latitude,-3.5)
        elon = longitude+self.change_in_longitude(latitude, 3.5)
        return(nlat, wlon, slat, elon)


    def get_area(self, lat, lon):
        '''second argument degrees longitude (E is positive, W negative)
            of the landslide location,
            first argument latitude (N positive, S negative),
            in decimal format(not minutes etc.)'''
        nlat, wlon, slat, elon = self.ten_km_square(lat,lon)

        region = [[wlon,nlat], [elon,nlat], [wlon,slat], [elon,slat]]
        rectangle = [wlon,slat,elon,nlat]
        return (region, rectangle)



coords = pd.read_csv('coords.csv')
coords['region'] = [SquareCoords().get_area(*coords.iloc[i, :2])[0] for i in range(len(coords))]
coords['rectangle'] = [SquareCoords().get_area(*coords.iloc[i, :2])[1] for i in range(len(coords))]



def downl(row):
    ee.Initialize()
    startDate = str((datetime.today() - timedelta(days=40)).date())
    finishDate = str(datetime.today().date())

    region = row['region']
    rectangle = row['rectangle']
    rectangle1 = ee.Geometry.Rectangle(rectangle)
    tile_coord = pd.DataFrame({"lat": [rectangle[0]], "lon": [rectangle[1]]})
    tile_coord.to_csv("downloaded/tele_coords.csv")

    dataset = ee.ImageCollection("COPERNICUS/S2").filterBounds(rectangle1).filterDate(startDate, finishDate).sort('system:time_start', True);

    selectors = ["B2","B3", "B4", "B5","B8","B12","QA60"]

    def mean_cloud(image):
        return(image.select("QA60").reduceRegion(
            reducer= ee.Reducer.mean(),
            geometry= rectangle1,
            scale= 10
        ).get('QA60'))

    def un_ndvi(image):
        ndwi = image.normalizedDifference(['B3', 'B5']);
        weighted = ndwi.clip(rectangle1).reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=rectangle1,
            scale=10).get('nd').getInfo();
        return weighted
    

    
    dataset = dataset.select(selectors)
    data = dataset.toList(dataset.size())
    ndvi = []
    cloud_idxs = []
    urls = []
    try:
        for i in range(100):
            image = ee.Image(data.get(i))
            ndvi.append(un_ndvi(image))
            cloud_idxs.append(mean_cloud(image).getInfo())
            image = image.select(["B2","B3","B4", "B5","B8","B12"]);
            urls.append(image.getDownloadURL({
              'region': str(rectangle),
              'scale': 10
            }))
    
            
    except:
        print('Конец парсинга ссылок')
    cloud_np = np.array(cloud_idxs)
    print('Облачность = ' + str(cloud_np.min()))
    print('url - ' + urls[cloud_np.argmin()])
    print(len(ndvi), len(urls), len(cloud_idxs))
    return urls[cloud_np.argmin()], ndvi[cloud_np.argmin()]


# In[27]:



ee.Initialize()
ndvi_list = []

for index, row in coords.iterrows():
    region = row['region']
    rectangle = row['rectangle']
    url, ndvi = downl(row)
    ndvi_list.append(ndvi)
    r = requests.get(url, allow_redirects=True)
    zipfile_name = 'imgs' + str(index) + '.zip'
    open('downloaded/' + zipfile_name, 'wb').write(r.content)
    with zipfile.ZipFile('downloaded/' + zipfile_name, 'r') as zip_ref:
        zip_ref.extractall('downloaded/imgs' + str(index) + '/')


# -*- coding: utf-8 -*-
"""
Created on Wed Oct 21 11:20:24 2020

@author: HP
"""

import pandas as pd
import geopandas as gpd
import  matplotlib.pyplot  as plt
import numpy as np
import matplotlib as mpl
from adjustText import adjust_text
import rasterio
from rasterio.mask import mask
from rasterio.plot import show
from rasterio.plot import show_hist
import matplotlib.colors as colors
import rasterio.fill
import scipy.interpolate as interpolate

ind =gpd.read_file(r'C:/Users/HP/Desktop/data/IND_adm/BOUNDARY/DISTRICT_4nov19.shp')
ind=ind.dissolve(by="STATE")
ind.reset_index(inplace=True)
ind=ind[ind['STATE']=='BIHAR']
ind['geometry']=ind['geometry'].buffer(0.0001)
ind.to_crs(epsg=4326, inplace=True)
ind_geom = ind['geometry']

#Jan-2020
img_jan=rasterio.open('C:/Users/HP/Desktop/Satellite-Data-Analysis/Raster_files/Jan-2020.tif',mode='r')
out_img_jan, out_transform_jan = mask(img_jan, shapes=ind_geom, crop=True)
out_img_jan[out_img_jan==0]='nan'

##feb-2020
img_feb=rasterio.open('C:/Users/HP/Desktop/Satellite-Data-Analysis/feb-2020.tif',mode='r')
out_img_feb, out_transform_feb = mask(img_feb, shapes=ind_geom, crop=True)
out_img_feb[out_img_feb==0]='nan'
##Mar-2020
img_mar=rasterio.open('C:/Users/HP/Desktop/Satellite-Data-Analysis/Mar-2020.tif',mode='r')
out_img_mar, out_transform_mar = mask(img_mar, shapes=ind_geom, crop=True)
out_img_mar[out_img_mar==0]='nan'
##Apr-2020
img_apr=rasterio.open('C:/Users/HP/Desktop/Satellite-Data-Analysis/Apr-2020.tif',mode='r')
out_img_apr, out_transform_apr = mask(img_apr, shapes=ind_geom, crop=True)
out_img_apr[out_img_apr==0]='nan'
##May-2020
img_may=rasterio.open('C:/Users/HP/Desktop/Satellite-Data-Analysis/May-2020.tif',mode='r')
out_img_may, out_transform_may = mask(img_may, shapes=ind_geom, crop=True)
out_img_may[out_img_may==0]='nan'
##June-2020
img_June=rasterio.open('C:/Users/HP/Desktop/Satellite-Data-Analysis/June-2020.tif',mode='r')
out_img_June, out_transform_June = mask(img_June, shapes=ind_geom, crop=True)
out_img_June[out_img_June==0]='nan'
##July-2020
img_July=rasterio.open('C:/Users/HP/Desktop/Satellite-Data-Analysis/july-2020.tif',mode='r')
out_img_July, out_transform_July = mask(img_July, shapes=ind_geom, crop=True)
out_img_July[out_img_July==0]='nan'

#Save tiff for June & July
##June-2020
out_img_June_meta=img_June.meta.copy()
out_img_June_meta.update({"driver": "GTiff",
                 "height": out_img_June.shape[1],
                 "width": out_img_June.shape[2],
                 "transform": out_transform_June})

with rasterio.open("C:/Users/HP/Desktop/Satellite-Data-Analysis/Python_tif/June1.tif", "w", **out_img_June_meta) as dest:
    dest.write(out_img_June)
    
##July-2020
out_img_July_meta=img_July.meta.copy()
out_img_July_meta.update({"driver": "GTiff",
                 "height": out_img_July.shape[1],
                 "width": out_img_July.shape[2],
                 "transform": out_transform_July})

with rasterio.open("C:/Users/HP/Desktop/Satellite-Data-Analysis/Python_tif/July.tif", "w", **out_img_July_meta) as dest:
    dest.write(out_img_July)

##plot these-2020
levels = [0.135, 0.208, 0.401, 0.562, 0.714, 0.887, 1.069, 1.27, 2.7]
clrs = ['blue','cornflowerblue', 'olivedrab', 'yellowgreen', 'yellow', 'gold', 'orange', 'darkorange', 'red']
cmap, norm = colors.from_levels_and_colors(levels, clrs,extend='max')
plt.subplot(2,3,1)
ax1=plt.gca()
plt.subplots_adjust(wspace=0.1,hspace=0.1)
ax1.xaxis.set_visible(False)
show(out_img_jan,transform=out_transform_jan,title='Jan-2020', cmap=cmap,ax=ax1)
ind.plot(facecolor='none',edgecolor='k',ax=ax1)
plt.subplot(2,3,2)
ax1=plt.gca()
ax1.xaxis.set_visible(False)
ax1.yaxis.set_visible(False)
show(out_img_feb,transform=out_transform_feb,title='Feb-2020', cmap=cmap,ax=ax1)
ind.plot(facecolor='none',edgecolor='k',ax=ax1)
plt.subplot(2,3,3)
ax1=plt.gca()
ax1.xaxis.set_visible(False)
ax1.yaxis.set_visible(False)
show(out_img_mar,transform=out_transform_mar,title='Mar-2020', cmap=cmap,ax=ax1)
ind.plot(facecolor='none',edgecolor='k',ax=ax1)
plt.subplot(2,3,4)
ax1=plt.gca()
show(out_img_apr,transform=out_transform_apr,title='Apr-2020', cmap=cmap,ax=ax1)
ind.plot(facecolor='none',edgecolor='k',ax=ax1)
plt.subplot(2,3,5)
ax1=plt.gca()
ax1.yaxis.set_visible(False)
show(out_img_may,transform=out_transform_may,title='May-2020', cmap=cmap,ax=ax1)
ind.plot(facecolor='none',edgecolor='k',ax=ax1)


plt.subplot(2,3,6)
ax1=plt.gca()
ax1.yaxis.set_visible(False)
img_June_new=rasterio.open('C:/Users/HP/Desktop/Satellite-Data-Analysis/Python_tif/June1.tif',mode='r')
out_img_June, out_transform_June = mask(img_June, shapes=ind_geom, crop=True)
out_img_June[out_img_June==0]='nan'
show(out_img_June,transform=out_transform_June,title='June-2020', cmap=cmap)
k=rasterio.fill.fillnodata(out_img_June,mask=out_img_June,max_search_distance=50,smoothing_iterations=0)
k_meta=img_June.meta.copy()
k_meta.update({"driver": "GTiff",
                 "height": k.shape[1],
                 "width": k.shape[2],
                 "transform": out_transform_June})

with rasterio.open("C:/Users/HP/Desktop/Satellite-Data-Analysis/Python_tif/June_filled1.tif", "w", **k_meta) as dest:
    dest.write(k)

img_June_filled=rasterio.open('C:/Users/HP/Desktop/Satellite-Data-Analysis/Python_tif/June_filled1.tif',mode='r')
out_img_June_fill, out_transform_June_fill = mask(img_June_filled, shapes=ind_geom, crop=True)
out_img_June_fill[out_img_June_fill==0]='nan'
img_June_new=rasterio.open('C:/Users/HP/Desktop/Satellite-Data-Analysis/Python_tif/June1.tif',mode='r')
out_img_June, out_transform_June = mask(img_June, shapes=ind_geom, crop=True)
out_img_June[out_img_June==0]='nan'
ax1=plt.gca()
show(out_img_June_fill,transform=out_transform_June_fill,title='June-2020', cmap=cmap,ax=ax1)
show(out_img_June,transform=out_transform_June,cmap=cmap, ax=ax1)
ind.plot(facecolor='none',edgecolor='k',ax=ax1)

ax1=plt.gca()
show(k,transform=out_transform_June, ax=ax1, cmap=cmap, with_bounds=True)
show(img_June,transform=out_transform_June,title='June-2020', cmap=cmap,ax=ax1,with_bounds=True)
ind.plot(facecolor='none',edgecolor='k',ax=ax1) 



##Histograms
ax, fig =plt.subplots(figsize=(10,10))
plt.subplot(2,3,1)
ax1=plt.gca()
show_hist(out_img_jan, bins=9, lw=0.0, stacked=False, alpha=0.3,
 histtype='stepfilled', title="Jan-2020", ax=ax1)
plt.xticks(fontweight='bold')
plt.xlabel('AOD-Value',fontweight='bold')
plt.subplot(2,3,2)
ax=plt.gca()
show_hist(out_img_feb, bins=9, lw=0.0, stacked=False, alpha=0.3,
 histtype='stepfilled', title="Feb-2020", ax=ax)
plt.xticks(fontweight='bold')



##Import 2019 data
#Jan-2019
img_jan=rasterio.open('C:/Users/HP/Desktop/Satellite-Data-Analysis/Jan-2019.tif',mode='r')
out_img_jan, out_transform_jan = mask(img_jan, shapes=ind_geom, crop=True)
out_img_jan[out_img_jan==0]='nan'
##feb-2019
img_feb=rasterio.open('C:/Users/HP/Desktop/Satellite-Data-Analysis/Feb-2019.tif',mode='r')
out_img_feb, out_transform_feb = mask(img_feb, shapes=ind_geom, crop=True)
out_img_feb[out_img_feb==0]='nan'
##Mar-2019
img_mar=rasterio.open('C:/Users/HP/Desktop/Satellite-Data-Analysis/Mar-2019.tif',mode='r')
out_img_mar, out_transform_mar = mask(img_mar, shapes=ind_geom, crop=True)
out_img_mar[out_img_mar==0]='nan'
##Apr-2019
img_apr=rasterio.open('C:/Users/HP/Desktop/Satellite-Data-Analysis/Apr-2019.tif',mode='r')
out_img_apr, out_transform_apr = mask(img_apr, shapes=ind_geom, crop=True)
out_img_apr[out_img_apr==0]='nan'
##May-2019
img_may=rasterio.open('C:/Users/HP/Desktop/Satellite-Data-Analysis/May-20191.tif',mode='r')
out_img_may, out_transform_may = mask(img_may, shapes=ind_geom, crop=True)
out_img_may[out_img_may==0]='nan'
##June-2019
img_June=rasterio.open('C:/Users/HP/Desktop/Satellite-Data-Analysis/June-2019.tif',mode='r')
out_img_June, out_transform_June = mask(img_June, shapes=ind_geom, crop=True)
out_img_June[out_img_June==0]='nan'
##July-2019
img_July=rasterio.open('C:/Users/HP/Desktop/Satellite-Data-Analysis/july-2019.tif',mode='r')
out_img_July, out_transform_July = mask(img_July, shapes=ind_geom, crop=True)
out_img_July[out_img_July==0]='nan'
##August-2019
img_aug = rasterio.open('C:/Users/HP/Desktop/Satellite-Data-Analysis/Aug-2019.tif',mode='r')
out_img_aug,out_transform_aug = mask(img_aug, shapes=ind_geom, crop=True)
out_img_aug[out_img_aug==0]='nan'
##Sept-2019
img_sep = rasterio.open('C:/Users/HP/Desktop/Satellite-Data-Analysis/Sep-2019.tif',mode='r')
out_img_sep,out_transform_sep = mask(img_sep, shapes=ind_geom, crop=True)
out_img_sep[out_img_sep==0]='nan'
##Oct-2019
img_oct = rasterio.open('C:/Users/HP/Desktop/Satellite-Data-Analysis/Oct-2019.tif',mode='r')
out_img_oct,out_transform_oct = mask(img_oct, shapes=ind_geom, crop=True)
out_img_oct[out_img_oct==0]='nan'
##Nov-2019
img_nov = rasterio.open('C:/Users/HP/Desktop/Satellite-Data-Analysis/Nov-2019.tif',mode='r')
out_img_nov,out_transform_nov = mask(img_nov, shapes=ind_geom, crop=True)
out_img_nov[out_img_nov==0]='nan'
##Dec-2019
img_dec = rasterio.open('C:/Users/HP/Desktop/Satellite-Data-Analysis/Dec-2019.tif',mode='r')
out_img_dec,out_transform_dec = mask(img_dec, shapes=ind_geom, crop=True)
out_img_dec[out_img_dec==0]='nan'



ax = plt.gca()
plt.imshow(temp, cmap=cmap) 
plt.colorbar(extend='both', orientation='horizontal').set_label( label='AOD',weight='bold', size=15)
ax.xaxis.set_visible(False)


##scipy interpolation for missing values
july_value = out_img_July[0].ravel()
cols_vals = np.arange(0,555)
ind_vals = np.arange(0,361)
xx, yy =np.meshgrid(ind_vals,cols_vals)
yy_points = yy.ravel(order='F')
xx_points = xx.ravel(order='F')
values = np.concatenate((july_value,xx_points,yy_points)).reshape((200355,3), order='F')
values=values[~np.isnan(values).any(axis=1)]
points = np.array([values[:,1],values[:,2]]).transpose()
values = values[:,0]
grid_June = interpolate.griddata(points, values , (xx,yy), method='nearest').transpose()
fig,ax1 = plt.subplots()
show(grid_June, ax=ax1, cmap='hsv')
show(out_img_June[0], ax=ax1,cmap='hsv')

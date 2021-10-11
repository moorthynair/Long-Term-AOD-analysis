# -*- coding: utf-8 -*-
"""
Created on Wed Dec 16 16:35:36 2020

@author: HP
"""
##Import all the libraries
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
from rasterio.plot import plotting_extent
import matplotlib.colors as colors
import rasterio.fill
import scipy.interpolate as interpolate
import os
import glob
from mpl_toolkits.axisartist.axislines import Subplot  
from matplotlib.figure import Figure
import matplotlib as mpl 
from PIL import Image
from scipy.signal import savgol_filter
from sklearn.metrics import r2_score, mean_squared_error
import math
import itertools
from matplotlib import cm
from rasterstats import zonal_stats
from mpl_toolkits.axes_grid1 import make_axes_locatable
from rasterio.merge import merge
from rasterio.plot import show
from rasterio.warp import calculate_default_transform, reproject, Resampling

##Generate filenames to be renamed
real_names = np.arange(0,48,1)
actual=[]
for i in real_names:
    name = str(i)+'.tif'
    actual.append(name)
month=['Jan','Feb','Mar','Apr','May','June','July','Aug','Sept','Oct','Nov','Dec']
rename=[]
month_iter=month*19 
numb = np.arange(2001,2020,1)

numb=np.repeat(numb,12)
for index, i in enumerate(month_iter):
    k = numb[index]
    string = str(i)+"-"+str(k)
    rename.append(string)

filename = np.concatenate((actual,rename),axis=0).reshape((48,2),order='F')
filename =pd.DataFrame(filename, columns=["actual_name","rename"])


##Rename the files
for files in os.listdir('G:/My on going proj/Satellite-Data-Analysis/monthly_aod-2001-2004/monthly_aod'):
      for index,row in filename.iterrows():
          if files==row['actual_name']:
              j=filename.iloc[index,1]
              os.rename(files,j+'.tif')

##Data availability
data_availability = pd.DataFrame()

##Read the dataset using rasterio module
year_seq = np.arange(2001,2020,1)
for years in year_seq:
    j=int(years)
    for i in glob.glob('*.tif'):
        file =i
        i=i[:-4]
        year_rast=i[-4:]
        if int(year_rast)==j:
            dataset =rasterio.open('G:/My on going proj/Satellite-Data-Analysis/Combined_raw_aod/'+file)            
            dataset_arr = dataset.read(1)
            dataset_transform = dataset.transform
            dataset_ravel =dataset_arr.ravel()
            cols_vals = np.arange(0,len(dataset_arr[0]))
            ind_vals = np.arange(0,len(dataset_arr))
            xx, yy =np.meshgrid(ind_vals,cols_vals)
            yy_points = yy.ravel(order='F')
            xx_points = xx.ravel(order='F')
            values = np.concatenate((dataset_ravel,xx_points,yy_points)).reshape(((len(dataset_arr[0])*len(dataset_arr)),3), order='F')
            values=values[~np.isnan(values).any(axis=1)]            
            points = np.array([values[:,1],values[:,2]]).transpose()
            values = values[:,0]
            dataset_interpolated = interpolate.griddata(points, values , (xx,yy), method='nearest').transpose()                   
            dataset_interpolated = dataset_interpolated. astype('float32')
            dataset_meta=dataset.meta.copy()            
            dataset_meta.update({"driver": "GTiff",
                             "height": dataset_arr.shape[0],
                             "width": dataset_arr.shape[1],
                             "transform": dataset.transform})
            with rasterio.open("G:/My on going proj/Satellite-Data-Analysis/Raster_interpolated/"+str(file), "w", **dataset_meta) as dest:
                dest.write(dataset_interpolated, indexes=1)
            print('Processing is completed :'+ str(file)) 

##read the shapefile
ind =gpd.read_file(r'F:/neeri/MODIS/BOUNDARY/DISTRICT_4nov19.shp')
ind=ind.dissolve(by="STATE")
ind.reset_index(inplace=True)
ind=ind[ind['STATE']=='BIHAR']
ind['geometry']=ind['geometry'].buffer(0.0001)
ind.to_crs(epsg=4326, inplace=True)
ind_geom = ind['geometry']

##Generate pandas dataframe to input stats to estimate data availability
for i in glob.glob('*.tif'): 
    i = i[:-4] 
    rename.append(i)
data_availability = pd.DataFrame(columns={'Data_available_percent'}, index=rename)

##calculate the data availability in each of the tiles
for i in glob.glob('*.tif'):
    filename =i[ :-4]
    print(filename)
    file=i
    dataset =rasterio.open('G:/My on going proj/Satellite-Data-Analysis/Combined_raw_aod/'+file, mode='r')
    out_img, out_transform = mask(dataset, shapes=ind_geom, crop=True)
    out_img=out_img[0].ravel()
    ##Total pixel within the tile
    Values_total =len(out_img)
    ##Total NA's pixel within Bihar shapefile
    values_Na_bihar=np.isnan(out_img)[np.isnan(out_img)==True].size   
    out_img[out_img==0]='nan'
    ##Total NA's pixel within the tile (This also include NA's within Bihar shapefile)
    values_NA_total_tile = np.isnan(out_img)[np.isnan(out_img)==True].size   
    ##Total Available pixels within Bihar shapefile (Excluding NAs)
    values_available = Values_total-values_NA_total_tile
    ##Total pixels within Bihar including NAs
    values_total_bihar = Values_total - values_NA_total_tile + values_Na_bihar
    ##Data availability 
    value_percent_available = (values_available*100)/(values_total_bihar)
    data_availability.loc[filename,'Data_available_percent']=value_percent_available
data_availability.to_excel('G:/My on going proj/Satellite-Data-Analysis/data_availability_sheet.xlsx')


##Apply savgol filter for smoothening with varying window size
r_val =pd.DataFrame(columns={'fig','R-squared-1','R-squared-2','window'})
r_val['fig']=my
r_val['R-squared-1']=0
r_val['R-squared-2']=0
r_val['window']=0
r_val=r_val[['fig','R-squared-1','R-squared-2','window']]
for index,i in r_val.iterrows():  
    n=5
    j =i['fig']    
    img = rasterio.open('G:/My on going proj/Satellite-Data-Analysis/Raster_interpolated/'+str(j)+'.tif')
    img_meta = img.meta.copy()
    img_transform = img.transform
    img= img.read(1)
    img_rav_ax1= img.ravel()
    img_rav_ax2= img.ravel(order='F')
    img_savgol_ax1 = savgol_filter(img_rav_ax1, n,0, mode='nearest')     
    k1=r2_score(img_rav_ax1,img_savgol_ax1)
    img_savgol = img_savgol_ax1.reshape(img.shape[0], img.shape[1])
    img_savgol_ax1_rav = img_savgol.ravel(order='F')
    img_savgol_ax2 = savgol_filter(img_savgol_ax1_rav, n,0, mode='nearest')  
    k2=r2_score(img_rav_ax2,img_savgol_ax2)
    while k1>=0.981 and k2>=0.981:
        n=n+2 
        img_savgol_ax1 = savgol_filter(img_rav_ax1, n,0, mode='nearest')     
        k1=r2_score(img_rav_ax1,img_savgol_ax1)
        img_savgol = img_savgol_ax1.reshape(img.shape[0], img.shape[1])
        img_savgol_ax1_rav = img_savgol.ravel(order='F')
        img_savgol_ax2 = savgol_filter(img_savgol_ax1_rav, n,0, mode='nearest')  
        k2=r2_score(img_rav_ax2,img_savgol_ax2)    
    r_val.iloc[int(index),1]=k1
    r_val.iloc[int(index),2]=k2
    r_val.iloc[int(index),3]=n      
    print('R2- squred value for '+str(j)+':'+ str(k1)+ ','+ str(k2)+' with window: '+ str(n))
    img_smoothened = img_savgol_ax2.reshape((img.shape[0],img.shape[1]), order='F')  
    img_meta.update({"driver": "GTiff",
                        "height": img.shape[0],
                         "width": img.shape[1],
                         "transform": img_transform})
    with rasterio.open("G:/My on going proj/Satellite-Data-Analysis/Processed_raster_savgol_filter/"+str(j)+'.tif', "w", **img_meta) as dest:
        dest.write(img_smoothened, indexes=1)
    print(str(j)+' is saved')
r_val.to_excel('G:/My on going proj/Satellite-Data-Analysis/Processed_raster/Raster_facets_savgol.xlsx')

##Apply savgol filter for smoothening with constant window_size
r_val =pd.DataFrame(columns={'fig','R-squared-1','R-squared-2','window'})
r_val['fig']=my
r_val['R-squared-1']=0
r_val['R-squared-2']=0
r_val['window']=0
r_val=r_val[['fig','R-squared-1','R-squared-2','window']]
for index,i in r_val.iterrows():  
    n=11
    j =i['fig']    
    img = rasterio.open('G:/My on going proj/Satellite-Data-Analysis/Raster_interpolated/'+str(j)+'.tif')
    img_meta = img.meta.copy()
    img_transform = img.transform
    img= img.read(1)
    img_rav_ax1= img.ravel()
    img_rav_ax2= img.ravel(order='F')
    img_savgol_ax1 = savgol_filter(img_rav_ax1, n,0, mode='nearest')     
    k1=r2_score(img_rav_ax1,img_savgol_ax1)
    img_savgol = img_savgol_ax1.reshape(img.shape[0], img.shape[1])
    img_savgol_ax1_rav = img_savgol.ravel(order='F')
    img_savgol_ax2 = savgol_filter(img_savgol_ax1_rav, n,0, mode='nearest')  
    k2=r2_score(img_rav_ax2,img_savgol_ax2)       
    r_val.iloc[int(index),1]=k1
    r_val.iloc[int(index),2]=k2
    r_val.iloc[int(index),3]=n      
    print('R2- squred value for '+str(j)+':'+ str(k1)+ ','+ str(k2)+' with window: '+ str(n))
    img_smoothened = img_savgol_ax2.reshape((img.shape[0],img.shape[1]), order='F')  
    img_meta.update({"driver": "GTiff",
                        "height": img.shape[0],
                         "width": img.shape[1],
                         "transform": img_transform})
    with rasterio.open("G:/My on going proj/Satellite-Data-Analysis/Processed_raster_savgol_filter/"+str(j)+'.tif', "w", **img_meta) as dest:
        dest.write(img_smoothened, indexes=1)
    print(str(j)+' is saved')
r_val.to_excel('G:/My on going proj/Satellite-Data-Analysis/Processed_raster/Raster_facets_savgol.xlsx')


##Generate colormap based on savgol filter percentile averages
# levels = [0.425,0.472,0.508,0.541,0.573,0.606,0.642,0.685,0.748,1.280]
# clrs = ['blue','cornflowerblue', 'olivedrab', 'yellowgreen', 'yellow', 'gold', 'orange', 'darkorange', 'red','darkred']
# cmap, norm = colors.from_levels_and_colors(levels, clrs,extend='max')
clrs = plt.cm.get_cmap('RdYlBu_r',10)
numb=1
y=2001
while y<=2019:   
    numb=1
    fig =plt.figure(figsize=(15,15)) 
    for i in my:    
        file=i   
        month=i[-9:-5]
        year=i[-4:]         
        if int(year)==y:
            dataset =rasterio.open('G:/My on going proj/Satellite-Data-Analysis/Processed_raster_savgol_filter/'+str(i)+'.tif', mode='r')
            out_img, out_transform = mask(dataset, shapes=ind_geom, crop=True)
            out_img=out_img[0]
            out_img[out_img==0]='nan'                               
            fig.set_figheight(12.5) 
            fig.set_figwidth(12.5) 
            ax1 =fig.add_subplot(4,3,numb)         
            plt.subplots_adjust(wspace=0.1,hspace=0.25)
            ax1.xaxis.set_visible(False)
            ax1.yaxis.set_visible(False)
            fig.suptitle(year, fontsize=30,fontweight="bold")
            ax1.set_title(month, fontsize= 25,fontweight="bold")             
            show(out_img,transform=out_transform,cmap=clrs,ax=ax1, vmin=0.15, vmax=1.4)
            ind_geom.plot(facecolor='none',edgecolor='k',ax=ax1)                          
            numb=numb+1               
            plt.savefig('G:/My on going proj/Satellite-Data-Analysis/Processed_raster/Raster_facets_savgol_updated/yearly_subplots/'+str(y)+'.png')
    y=y+1

##Generate raster images in facets for individual years
levels = [0.414,0.464,0.502,0.537,0.569,0.603,0.641,0.686,0.756,1.613]
clrs = ['blue','cornflowerblue', 'olivedrab', 'yellowgreen', 'yellow', 'gold', 'orange', 'darkorange', 'red','darkred']
cmap, norm = colors.from_levels_and_colors(levels, clrs,extend='max')
numb=1
y=2001
while y<=2019:   
    numb=1
    fig =plt.figure(figsize=(15,15)) 
    for i in my:    
        file=i   
        month=i[-9:-5]
        year=i[-4:]         
        if int(year)==y:
            dataset =rasterio.open('G:/My on going proj/Satellite-Data-Analysis/Raster_interpolated/'+str(i)+'.tif', mode='r')
            out_img, out_transform = mask(dataset, shapes=ind_geom, crop=True)
            out_img=out_img[0]
            out_img[out_img==0]='nan'                               
            fig.set_figheight(12.5) 
            fig.set_figwidth(12.5) 
            ax1 =fig.add_subplot(4,3,numb)         
            plt.subplots_adjust(wspace=0.1,hspace=0.25)
            ax1.xaxis.set_visible(False)
            ax1.yaxis.set_visible(False)
            fig.suptitle(year, fontsize=30,fontweight="bold")
            ax1.set_title(month, fontsize= 25,fontweight="bold")        
            show(out_img,transform=out_transform,cmap=cmap,ax=ax1)
            ind_geom.plot(facecolor='none',edgecolor='k',ax=ax1)                          
            numb=numb+1               
            plt.savefig('G:/My on going proj/Satellite-Data-Analysis/Processed_raster/'+str(y)+'.png')
    y=y+1
   
##Generate Poster
# levels = [0.425,0.472,0.508,0.541,0.573,0.606,0.642,0.685,0.748,1.280]
# clrs = ['blue','cornflowerblue', 'olivedrab', 'yellowgreen', 'yellow', 'gold', 'orange', 'darkorange', 'red','darkred']
# cmap, norm = colors.from_levels_and_colors(levels, clrs,extend='max')
clrs = plt.cm.get_cmap('RdYlBu',10)
numb=1
fig =plt.figure(figsize=(30,30)) 
for i in my:    
    file=i   
    year=i[-4:]     
    dataset =rasterio.open('G:/My on going proj/Satellite-Data-Analysis/Processed_raster_savgol_filter/'+str(i)+'.tif', mode='r')
    out_img, out_transform = mask(dataset, shapes=ind_geom, crop=True)
    out_img=out_img[0]
    out_img[out_img==0]='nan'                               
    fig.set_figheight(35) 
    fig.set_figwidth(35) 
    ax1 =fig.add_subplot(20,12,numb)         
    plt.subplots_adjust(wspace=0.1,hspace=0.25)
    ax1.xaxis.set_visible(False)
    ax1.yaxis.set_visible(False)
    ax1.set_title(file, fontsize= 12,fontweight="bold")
    show(out_img,transform=out_transform, cmap=clrs,ax=ax1, vmin=0.15, vmax=1.4)
    ind_geom.plot(facecolor='none',edgecolor='k',ax=ax1)  
    print('Processing is completed for:'+str(file))
    numb=numb+1

##create raster image with legends/colorbar
plt.figure(figsize=(15,15))
# cmap=mpl.colors.ListedColormap(['blue','cornflowerblue', 'olivedrab', 'yellowgreen', 'yellow', 'gold', 'orange', 'darkorange', 'red','darkred'])
sm = plt.cm.ScalarMappable(cmap=clrs)
cbar = plt.colorbar(sm, ticks=np.linspace(0.0, 1, 10, endpoint=False)+0.05, extend='both')
# cbar.ax.locator_params(nbins=5)
cbar.ax.set_yticklabels([r'$\leq$0.15', '0.29','0.43', '0.57', '0.71','0.85', '0.99','1.13','1.27',r'$>$1.4'], fontsize=25, weight='bold')
# cbar.ax.set_yticklabels(['0.407', '0.458', '0.513', '0.567', '0.601', '0.641', '0.690', '0.766', r'$\geq$2.16'], fontsize=20, weight='bold')
cbar.ax.axes.tick_params(length=5)
cbar.ax.yaxis.set_tick_params(pad=10)
cbar.ax.tick_params(width=3)
cbar.set_label( label='AOD',weight='bold', size=35)
plt.show()

##club the generated raster images and legend
for i in glob.glob('*.png'):    
    filename=i[:-4]    
    post =Image.open('G:/My on going proj/Satellite-Data-Analysis/Processed_raster/Raster_facets_savgol_updated/monthly_raster/monthly_new.png')
    #post =Image.open('G:/My on going proj/Satellite-Data-Analysis/Processed_raster/Raster_facets_savgol_updated/yearly_subplots/'+str(filename)+'.png')
    post=post.crop((0,0,670,720))
    legend=Image.open('G:/My on going proj/Satellite-Data-Analysis/Processed_raster/Raster_facets_savgol_updated/subplot_legend_crop.png')
    final_poster= Image.new('RGB',(post.width+legend.width, post.height),(255,255,255))
    final_poster.paste(post,(0,0))
    final_poster.paste(legend,(post.width,80))
    final_poster.show()
    final_poster.save('G:/My on going proj/Satellite-Data-Analysis/Processed_raster/Raster_facets_savgol_updated/yearly_subplots/'+str(filename)+'.png')
    print(str(filename)+' is saved in the mentioned folder')

##Generate Individual monthly average rasterfiles for animation
clrs=plt.cm.get_cmap('RdYlBu_r',10)
for i in glob.glob('*.tif'):
    file=i[:-4]    
    dataset =rasterio.open('G:/My on going proj/Satellite-Data-Analysis/Processed_raster_savgol_filter/'+str(i), mode='r')
    out_img, out_transform = mask(dataset, shapes=ind_geom, crop=True)
    out_img=out_img[0]
    out_img[out_img==0]='nan'                               
    fig=plt.figure(figsize=(10,10))
    fig.set_figheight(12.5) 
    fig.set_figwidth(12.5) 
    ax1=plt.gca()
    ax1.xaxis.set_visible(False)
    ax1.yaxis.set_visible(False)
    ax1.set_title(file, fontsize= 30,fontweight="bold")
    ax1.title.set_position([0.5,1.02])
    show(out_img,transform=out_transform, cmap=clrs,ax=ax1, vmin=0.15, vmax=1.4)
    ind_geom.plot(facecolor='none',edgecolor='k',ax=ax1) 
    plt.savefig('G:/My on going proj/Satellite-Data-Analysis/Processed_raster/Raster_facets_savgol_updated/Individual_monthly_raster/'+str(file)+'.png')
    plt.cla()
    plt.clf()
    print(str(file)+' : is processed')

##Generate month wise raster facet of all the year
month=['January','February','March','April','May','June','July','August','September','October','November','December']
month=np.repeat(month,19)
numb= np.arange(2001,2020,1)
numb = list(itertools.repeat(numb,12))
numb =np.array(numb).ravel() 
fig_name=['Jan','Feb','Mar','Apr','May','June','July','Aug','Sept','Oct','Nov','Dec']
figured=fig_name
fig_name =np.repeat(fig_name,19)
df = np.concatenate((month,numb,fig_name),axis=0).reshape((228,3), order='F')
df =pd.DataFrame(df, columns={'month','year','fig_name'})
df = df.rename(columns={'year':'month', 'month':'year'})
for j in figured:
    fig = plt.figure(figsize=(15,15))
    numb=1
    while numb<=19:
        for index, i in df.iterrows():
            main_title = i['month']
            year = i['year']
            figure_name= i['fig_name']         
            if figure_name==j:
                dataset =rasterio.open('G:/My on going proj/Satellite-Data-Analysis/Processed_raster_savgol_filter/'+str(figure_name)+'-'+str(year)+'.tif', mode='r')
                out_img, out_transform = mask(dataset, shapes=ind_geom, crop=True)
                out_img=out_img[0]
                out_img[out_img==0]='nan'                               
                fig.set_figheight(12.5) 
                fig.set_figwidth(12.5) 
                ax1 =fig.add_subplot(5,4,numb)         
                plt.subplots_adjust(wspace=0.1,hspace=0.25)
                ax1.xaxis.set_visible(False)
                ax1.yaxis.set_visible(False)
                fig.suptitle(main_title, fontsize=30,fontweight="bold")
                ax1.set_title(year, fontsize= 25,fontweight="bold")        
                show(out_img,transform=out_transform,cmap=clrs,ax=ax1, vmin=0.15, vmax=1.4)
                ind_geom.plot(facecolor='none',edgecolor='k',ax=ax1)                          
                numb=numb+1
                plt.savefig('G:/My on going proj/Satellite-Data-Analysis/Processed_raster/Raster_facets_savgol-updated/monthwise_subplot/'+str(j)+'.png')
    print('processing is completed for the month: '+ str(j))
  
## Club Individual monthly averages with legend
for i in glob.glob('*.png'):
    # monthly_avg = Image.open('G:/My on going proj/Satellite-Data-Analysis/Processed_raster/Raster_facets_savgol_updated/monthly_raster/'+str(i))    
    monthly_avg = Image.open('G:/My on going proj/Satellite-Data-Analysis/Processed_raster/Raster_facets_savgol_updated/combined.png')
    legend = Image.open('G:/My on going proj/Satellite-Data-Analysis/Processed_raster/Raster_facets_savgol_updated/subplot_legend_crop.png')
    monthly_avg= monthly_avg.crop([0,0,1928,1840])
    # legend= legend.crop([5,0,160,598])
    final_img = Image.new('RGB',(monthly_avg.width+legend.width, monthly_avg.height),(255,255,255))
    final_img.paste(monthly_avg,(0,0))
    final_img.paste(legend,(monthly_avg.width,550)) 
    final_img.show()     
    final_img.save('combined.png')
    print(str(i)+': is processed')

#Generate dataframe as per month and year format
month=['Jan','Feb','Mar','Apr','May','June','July','Aug','Sept','Oct','Nov','Dec']
month=month*19
year = np.arange(2001,2020)
year = np.repeat(year,12)
my =[]
for index, i in enumerate(month):
    y= year[index]
    j =i+'-'+str(y)
    my.append(j)
    
##Generate an animation
image_frame=[]
for i in my:
    for img in glob.glob('*.png'):
        j=img[:-4]        
        if j==i:
            k=Image.open('G:/My on going proj/Satellite-Data-Analysis/Processed_raster/Raster_facets_savgol_updated/Individual_monthly_raster/'+str(img))
            image_frame.append(k)
            print(str(img)+' file has be appended')

image_frame[0].save('G:/My on going proj/Satellite-Data-Analysis/Processed_raster/AOD_time_lapse_new.gif',
                    format='GIF', append_images = image_frame[1:], save_all=True, duration=500, loop=0)
            
##Generate yearly averages
i=2001
while i<=2019:
    yearly_aod=pd.DataFrame()
    for p in glob.glob('*.tif'):
        y = p[-8:-4]        
        if int(y)==i:        
            img=rasterio.open('G:/My on going proj/Satellite-Data-Analysis/Processed_raster_savgol_filter/'+str(p))
            a,b =img.shape
            img_transform = img.transform
            img_meta=img.meta.copy()
            img=img.read(1).ravel()
            yearly_aod[p]=img            
    yearly_aod = yearly_aod.to_numpy()
    yearly_aod_mean = np.nanmean(yearly_aod, axis=1).reshape(a, b)
    img_meta.update({"driver": "GTiff",
                         "height": a,
                         "width":b,
                         "transform": img_transform})
    with rasterio.open("G:/My on going proj/Satellite-Data-Analysis/Processed_raster/Raster_yearly_savgol/"+str(i)+".tif", "w", **img_meta) as dest:
        dest.write(yearly_aod_mean, indexes=1)
    print('Processing is completed :'+ str(i))
    i=i+1 

##Generate yearly raster images       
numb=1
while numb<=19:
    fig=plt.figure(figsize=(15,15))    
    for i in os.listdir('G:/My on going proj/Satellite-Data-Analysis/Processed_raster/Raster_yearly_savgol/'):
        img_name =i[0:4]
        img=rasterio.open('G:/My on going proj/Satellite-Data-Analysis/Processed_raster/Raster_yearly_savgol/'+str(i))
        out_img, out_transform = mask(img, shapes=ind_geom, crop=True)                
        out_img=out_img[0]
        out_img[out_img==0]='nan'    
        left= out_transform[2]
        top= out_transform[5]
        a =out_img.shape[0]
        b=out_img.shape[1]
        extent= (left,left+b*0.009,top-a*0.009,top)                              
        fig.set_figheight(15) 
        fig.set_figwidth(15)         
        ax1=fig.add_subplot(5,4,numb)
        plt.subplots_adjust(wspace=0.05,hspace=0.4)
        extent= (left,left+b*0.009,top-a*0.009,top)
        fig1=ax1.imshow(out_img, cmap=clrs, extent=extent, vmin=0.3, vmax=0.9)
        # ax1.xaxis.set_visible(False)
        # ax1.yaxis.set_visible(False)
        plt.xticks(weight='bold')
        plt.yticks(weight='bold')
        ax1.set_title(img_name, fontsize= 20,fontweight="bold")        
        ax1.title.set_position([0.5,1.02])
        # show(out_img,transform=out_transform, cmap=clrs,ax=ax1, vmin=0.3, vmax=0.9)
        # bihar_geom.plot(facecolor='none',edgecolor='k',ax=ax1, linewidth=0.5) 
        ind_geom.plot(facecolor='none',edgecolor='k',ax=ax1) 
        print(str(i)+' : is processed')
        numb=numb+1
cbar_ax = fig.add_axes([0.92, 0.15, 0.03, 0.7])
cbar = fig.colorbar(fig1, extend='both',cax=cbar_ax)
cbar.ax.axes.tick_params(length=5,width=3)
cbar.ax.yaxis.set_tick_params(pad=10)
# cbar.ax.tick_params(width=3)
cbar.set_label( label='AOD',weight='bold', size=15, labelpad=12)
cbar.ax.tick_params(labelsize=20)
cbar.set_ticks(np.arange(0.3, 0.9, 0.1))
cbar.ax.set_yticklabels(np.arange(0.3, 0.9, 0.1).round(1),weight='bold')
    # cbar_ax = fig.add_axes([0.85, 0.15, 0.05, 0.7])
    # cbar = fig.colorbar(fig1, extend='both',cax=cbar_ax)

    plt.savefig('G:/My on going proj/Satellite-Data-Analysis/Processed_raster/Raster_facets_savgol_updated/yearly_raster/yearly1.png')
    
##Generate cumulative monthly raster tif images
month=['Jan','Feb','Mar','Apr','May','June','July','Aug','Sept','Oct','Nov','Dec']
for i in month:
    monthly_aod =pd.DataFrame()
    for date in range(2001,2020):
        img =rasterio.open('G:/My on going proj/Satellite-Data-Analysis/Processed_raster_savgol_filter/'+str(i)+'-'+str(date)+'.tif')
        a,b =img.shape
        img_transform = img.transform
        img_meta=img.meta.copy()
        img=img.read(1).ravel()
        monthly_aod[date]=img
    monthly_aod = monthly_aod.to_numpy()
    monthly_aod_mean = np.nanmean(monthly_aod, axis=1).reshape(a, b)
    img_meta.update({"driver": "GTiff",
                         "height": a,
                         "width":b,
                         "transform": img_transform})
    with rasterio.open("G:/My on going proj/Satellite-Data-Analysis/Processed_raster/Raster_monthly_savgol/"+str(i)+".tif", "w", **img_meta) as dest:
        dest.write(monthly_aod_mean, indexes=1)
    print('Processing is completed :'+ str(i))
    

## Generate cumulative seasonal raster tif images
month=['Jan','Feb','Mar','Apr','May','June','July','Aug','Sept','Oct','Nov','Dec']
month_rep = list(itertools.repeat(month,19))
month_rep = np.array(month_rep).ravel()
year= np.arange(2001,2020,1)
year_rep = np.repeat(year,12)
comb = np.concatenate((month_rep,year_rep),axis=0).reshape((228,2),order='F')
df = pd.DataFrame(comb, columns=['month','year'])
Winter = ['Jan','Feb']
Pre_Monsoon =['Mar','Apr','May']
Monsoon =['June','July','Aug','Sept']
Post_Monsoon = ['Oct','Nov','Dec']
condition = [df['month'].isin(Winter),df['month'].isin(Pre_Monsoon),df['month'].isin(Monsoon),df['month'].isin(Post_Monsoon)]   
choice = ['Winter','Pre_Monsoon','Monsoon','Post_Monsoon']  
df['season']= np.select(condition,choice)     
season = df['season'].unique().tolist()

for i in season:
    new_list = df[(df['season']==i)]
    seasonal_aod =pd.DataFrame()
    numb=1
    for index, j in new_list.iterrows():
        month = j['month']
        year = j['year']
        img = rasterio.open('G:/My on going proj/Satellite-Data-Analysis/Processed_raster_savgol_filter/'+str(month)+'-'+str(year)+'.tif')
        a,b =img.shape
        img_transform = img.transform
        img_meta=img.meta.copy()
        img=img.read(1).ravel()
        seasonal_aod[numb]=img
        num=numb+1        
    seasonal_aod = seasonal_aod.to_numpy()
    seasonal_aod_mean = np.nanmean(seasonal_aod, axis=1).reshape(a, b)
    img_meta.update({"driver": "GTiff",
                         "height": a,
                         "width":b,
                         "transform": img_transform})
    with rasterio.open("G:/My on going proj/Satellite-Data-Analysis/Processed_raster/Raster_seasonal_savgol/"+str(i)+".tif", "w", **img_meta) as dest:
        dest.write(seasonal_aod_mean, indexes=1)
    print('Processing is completed :'+ str(i))


##Generate monthly raster 
month=['January','February','March','April','May','June','July','August','September','October','November','December']
numb=1
fig =plt.figure(figsize=(15,15))  
for mon in month:
    month_adjust =mon[ :3]    
    for i in os.listdir('G:/My on going proj/Satellite-Data-Analysis/Processed_raster/Raster_monthly_savgol/'):          
        img_name =i[:-4]
        num = i[:3]        
        if month_adjust==num:        
            img=rasterio.open('G:/My on going proj/Satellite-Data-Analysis/Processed_raster/Raster_monthly_savgol/'+str(i))
            out_img, out_transform = mask(img, shapes=ind_geom, crop=True)
            out_img=out_img[0]
            out_img[out_img==0]='nan' 
            #fig =plt.figure(figsize=(15,15))                                          
            fig.set_figheight(12.5) 
            fig.set_figwidth(12.5)           
            ax1=fig.add_subplot(4,3,numb)
            #ax1=plt.gca()
            plt.subplots_adjust(wspace=0.05,hspace=0.4)
            # ax1.xaxis.set_visible(False)
            # ax1.yaxis.set_visible(False)
            plt.xticks(weight='bold')
            plt.yticks(weight='bold')
            ax1.set_title(img_name[0:3], fontsize= 20,fontweight="bold")        
            ax1.title.set_position([0.5,1.02])
            fig1=ax1.imshow(out_img, cmap=clrs, extent=extent, vmin=0.3, vmax=0.9)
            ind_geom.plot(facecolor='none',edgecolor='k',ax=ax1) 
            # bihar_geom.plot(facecolor='none',edgecolor='k',ax=ax1, linewidth=0.5)         
            print(str(mon)+' : is processed')
            numb=numb+1
cbar_ax = fig.add_axes([0.90, 0.15, 0.03, 0.7])
cbar = fig.colorbar(fig1, extend='both',cax=cbar_ax)
cbar.ax.axes.tick_params(length=5,width=3)
cbar.ax.yaxis.set_tick_params(pad=10)
# cbar.ax.tick_params(width=3)
cbar.set_label( label='AOD',weight='bold', size=15, labelpad=12)
cbar.ax.tick_params(labelsize=20)
cbar.set_ticks(np.arange(0.3, 0.9, 0.1))
cbar.ax.set_yticklabels(np.arange(0.3, 0.9, 0.1).round(1),weight='bold')    
        # cb_ax = fig.add_axes([0.92, 0.1, 0.02, 0.8])
        # fig.colorbar(j, cax=cb_ax)
plt.savefig('G:/My on going proj/Satellite-Data-Analysis/Processed_raster/Raster_facets_savgol_updated/monthly_raster/'+str(mon)+'.png')

##Generating seasonal raster images
fig = plt.figure(figsize=(15,15))
numb=1
for i in season:
    name = i.replace('_',"-")
    img = rasterio.open('G:/My on going proj/Satellite-Data-Analysis/Processed_raster/Raster_seasonal_savgol/'+str(i)+'.tif')
    out_img, out_transform = mask(img, shapes=ind_geom, crop=True)
    out_img=out_img[0]
    out_img[out_img==0]='nan' 
    #fig =plt.figure(figsize=(15,15))                                          
    fig.set_figheight(12.5) 
    fig.set_figwidth(12.5)          
    ax1=fig.add_subplot(2,2,numb)
    #ax1=plt.gca()
    plt.subplots_adjust(wspace=0.25,hspace=0.00)
    # ax1.xaxis.set_visible(False)
    # ax1.yaxis.set_visible(False)
    ax1.xaxis.set_tick_params(labelsize=15)
    ax1.yaxis.set_tick_params(labelsize=15)    
    plt.xticks(weight='bold')
    plt.yticks(weight='bold')
    ax1.set_title(name, fontsize= 20,fontweight="bold")        
    ax1.title.set_position([0.5,1.02])
    fig1=ax1.imshow(out_img, cmap=clrs, extent=extent, vmin=0.3, vmax=0.9)
    ind_geom.plot(facecolor='none',edgecolor='k',ax=ax1) 
    # bihar_geom.plot(facecolor='none',edgecolor='k',ax=ax1, linewidth=0.5)         
    print(str(i)+' : is processed')
    numb=numb+1            
cbar_ax = fig.add_axes([0.95, 0.15, 0.03, 0.7])
cbar = fig.colorbar(fig1, extend='both',cax=cbar_ax)
cbar.ax.axes.tick_params(length=5,width=3)
cbar.ax.yaxis.set_tick_params(pad=10)
# cbar.ax.tick_params(width=3)
cbar.set_label( label='AOD',weight='bold', size=15, labelpad=12)
cbar.ax.tick_params(labelsize=20)
cbar.set_ticks(np.arange(0.3, 0.9, 0.1))
cbar.ax.set_yticklabels(np.arange(0.3, 0.9, 0.1).round(1),weight='bold')       

##Percentile value for all the interpolated raster images 
percentile =np.arange(10,110,10)
col_name=[]
for files in glob.glob('*.tif'):
    files=files[ :-4]
    col_name.append(files)
quantile_data = pd.DataFrame(columns=percentile, index=col_name)        


for files in glob.glob('*.tif'):
    filename=files[ :-4]
    dataset =rasterio.open('G:/My on going proj/Satellite-Data-Analysis/Processed_raster_savgol_filter/'+str(files), mode='r')
    out_img, out_transform = mask(dataset, shapes=ind_geom, crop=True)
    out_img=out_img[0]
    out_img[out_img==0]='nan'
    out_img = out_img.ravel()
    out_img=out_img[~np.isnan(out_img)]
    for i in quantile_data:        
        quantile_data.loc[filename,i]=np.percentile(out_img,int(i))
                
quantile_data.reset_index(inplace=True)    
comb = np.concatenate((month_iter,numb),axis=0).reshape((228,2),order='F')
combined=[]
for i in comb:
    month=i[0]
    year=i[1]
    k=month+'-'+year
    combined.append(k)
combined=pd.DataFrame(combined, columns={'period'})

combined=combined.merge(quantile_data, left_on='period', right_on='index')
quantile_data=combined.drop('index', axis=1)
quantile_data.to_excel('G:/My on going proj/Satellite-Data-Analysis/quantile_data_savgol.xlsx', index=False)

## Rearrange the list as per seasons categorised by IMD
month=['Dec','Jan','Feb','Mar','Apr','May','June','July','Aug','Sept','Oct','Nov']
month=month*19
year = np.arange(2001,2020)
year = np.repeat(year,12)
my =[]
for index, i in enumerate(month):
    y= year[index]
    j =i+'-'+str(y)
    my.append(j)
    
##Mean of raster images
for files in glob.glob('*.tif'):
    files=files[ :-4]
    col_name.append(files)
mean_data = pd.DataFrame(columns={'mean_val'})        


for files in glob.glob('*.tif'):
    filename=files[ :-4]
    dataset =rasterio.open('G:/My on going proj/Satellite-Data-Analysis/Processed_raster_savgol_filter/'+str(files), mode='r')
    out_img, out_transform = mask(dataset, shapes=ind_geom, crop=True)
    out_img=out_img[0]
    out_img[out_img==0]='nan'  
    out_img=out_img.ravel()
    for i in mean_data:        
        mean_data.loc[filename,i]=np.nanmean(out_img)
                
mean_data .reset_index(inplace=True)    
comb = np.concatenate((month_iter,numb),axis=0).reshape((228,2),order='F')
combined=[]
for i in comb:
    month=i[0]
    year=i[1]
    k=month+'-'+year
    combined.append(k)
combined=pd.DataFrame(combined, columns={'period'})

combined=combined.merge(mean_data , left_on='period', right_on='index')
mean_data =combined.drop('index', axis=1)
mean_data .to_excel('G:/My on going proj/Satellite-Data-Analysis/mean_data_savgol.xlsx', index=False)


##read neighbouring district shapefiles
ind =gpd.read_file(r'F:/neeri/MODIS/BOUNDARY/DISTRICT_4nov19.shp')
ind=ind.dissolve(by="STATE")
ind.reset_index(inplace=True)
ind['geometry']=ind['geometry'].buffer(0.0001)
ind.to_crs(epsg=4326, inplace=True)
bihar=ind[ind['STATE']=='BIHAR']
up=ind[ind['STATE']=='UTTAR PRADESH']
jh=ind[ind['STATE']=='JHARKHAND']
# wb=ind[ind['STATE']=='WEST BENGAL']
# j=bihar.append(up).append(jh).append(wb)
j=bihar.append(up).append(jh)
ind_geom = j['geometry']

#Generate histogram for monthly mean raster
monthly_df =pd.DataFrame()
month=['January','February','March','April','May','June','July','August','September','October','November','December']
for i in month:
    short_i =i[ :3]
    for j in glob.glob('*.tif'):
        short_j =j[ :3]
        if short_i==short_j:
            k =rasterio.open('G:/My on going proj/Satellite-Data-Analysis/Processed_raster/Raster_monthly_savgol/'+str(j))
            out_img, out_transform=mask(k, shapes=ind_geom,crop=True)            
            out_img = out_img.ravel()
            out_img[out_img==0]='nan'
            out_img = out_img[~np.isnan(out_img)]
            monthly_df[i]=out_img

fig = plt.figure(figsize=(15,15))
numb=1
for i in monthly_df:
    colvalue =monthly_df[i]
    ax1=fig.add_subplot(4,3,numb)
    plt.subplots_adjust(wspace=0.45,hspace=0.6)
    fig.set_figheight(12.5)
    fig.set_figwidth(12.5)    
    ax1.set_ylabel('Count', fontweight='bold', fontsize=10)
    ax1.set_xlabel('AOD', fontweight='bold', fontsize=10)
    ax1.set_title(i,fontweight='bold', fontsize=15)
    ax1.title.set_position([0.5,1.02])
    ax1.tick_params(length=5, pad=10, width=3)
    ax1.xaxis.set_tick_params(labelsize=10)
    ax1.yaxis.set_tick_params(labelsize=10)
    plt.xticks(np.arange(min(colvalue),max(colvalue),0.1),weight='bold')
    ax1.xaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    plt.yticks(weight='bold')
    plt.hist(colvalue, bins=25, edgecolor='black', facecolor='lightblue')
    numb=numb+1
    plt.savefig('G:/My on going proj/Satellite-Data-Analysis/Processed_raster/Raster_facets_savgol_updated/monthly_raster/histogram_monthly_bihar.png')
    
##Generate Histogram for yearly mean raster
year = np.arange(2001,2020,1)
yearly_df =pd.DataFrame()
for i in month:
    for j in glob.glob('*.tif'):
        i =i[ :3]
        j1 = j[ :3]
        if i==j1:
            k =rasterio.open('G:/My on going proj/Satellite-Data-Analysis/Processed_raster/Raster_monthly_savgol/'+str(j))
            out_img, out_transform=mask(k, shapes=ind_geom,crop=True)            
            out_img = out_img.ravel()
            out_img[out_img==0]=np.nan
            out_img = out_img[~np.isnan(out_img)]
            yearly_df[j1]=out_img

fig = plt.figure(figsize=(15,15))
numb=1
for i in yearly_df:
    colvalue =yearly_df[i]
    ax1=fig.add_subplot(4,3,numb)
    plt.subplots_adjust(wspace=0.5,hspace=0.8)
    fig.set_figheight(12.5)
    fig.set_figwidth(12.5)    
    ax1.set_ylabel('Count', fontweight='bold', fontsize=10)
    ax1.set_xlabel('AOD', fontweight='bold', fontsize=10)
    ax1.set_title(i,fontweight='bold', fontsize=15)
    ax1.title.set_position([0.5,1.02])
    ax1.tick_params(length=5, pad=5, width=3)
    ax1.xaxis.set_tick_params(labelsize=10)
    ax1.yaxis.set_tick_params(labelsize=10)
    plt.xticks(np.arange(min(colvalue),max(colvalue),0.1),weight='bold')
    ax1.xaxis.set_major_formatter(ticker.FormatStrFormatter('%.1f'))
    plt.yticks(weight='bold')
    plt.hist(colvalue, bins=25, edgecolor='black', facecolor='lightblue')
    numb=numb+1



##Generate seasonal histogram
seasonal_df = pd.DataFrame()
for i in season:
    name = i.replace('_',"-")
    k =rasterio.open('G:/My on going proj/Satellite-Data-Analysis/Processed_raster/Raster_seasonal_savgol/'+str(i)+'.tif')
    out_img, out_transform=mask(k, shapes=ind_geom,crop=True)            
    out_img = out_img.ravel()
    out_img[out_img==0]=np.nan
    out_img = out_img[~np.isnan(out_img)]
    seasonal_df[name]=out_img

fig = plt.figure(figsize=(15,15))
numb=1
for i in seasonal_df:
    print(i)
    colvalue =seasonal_df[i]
    ax1=fig.add_subplot(2,2,numb)
    plt.subplots_adjust(wspace=0.35,hspace=0.3)
    fig.set_figheight(12.5)
    fig.set_figwidth(15)    
    ax1.set_ylabel('Count', fontweight='bold', fontsize=15)
    ax1.set_xlabel('AOD', fontweight='bold', fontsize=15)
    ax1.set_title(i,fontweight='bold', fontsize=20)
    ax1.title.set_position([0.5,1.02])
    ax1.tick_params(length=5, pad=5, width=3)
    ax1.xaxis.set_tick_params(labelsize=15)
    ax1.yaxis.set_tick_params(labelsize=15)
    ax1.spines['top'].set_linewidth(1.2)
    ax1.spines['bottom'].set_linewidth(1.2)
    ax1.spines['right'].set_linewidth(1.2)
    ax1.spines['left'].set_linewidth(1.2)
    if i == str('Winter'):    
        plt.xticks(np.arange(min(colvalue),max(colvalue),0.1),weight='bold')
        ax1.xaxis.set_major_formatter(ticker.FormatStrFormatter('%.1f'))
        plt.yticks(weight='bold')
        plt.hist(colvalue, bins=25, edgecolor='black', facecolor='lightblue')
    else:
        plt.xticks(np.arange(min(colvalue),max(colvalue),0.4),weight='bold')
        ax1.xaxis.set_major_formatter(ticker.FormatStrFormatter('%.1f'))
        plt.yticks(weight='bold')
        plt.hist(colvalue, bins=25, edgecolor='black', facecolor='lightblue')
    numb=numb+1
        
##Raster statistics
ind =gpd.read_file(r'F:/neeri/MODIS/BOUNDARY/DISTRICT_4nov19.shp')
ind.reset_index(inplace=True)
ind=ind[ind['STATE']=='BIHAR']
ind.to_crs(epsg=4326, inplace=True)
bihar_geom = ind[['DISTRICT','geometry']]
## Yearly
for i in glob.glob('*.tif'):
    comp =[]
    k=rasterio.open('G:/My on going proj/Satellite-Data-Analysis/Processed_raster/Raster_yearly_savgol/'+str(i))
    trans = k.transform
    out_img =k.read(1)
    stat =zonal_stats(bihar_geom,out_img,affine=trans, stats=['mean','min','max', 'median','percentile_10','percentile_90'],geojson_out=True)
    t=0
    while t <len(stat):
        stat =zonal_stats(bihar_geom,out_img,affine=trans, stats=['mean','min','max','median', 'percentile_10','percentile_90'],geojson_out=True)
        p=stat[t]['properties']
        comp.append(p)
        year =i[ :4]
        t=t+1
    comp=pd.DataFrame(comp)
    comp['year']= i[ :4]
    comp.to_excel('G:/My on going proj/Satellite-Data-Analysis/Processed_raster/Raster_facets_savgol_updated/district_stat_yearly/'+ i[:4]+'.xlsx', index=False)
    print('processing completed for: '+str(i))
    
##Monthly
for i in glob.glob('*.tif'):    
    comp =[]
    k=rasterio.open('G:/My on going proj/Satellite-Data-Analysis/Processed_raster/Raster_monthly_savgol/'+str(i))
    trans = k.transform
    out_img =k.read(1)
    stat =zonal_stats(bihar_geom,out_img,affine=trans, stats=['mean','min','max', 'median','percentile_10','percentile_90'],geojson_out=True)
    t=0
    while t <len(stat):
        stat =zonal_stats(bihar_geom,out_img,affine=trans, stats=['mean','min','max','median', 'percentile_10','percentile_90'],geojson_out=True)
        p=stat[t]['properties']
        comp.append(p)        
        t=t+1
    comp=pd.DataFrame(comp)
    comp['month']= i[ :-4]
    comp.to_excel('G:/My on going proj/Satellite-Data-Analysis/Processed_raster/Raster_facets_savgol_updated/district_stat_montly/'+ i[:-4]+'.xlsx', index=False)
    print('processing completed for: '+str(i))
    
##individual monthly cum yearly raster
month=['Jan','Feb','Mar','Apr','May','June','July','Aug','Sept','Oct','Nov','Dec']
year =np.arange(2001,2020,1)
for m in month:
    for y in year:        
        match = m+'-'+str(y)
        for i in glob.glob('*.tif'):
            if i[:-4]==match:
                comp =[]
                k=rasterio.open('G:/My on going proj/Satellite-Data-Analysis/Processed_raster_savgol_filter/'+str(i))
                trans = k.transform
                out_img =k.read(1)
                stat =zonal_stats(bihar_geom,out_img,affine=trans, stats=['mean','min','max', 'median','percentile_10','percentile_90'],geojson_out=True)
                t=0
                while t <len(stat):
                    stat =zonal_stats(bihar_geom,out_img,affine=trans, stats=['mean','min','max','median', 'percentile_10','percentile_90'],geojson_out=True)
                    p=stat[t]['properties']
                    comp.append(p)                    
                    t=t+1
                comp=pd.DataFrame(comp)
                comp['month']= m
                comp['year']=y
                comp.to_excel('G:/My on going proj/Satellite-Data-Analysis/Processed_raster/Raster_facets_savgol_updated/stat_individual_raster/'+ i[:-4]+'.xlsx', index=False)
                print('processing completed for: '+str(i[:-4]))

##Statistics for bihar state for individual
month=['Jan','Feb','Mar','Apr','May','June','July','Aug','Sept','Oct','Nov','Dec']
year =np.arange(2001,2020,1)
comp=[]
fig=[]
for y in year:
    for m in month:
        for i in glob.glob('*.tif'):
            match = m +'-'+str(y)
            if i[:-4]==match:
                k=rasterio.open('G:/My on going proj/Satellite-Data-Analysis/Processed_raster_savgol_filter/'+str(i))
                trans = k.transform
                out_img =k.read(1)
                stat =zonal_stats(ind_geom,out_img,affine=trans, stats=['mean','min','max', 'median','percentile_10','percentile_90'],geojson_out=True)
                p=stat[0]['properties']
                comp.append(p)
                fig.append(match)
                print('processing completed: '+str(match))
comp =pd.DataFrame(comp)
fig =pd.DataFrame(fig, columns={'month-year'})
bihar_state_stat =pd.concat([comp,fig], axis=1)    
bihar_state_stat.to_excel('G:/My on going proj/Satellite-Data-Analysis/Processed_raster/Raster_facets_savgol_updated/stat_individual_raster/bihar_state_stat.xlsx', index=False)

##stats for bihar state monthly
month=['Jan','Feb','Mar','Apr','May','June','July','Aug','Sept','Oct','Nov','Dec']
comp=[]
monthly=[]
for mon in month:
    for i in glob.glob('*.tif'):
        if mon==i[ :-4]:
            k=rasterio.open('G:/My on going proj/Satellite-Data-Analysis/Processed_raster/Raster_monthly_savgol/'+str(i))
            trans = k.transform
            out_img =k.read(1)
            stat =zonal_stats(ind_geom,out_img,affine=trans, stats=['mean','min','max', 'median','percentile_10','percentile_90'],geojson_out=True)
            p=stat[0]['properties']
            comp.append(p)
            monthly.append(mon)
            print('processing is complted: '+str(i[:-4]))
comp =pd.DataFrame(comp)
monthly =pd.DataFrame(monthly, columns={'month'})
bihar_state_stat =pd.concat([comp,monthly], axis=1) 
bihar_state_stat.to_excel('G:/My on going proj/Satellite-Data-Analysis/Processed_raster/Raster_facets_savgol_updated/district_stat_montly/bihar_state_monthlystat.xlsx', index=False)

##stats for bihar state yearly
comp=[]
yearly=[]
for i in glob.glob('*.tif'):
    mon=i[:-4]
    k=rasterio.open('G:/My on going proj/Satellite-Data-Analysis/Processed_raster/Raster_yearly_savgol/'+str(i))
    trans = k.transform
    out_img =k.read(1)
    stat =zonal_stats(ind_geom,out_img,affine=trans, stats=['mean','min','max', 'median','percentile_10','percentile_90'],geojson_out=True)
    p=stat[0]['properties']
    comp.append(p)
    yearly.append(mon)
    print('processing is complted: '+str(i[:-4]))
comp =pd.DataFrame(comp)
yearly =pd.DataFrame(yearly, columns={'year'})
bihar_state_stat =pd.concat([comp,yearly], axis=1) 
bihar_state_stat.to_excel('G:/My on going proj/Satellite-Data-Analysis/Processed_raster/Raster_facets_savgol_updated/district_stat_yearly/bihar_state_yearlystat.xlsx', index=False)

##Generate yearly difference maps
k=rasterio.open('G:/My on going proj/Satellite-Data-Analysis/Processed_raster/Raster_yearly_savgol/2001.tif')
out_img_2001, out_trnasform_2001=mask(k, shapes=ind_geom, crop=True)
left= out_trnasform_2001[2]
top= out_trnasform_2001[5]
out_img_2001=out_img_2001[0]
out_img_2001[out_img_2001==0]='nan'
a =out_img_2001.shape[0]
b=out_img_2001.shape[1]
out_img_2001=out_img_2001.ravel()
k=rasterio.open('G:/My on going proj/Satellite-Data-Analysis/Processed_raster/Raster_yearly_savgol/2019.tif')
out_img_2005, out_trnasform_2005=mask(k, shapes=ind_geom, crop=True)
out_img_2005=out_img_2005[0]
out_img_2005[out_img_2005==0]='nan'
out_img_2005=out_img_2005.ravel()
result =(out_img_2005-out_img_2001)*100/(out_img_2001)
result=np.reshape(result, (a,b))
plt.figure(figsize=(10,10))
ax1=plt.gca()
extent= (left,left+b*0.009,top-a*0.009,top)
fig=ax1.imshow(result, cmap=clrs, extent=extent, vmin=0, vmax=80)
bihar_geom.plot(ax=ax1,facecolor='none', edgecolor='k')
# ax1.xaxis.set_visible(False) 
# ax1.yaxis.set_visible(False)
plt.xticks(weight='bold')
plt.yticks(weight='bold')
ax1.xaxis.set_tick_params(labelsize=20)
ax1.yaxis.set_tick_params(labelsize=20)
divider=make_axes_locatable(ax1)
cax=divider.append_axes(position="right",size='4%')
cbar=plt.colorbar(fig,  extend='both', cax=cax)
cbar.ax.axes.tick_params(length=5,width=3)
cbar.ax.yaxis.set_tick_params(pad=10)
# cbar.ax.tick_params(width=3)
cbar.set_label( label='Percentage Increase',weight='bold', size=15, labelpad=12)
cbar.ax.tick_params(labelsize=20)
cbar.set_ticks([0,15, 30, 45, 60, 75])
cbar.ax.set_yticklabels(np.arange(0, 80, 15),weight='bold')


##Input GHSL data for analysis & merge & reproject for the year 2015 & 2000
merged =[]
for i in glob.glob('*.tif'):
    k=rasterio.open('G:/My on going proj/Satellite-Data-Analysis/G-MOD/G-MOD-2000/'+str(i))
    merged.append(k)
mosaic, out_transform =merge(merged)
out_meta = k.meta.copy()
out_meta.update({"driver": "GTiff",
                 "height": mosaic.shape[1],
                 "width": mosaic.shape[2],
                 "transform": out_transform,
                 "crs":k.crs
                 }
                )
with rasterio.open('G:/My on going proj/Satellite-Data-Analysis/G-MOD/G-MOD-2000/GSMOD_combined_projected.tif', "w", **out_meta) as dest:
    dest.write(mosaic)
    
## reprojection    
dst_crs = 'EPSG:4326'

with rasterio.open('G:/My on going proj/Satellite-Data-Analysis/G-MOD/G-MOD-2000/GSMOD_combined_projected.tif') as src:
    transform, width, height = calculate_default_transform(
        src.crs, dst_crs, src.width, src.height, *src.bounds)
    kwargs = src.meta.copy()
    kwargs.update({
        'crs': dst_crs,
        'transform': transform,
        'width': width,
        'height': height
    })

    with rasterio.open('G:/My on going proj/Satellite-Data-Analysis/G-MOD/Reprojected/GSMOD_combined_projected-2000.tif', 'w', **kwargs) as dst:
        for i in range(1, src.count + 1):
            reproject(
                source=rasterio.band(src, i),
                destination=rasterio.band(dst, i),
                src_transform=src.transform,
                src_crs=src.crs,
                dst_transform=transform,
                dst_crs=dst_crs,
                resampling=Resampling.nearest)

img = gdal.Open('G:/My on going proj/Satellite-Data-Analysis/G-MOD/Reprojected/GSMOD_combined_projected-2000.tif')
resamp_proj_aligned= gdal.Warp('GSMOD_gdal-2000.tif', img, xRes=a, yRes=a, outputBounds=bound)
resamp_proj_aligned= None


##Conduct data analysis with GHSL and AOD corresponding to the year 2001 & 2015
j=rasterio.open('G:/My on going proj/Satellite-Data-Analysis/G-MOD/Reprojected/GSMOD_gdal-2015.tif')
j_img, j_transform =mask(j, shapes=ind_geom, crop=True)
j_img=j_img[0]
j_img=j_img.astype('float32')
j_img[j_img==-200]='nan'
j_img_2015=j_img

j=rasterio.open('G:/My on going proj/Satellite-Data-Analysis/G-MOD/Reprojected/GSMOD_gdal-2000.tif')
j_img, j_transform =mask(j, shapes=ind_geom, crop=True)
j_img=j_img[0]
j_img=j_img.astype('float32')
j_img[j_img==-200]='nan'
j_img_2001=j_img

p=rasterio.open('G:/My on going proj/Satellite-Data-Analysis/Processed_raster/Raster_yearly_savgol/2016.tif')
p_img, p_trans =mask(p, shapes=ind_geom, crop=True)
p_img=p_img[0]
p_img[p_img==0]='nan'
p_img_2015=p_img

p=rasterio.open('G:/My on going proj/Satellite-Data-Analysis/Processed_raster/Raster_yearly_savgol/2001.tif')
p_img, p_trans =mask(p, shapes=ind_geom, crop=True)
p_img=p_img[0]
p_img[p_img==0]='nan'
p_img_2001=p_img

j_img_rav_2015 = j_img_2015.ravel()
p_img_rav_2015 = p_img_2015.ravel()
j_img_rav_2001 = j_img_2001.ravel()
p_img_rav_2001 = p_img_2001.ravel()

j_img_rav_2015=j_img_rav_2015[~np.isnan(j_img_rav_2015)]
p_img_rav_2015=p_img_rav_2015[~np.isnan(p_img_rav_2015)]
j_img_rav_2001=j_img_rav_2001[~np.isnan(j_img_rav_2001)]
p_img_rav_2001=p_img_rav_2001[~np.isnan(p_img_rav_2001)]

img_comb = np.concatenate((j_img_rav_2015,p_img_rav_2015,j_img_rav_2001,p_img_rav_2001), axis=0).reshape((104972,4), order='F')
img_comb=pd.DataFrame(img_comb, columns={'GHSL-2015','AOD-2015','GHSL-2001','AOD-2001'})
img_comb=img_comb.rename(columns={'GHSL-2001':'GHSL-2015','AOD-2001':'AOD-2015','GHSL-2015':'GHSL-2001','AOD-2015':'AOD-2001'})
img_comb.to_excel('G:/My on going proj/Satellite-Data-Analysis/G-MOD/AOD_with_MOD/Bihar_2016.xlsx', index=False)

##Data analysis on aod based on change in settlement observed using GHSL data
data =pd.read_excel('G:/My on going proj/Satellite-Data-Analysis/G-MOD/AOD_with_MOD/Bihar.xlsx')
class_set1 = data['GHSL-2001'].unique().tolist()
class_set2 = data['GHSL-2015'].unique().tolist()
data_analysis =pd.DataFrame(columns={'GHSL-2001','GHSL-2015','AOD-2001','AOD-2015','count'})
combined =[]
p=0
for i in class_set1:
    for j in class_set2:        
        val =data.loc[(data['GHSL-2001']==i) & (data['GHSL-2015']==j)]
        data_analysis.loc[p,'GHSL-2001']=i
        data_analysis.loc[p,'GHSL-2015']=j
        data_analysis.loc[p,'AOD-2001']=np.mean(val.iloc[:,3])
        data_analysis.loc[p,'AOD-2015']=np.mean(val.iloc[:,1])
        data_analysis.loc[p,'count']=len(val)
        p=p+1
data_analysis=data_analysis[['GHSL-2001','AOD-2001','GHSL-2015','AOD-2015','count']]
data_analysis.to_excel('G:/My on going proj/Satellite-Data-Analysis/G-MOD/AOD_with_MOD_final/Bihar_2016.xlsx', index=False)

##Analyse the change oberved in AOD due to shift in LU/LC (ie., GHSL) for various states in Bihar
ind =gpd.read_file(r'F:/neeri/MODIS/BOUNDARY/DISTRICT_4nov19.shp')
ind=ind[ind['STATE']=='BIHAR']
bihar_districts = ind['DISTRICT'].tolist()
bihar_districts= ['ARARIYA']
month=['Dec']
for dist in bihar_districts:   
    ind =gpd.read_file(r'F:/neeri/MODIS/BOUNDARY/DISTRICT_4nov19.shp')
    ind=ind[ind['STATE']=='BIHAR']
    ind=ind[ind['DISTRICT']==dist]    
    ind.to_crs(epsg=4326, inplace=True)
    ind_geom = ind['geometry']
    for m in month:
        j=rasterio.open('G:/My on going proj/Satellite-Data-Analysis/G-MOD/Reprojected/GSMOD_gdal-2015.tif')
        j_img, j_transform =mask(j, shapes=ind_geom, crop=True)
        j_img=j_img[0]
        j_img=j_img.astype('float32')
        j_img[j_img==-200]='nan'
        j_img_2015=j_img
        
        j=rasterio.open('G:/My on going proj/Satellite-Data-Analysis/G-MOD/Reprojected/GSMOD_gdal-2000.tif')
        j_img, j_transform =mask(j, shapes=ind_geom, crop=True)
        j_img=j_img[0]
        j_img=j_img.astype('float32')
        j_img[j_img==-200]='nan'
        j_img_2001=j_img
        
        p=rasterio.open('G:/My on going proj/Satellite-Data-Analysis/Processed_raster_savgol_filter/'+str(m)+'-2015.tif')
        p_img, p_trans =mask(p, shapes=ind_geom, crop=True)
        p_img=p_img[0]
        p_img[p_img==0]='nan'
        p_img_2015=p_img
        
        p=rasterio.open('G:/My on going proj/Satellite-Data-Analysis/Processed_raster_savgol_filter/'+str(m)+'-2001.tif')
        p_img, p_trans =mask(p, shapes=ind_geom, crop=True)
        p_img=p_img[0]
        p_img[p_img==0]='nan'
        p_img_2001=p_img
        
        j_img_rav_2015 = j_img_2015.ravel()
        p_img_rav_2015 = p_img_2015.ravel()
        j_img_rav_2001 = j_img_2001.ravel()
        p_img_rav_2001 = p_img_2001.ravel()
        
        j_img_rav_2015=j_img_rav_2015[~np.isnan(j_img_rav_2015)]
        p_img_rav_2015=p_img_rav_2015[~np.isnan(p_img_rav_2015)]
        j_img_rav_2001=j_img_rav_2001[~np.isnan(j_img_rav_2001)]
        p_img_rav_2001=p_img_rav_2001[~np.isnan(p_img_rav_2001)]
        
        size =(p_img_rav_2001).size
        img_comb = np.concatenate((j_img_rav_2015,p_img_rav_2015,j_img_rav_2001,p_img_rav_2001), axis=0).reshape((size,4), order='F')
        img_comb=pd.DataFrame(img_comb, columns={'GHSL-2015','AOD-2015','GHSL-2001','AOD-2001'})
        img_comb=img_comb.rename(columns={'GHSL-2001':'GHSL-2015','AOD-2001':'AOD-2015','GHSL-2015':'GHSL-2001','AOD-2015':'AOD-2001'})
        img_comb['month']=m
        img_comb.to_excel('G:/My on going proj/Satellite-Data-Analysis/G-MOD/AOD_with_MOD/month_wise/'+str(dist)+'-'+str(m)+'.xlsx', index=False)
        print('Raw data compiled for: '+str(dist)+'-'+str(m))
    
    data_analysis =pd.DataFrame(columns={'GHSL-2001','GHSL-2015','AOD-2001','AOD-2015','count','month'})
    p=0
    for file_name in glob.glob('*.xlsx'):
        if file_name[0:3]==dist[0:3]:
            data =pd.read_excel('G:/My on going proj/Satellite-Data-Analysis/G-MOD/AOD_with_MOD/month_wise/'+str(file_name))
            class_set1 = data['GHSL-2001'].unique().tolist()
            class_set2 = data['GHSL-2015'].unique().tolist()            
            combined =[]            
            for i in class_set1:
                for k in class_set2:        
                    val =data.loc[(data['GHSL-2001']==i) & (data['GHSL-2015']==k)]
                    data_analysis.loc[p,'GHSL-2001']=i
                    data_analysis.loc[p,'GHSL-2015']=k
                    data_analysis.loc[p,'AOD-2001']=np.mean(val.iloc[:,3])
                    data_analysis.loc[p,'AOD-2015']=np.mean(val.iloc[:,1])
                    data_analysis.loc[p,'count']=len(val)
                    data_analysis.loc[p,'month']=file_name[ :-5]
                    p=p+1
    data_analysis=data_analysis[['GHSL-2001','AOD-2001','GHSL-2015','AOD-2015','count','month']]
    data_analysis.to_excel('G:/My on going proj/Satellite-Data-Analysis/G-MOD/AOD_with_MOD_final/month_wise/'+str(dist)+'.xlsx', index=False)
    print('Final analysis completed for: '+str(dist))

## generate rasterimage showing the percentage of data availability
comb =[]
for i in glob.glob('*.tif'):
    j =rasterio.open('G:/My on going proj/Satellite-Data-Analysis/Processed_raster/Raster_yearly_savgol/'+str(i))
    j_img, out_transform = mask(j, shapes=ind_geom, crop=True)
    j_img=j_img[0].ravel()
   #j =np.where(j>0, 1, 0)
    j_img[j_img==0]='nan'
    comb.append(j_img)
comb1 = np.array(comb).transpose()
q =rasterio.open('G:/My on going proj/Satellite-Data-Analysis/Processed_raster/Raster_yearly_savgol/2001.tif')
q=q.read(1).ravel()
comb2 =comb1[:,0]
k =np.concatenate((q, comb2), axis=0).reshape((2176362,2), order='F')

##overall average AOD for Bihar
avg = pd.DataFrame()
for i in os.listdir('G:/My on going proj/Satellite-Data-Analysis/Processed_raster_savgol_filter/'):
    k= rasterio.open('G:/My on going proj/Satellite-Data-Analysis/Processed_raster_savgol_filter/' +str(i))
    out_img, out_trnasform=mask(k, shapes=ind_geom, crop=True)
    left= out_trnasform[2]
    top= out_trnasform[5]
    out_img=out_img[0]
    out_img[out_img==0]=np.nan
    a =out_img.shape[0]
    b=out_img.shape[1]
    out_img=out_img.ravel()
    avg[i]= out_img
    print('processing done for:' +str(i))
avg = avg.to_numpy()
avg = np.nanmean(avg, axis=1).reshape((a,b))
avg[avg==0]= np.nan
fig = plt.figure(figsize=(15,15))
ax1=plt.gca()
extent= (left,left+b*0.009,top-a*0.009,top)
fig=ax1.imshow(avg, cmap=clrs, extent=extent, vmin=0.3, vmax=0.8)
ind_geom.plot(ax=ax1,facecolor='none', edgecolor='k')
# ax1.xaxis.set_visible(False) 
# ax1.yaxis.set_visible(False)
plt.xticks(weight='bold')
plt.yticks(weight='bold')
ax1.xaxis.set_tick_params(labelsize=30)
ax1.yaxis.set_tick_params(labelsize=30)
divider=make_axes_locatable(ax1)
cax=divider.append_axes(position="right",size='4%')
cbar=plt.colorbar(fig,  extend='both', cax=cax)
cbar.ax.axes.tick_params(length=5,width=3)
cbar.ax.yaxis.set_tick_params(pad=10)
# cbar.ax.tick_params(width=3)
cbar.set_label( label='AOD',weight='bold', size=25, labelpad=15)
cbar.ax.tick_params(labelsize=25)
cbar.set_ticks(np.arange(0, 0.9, 0.1))
cbar.ax.set_yticklabels(np.arange(0, 0.9, 0.1).round(1),weight='bold')      


##Graphical abstract
slope = pd.read_csv(r'G:/My on going proj/Satellite-Data-Analysis/Processed_raster/Raster_facets_savgol_updated/mk_openair_deseason.csv')
threshold = slope.iloc[38,2].round(5)
slope = slope.iloc[0:38,]
slope['cat']= np.where(slope['slope']>=threshold,'TRUE','FALSE')
slope['dist']= slope['dist'].str.upper()
bihar_merge = bihar.merge(slope, right_on='dist', left_on='DISTRICT')
col1 = mpl.colors.ListedColormap(['white','red'])
fig,ax = plt.subplots(figsize =(8,10))
ax = plt.gca()
ax.xaxis.set_visible(False)
ax.yaxis.set_visible(False)
bihar_merge.plot(ax=ax,categorical=True,  edgecolor='k', cmap=col1, column = 'cat', alpha=0.5)
bihar.plot(ax=ax, edgecolor='k', facecolor='none')

##RMSE between original and savgolay filter
rmse = pd.DataFrame(columns={'month','RMSE'})
# cat = pd.DataFrame(columns= {'act_img','pred_img'})
n=0
for i in glob.glob('*.tif'):        
    actual = rasterio.open('G:/My on going proj/Satellite-Data-Analysis/Raster_interpolated/'+str(i))
    act_img, act_trans = mask(actual, shapes = ind_geom, crop= True)
    act_img = act_img[0].ravel()
    act_img[act_img==0]= np.nan
    predict = rasterio.open('G:/My on going proj/Satellite-Data-Analysis/Processed_raster_savgol_filter/'+str(i))
    pred_img, pred_trans = mask(predict, shapes = ind_geom, crop= True)
    pred_img = pred_img[0].ravel()    
    dat = pd.DataFrame()
    dat['act_img']= act_img
    dat['pred_img']= pred_img  
    dat = dat.dropna()
    rmse.loc[n,'month']= str(i[:-4])
    error = mean_squared_error(dat['act_img'],dat['pred_img'], squared=False)
    rmse.loc[n,'RMSE']= error
    n=n+1
    print(str(i[ :-4])+ 'is completed' + str(error))
    
rmse.to_excel('G:/My on going proj/Satellite-Data-Analysis/savgol_rmse.xlsx', index = False)

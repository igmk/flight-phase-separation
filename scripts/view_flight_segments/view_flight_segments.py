# matplotlib==3.3.4
# xarray==0.17.0
# pandas==1.2.3
# numpy==1.20.1

import numpy as np
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from glob import glob
from matplotlib import cm
import xarray as xr
import yaml
import sys
import yaml


if __name__ == '__main__':
    
    # choose a flight
    campaign = 'ACLOUD'
    flight_number = 'RF04'
    aircraft = 'P5'
    date = '20170523'
    
    # read file with paths (set wdir to the current script location)
    with open('paths.yaml') as f:
        paths = yaml.safe_load(f)
    
    # read gps data
    file = paths['path_gps']+campaign.lower()+'/'+aircraft.lower()+'/gps_ins/'+campaign+'_polar'+aircraft[1]+'_'+date+'_'+flight_number+'.nc'
    ds_gps = xr.open_dataset(file)
    
    # read flight segments of flight
    file = '../../flight_phase_files/'+campaign+'/'+aircraft+'/'+campaign+'_'+aircraft+'_Flight-Segments_'+date+'_'+flight_number+'.yaml'
    with open(file, 'r') as f:
        flight_segments = yaml.safe_load(f)
    
    # read dropsondes of flight
    files = glob(paths['path_dropsonde']+campaign.lower()+'/dropsondes/'+date[:4]+'/'+date[4:6]+'/'+date[6:8]+'/*PQC.nc')
    dict_ds_dsd = {}  # dictionary of dropsondes
    for file in files:
        filename = file.split('/')[-1].split('_PQC')[0]
        dict_ds_dsd[filename] = xr.open_dataset(file)
    
    #%% plot track on map to get an overview
    data_crs = ccrs.PlateCarree()
    map_crs = ccrs.NorthPolarStereo()
    
    fig, ax = plt.subplots(1, 1, figsize=(5, 5), subplot_kw=dict(projection=map_crs))
    
    # add coastlines
    ax.coastlines()
    
    # plot flight: color is altitude
    #kwargs = dict(s=4, c=ds_gps.alt, linewidths=0, cmap='jet', vmin=0, vmax=3000, transform=data_crs)
    #ax.scatter(ds_gps.lon, ds_gps.lat, **kwargs)
    
    # plot flight in black
    kwargs = dict(s=4, color='k', linewidths=0, transform=data_crs)
    ax.scatter(ds_gps.lon, ds_gps.lat, **kwargs)
    
    # plot flight segments as colored points
    n = len(flight_segments['segments'])
    cmap = cm.get_cmap('prism')
    colors = [cmap(i/n) for i in range(n)]
    
    for i, flight_segment in enumerate(flight_segments['segments']):
        
        start = flight_segment['start']
        end = flight_segment['end']
        name = flight_segment['name']
        
        if start and end:
        
            kwargs = dict(s=10, color=colors[i], linewidths=0, transform=data_crs)
            ax.scatter(ds_gps.lon.sel(time=slice(start, end)), ds_gps.lat.sel(time=slice(start, end)), **kwargs)
            
            ax.annotate(flight_segment['name'], xy=ax.projection.transform_point(ds_gps.lon.sel(time=start), ds_gps.lat.sel(time=start), data_crs), va='top', ha='left')
            ax.annotate(flight_segment['name'], xy=ax.projection.transform_point(ds_gps.lon.sel(time=end), ds_gps.lat.sel(time=end), data_crs), va='bottom', ha='left', color='gray')
    
    plt.show()

    #%% plot time series
    fig, axes = plt.subplots(7, 1, figsize=(9, 9), sharex=True, constrained_layout=True)
    
    fig.suptitle(campaign+', '+flight_number+', '+aircraft+', '+date)
    
    kwargs = dict(linewidths=0, c='k', s=1)
    ds_kwargs = dict(linewidths=0, c='r', s=1)
    
    # latitude and longitude
    axes[0].scatter(ds_gps.time, ds_gps.lat, **kwargs)
    axes[0].set_ylabel('lat [°N]')
        
    axes[1].scatter(ds_gps.time, ds_gps.lon, **kwargs)
    axes[1].set_ylabel('lon [°E]')
    
    # flight altitude
    axes[2].scatter(ds_gps.time, ds_gps.alt, **kwargs)
    axes[2].set_ylabel('alt [m]')
    
    # vertical speed
    axes[3].scatter(ds_gps.time, ds_gps.vs, **kwargs)
    axes[3].set_ylabel('vs [m/s]')
    axes[3].set_ylim([-10, 10])
    axes[3].fill_between(x=ds_gps.time, y1=0, y2=ds_gps.vs, color='#9087ea', alpha=0.5, linewidth=0)

    # roll angle
    axes[4].scatter(ds_gps.time, ds_gps['roll'], **kwargs)
    axes[4].fill_between(x=ds_gps.time, y1=0, y2=ds_gps['roll'], color='red', alpha=0.5, linewidth=0)
    axes[4].set_ylabel('roll [°]')

    # add pitch angle
    axes[5].scatter(ds_gps.time, ds_gps.pitch, **kwargs)
    axes[5].fill_between(x=ds_gps.time, y1=3, y2=ds_gps['pitch'], color='red', alpha=0.5, linewidth=0)
    axes[5].set_ylabel('pitch [°]')
    
    # add heading
    axes[6].scatter(ds_gps.time, ds_gps.heading, **kwargs)
    axes[6].set_ylabel('head [°]')
    axes[6].set_ylim([-180, 180])
    axes[6].set_yticks([-180, -90, 0, 90, 180])
    
    # add dropsondes
    for ds_name, ds_dsd in dict_ds_dsd.items():
        
        # latitude plot
        axes[0].scatter(ds_dsd.time, ds_dsd.lat, **ds_kwargs)
        axes[0].annotate(ds_name, xy=(ds_dsd.time[0], 0), xycoords=('data', 'axes fraction'), color='green', fontsize=7)
        
        # longitude plot
        axes[1].scatter(ds_dsd.time, ds_dsd.lon, **ds_kwargs)
        axes[1].annotate(ds_name, xy=(ds_dsd.time[0], 0), xycoords=('data', 'axes fraction'), color='green', fontsize=7)

        # altitude plot
        axes[2].scatter(ds_dsd.time, ds_dsd.alt, **ds_kwargs)
        axes[2].annotate(ds_name, xy=(ds_dsd.time[0], 0), xycoords=('data', 'axes fraction'), color='green', fontsize=7)

    # date axis settings
    axes[5].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    plt.setp(axes[5].xaxis.get_majorticklabels(), rotation=30)
    axes[5].set_xlabel('Time (hh:mm:ss) [UTC]')
    
    # add flight segments as vertical line
    for i_ax, ax in enumerate(axes):
        for flight_segment in flight_segments['segments']:
            
            start = flight_segment['start']
            end = flight_segment['end']
            name = flight_segment['name']
            
            if start and end:
            
                ax.axvline(start, color='blue', alpha=0.5)
                ax.axvline(end, color='green', alpha=0.5, linestyle='--')
                
                if i_ax == 0:
                    ax.annotate('start: '+name, xy=(start, 1), va='bottom', ha='left', xycoords=('data', 'axes fraction'), fontsize=8, rotation=90, color='blue')
                    ax.annotate('end: '+name, xy=(end, 1), va='bottom', ha='right', xycoords=('data', 'axes fraction'), fontsize=8, rotation=90, color='green')
    plt.show()

# matplotlib==3.3.4
# xarray==0.17.0
# pandas==1.2.3
# numpy==1.20.1

import numpy as np
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backend_bases import MouseButton
from glob import glob
from matplotlib import cm
import xarray as xr
import yaml
import sys


def tellme(s):
    print(s)
    plt.title(s, fontsize=16)
    plt.draw()


if __name__ == '__main__':
    
    # # choose a flight
    # campaign = 'ACLOUD'
    # flight['number'] = 'RF14'
    # flight['aircraft'] = 'P5'
    # flight['date'] = '20170608'

    # read file with flight settings
    with open('flight_settings.yaml') as f:
        flight = yaml.safe_load(f)
    
    # read file with paths (set wdir to the current script location)
    with open('paths.yaml') as f:
        paths = yaml.safe_load(f)
    
    # read gps data
    file = paths['path_gps']+flight['campaign'].lower()+'/'+flight['aircraft'].lower()+'/gps_ins/'+flight['campaign']+'_polar'+flight['aircraft'][1]+'_'+flight['date']+'_'+flight['number']+'.nc'
    ds_gps = xr.open_dataset(file)
    
    # read sea ice along path
    file = paths['path_sea_ice']+flight['campaign']+'_polar'+flight['aircraft'][-1]+'_'+flight['date']+'_'+flight['number']+'.nc'
    ds_sic = xr.open_dataset(file)
    
    # read flight segments of flight
    file = '../../flight_phase_files/'+flight['campaign']+'/'+flight['aircraft']+'/'+flight['campaign']+'_'+flight['aircraft']+'_Flight-Segments_'+flight['date']+'_'+flight['number']+'.yaml'
    with open(file, 'r') as f:
        flight_segments = yaml.safe_load(f)
    
    # read dropsondes of flight
    files = glob(paths['path_dropsonde']+flight['campaign'].lower()+'/dropsondes/'+flight['date'][:4]+'/'+flight['date'][4:6]+'/'+flight['date'][6:8]+'/*PQC.nc')
    dict_ds_dsd = {}  # dictionary of dropsondes
    for file in files:
        filename = file.split('/')[-1].split('_PQC')[0]
        dict_ds_dsd[filename] = xr.open_dataset(file)
    
    #%% plot track on map to get an overview
    print('plot track on map')
    
    data_crs = ccrs.PlateCarree()
    map_crs = ccrs.NorthPolarStereo()
        
    fig, ax = plt.subplots(1, 1, figsize=(5, 5), subplot_kw=dict(projection=map_crs))
    ax.coastlines()
    
    # plot flight in black
    kwargs = dict(s=4, color='k', linewidths=0, transform=data_crs, zorder=0)
    ax.scatter(ds_gps.lon, ds_gps.lat, **kwargs)
    
    # plot flight segments as colored points
    n = len(flight_segments['segments'])
    cmap = cm.get_cmap('prism')
    colors = [cmap(i/n) for i in range(n)]
    
    for i, flight_segment in enumerate(flight_segments['segments']):
        
        tellme('Draw next segment: right mouse button\nStop drawing: middle mouse button')
        pts = plt.ginput(n=1, timeout=-1, show_clicks=False, mouse_add=MouseButton.RIGHT, mouse_stop=MouseButton.MIDDLE, mouse_pop=MouseButton.LEFT)
        
        if 'segment_id' in flight_segment.keys():
            print('plot segment id %s'%flight_segment['segment_id'])
        else:
            print('plot segment id ???')
        
        start = flight_segment['start']
        end = flight_segment['end']
        
        # workaround for flight segments without a name
        try:
            name = flight_segment['name']
        
        except KeyError:
            name = ', '.join(flight_segment['kinds'])
        
        if start and end:
        
            kwargs = dict(s=10, color=colors[i], linewidths=0, transform=data_crs, zorder=1)
            ax.scatter(ds_gps.lon.sel(time=slice(start, end)), ds_gps.lat.sel(time=slice(start, end)), **kwargs)
            
            kwargs = dict(fontsize=8, ha='left')
            ax.annotate(name, xy=ax.projection.transform_point(ds_gps.lon.sel(time=start), ds_gps.lat.sel(time=start), data_crs), va='top', color='k', **kwargs)
            ax.annotate(name, xy=ax.projection.transform_point(ds_gps.lon.sel(time=end), ds_gps.lat.sel(time=end), data_crs), va='bottom', color='gray', **kwargs)
    
        # add parts, if they exist for this flight segment
        if 'parts' in list(flight_segment.keys()):
                        
            for j, part in enumerate(flight_segment['parts']):
                
                if 'segment_id' in part.keys():
                    print('plot segment id %s'%part['segment_id'])
                else:
                    print('plot segment id ???')
                
                start = part['start']
                end = part['end']
                
                # workaround for flight segments without a name
                try:
                    name = part['name']
                
                except KeyError:
                    name = ', '.join(part['kinds'])
                
                if start and end:
                
                    kwargs = dict(s=2, color=colors[j], linewidths=0.25, transform=data_crs, marker='+', zorder=2)
                    ax.scatter(ds_gps.lon.sel(time=slice(start, end)), ds_gps.lat.sel(time=slice(start, end)), **kwargs)
                    
                    kwargs = dict(fontsize=6, ha='right')
                    ax.annotate(name, xy=ax.projection.transform_point(ds_gps.lon.sel(time=start), ds_gps.lat.sel(time=start), data_crs), va='top', color='k', **kwargs)
                    ax.annotate(name, xy=ax.projection.transform_point(ds_gps.lon.sel(time=end), ds_gps.lat.sel(time=end), data_crs), va='bottom', color='gray', **kwargs)
    
    tellme('All segments are drawn')
    plt.show()


import numpy as np
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from matplotlib.backend_bases import MouseButton
from matplotlib import cm
import yaml
import ac3airborne
import os

#ac3cloud_username = os.environ['AC3_USER']
#ac3cloud_password = os.environ['AC3_PASSWORD']


def tellme(s):
    print(s)
    plt.title(s, fontsize=16)
    plt.draw()


if __name__ == '__main__':

    # read file with flight settings
    with open('flight_settings.yaml') as f:
        flight = yaml.safe_load(f)
    
    flight_id = flight['mission']+'_'+flight['platform']+'_'+flight['name']
    
    # read data
    cat = ac3airborne.get_intake_catalog()
    try:
        ds_gps = cat[flight['mission']][flight['platform']]['GPS_INS'][flight_id].to_dask()
    except TypeError:
        ds_gps = cat[flight['mission']][flight['platform']]['GPS_INS'][flight_id](user=ac3cloud_username,password=ac3cloud_password).to_dask()
    
    # read flight segments of flight
    file = '../flight_phase_files/'+flight['mission']+'/'+flight['platform']+'/'+flight['mission']+'_'+flight['platform']+'_Flight-Segments_'+flight['date']+'_'+flight['name']+'.yaml'
    with open(file, 'r') as f:
        flight_segments = yaml.safe_load(f)
    
    #%% plot track on map to get an overview
    print('plot track on map')
    
    data_crs = ccrs.PlateCarree()
    map_crs = ccrs.NorthPolarStereo()
        
    fig, ax = plt.subplots(1, 1, figsize=(12, 8), subplot_kw=dict(projection=map_crs))
    ax.coastlines()
    
    # plot flight in black
    kwargs = dict(s=4, color='k', linewidths=0, transform=data_crs, zorder=0)
    ax.scatter(ds_gps.lon, ds_gps.lat, **kwargs)
    
    # plot flight segments as colored points
    cmap = cm.get_cmap('gist_rainbow')
    n = len(flight_segments['segments'])
    rnd = np.random.uniform(low=0, high=1, size=n)
    colors1 = cmap(rnd)
    
    for i, flight_segment in enumerate(flight_segments['segments']):
        
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
        
            kwargs = dict(s=10, color=colors1[i], linewidths=0, transform=data_crs, zorder=1)
            ax.scatter(ds_gps.lon.sel(time=slice(start, end)), ds_gps.lat.sel(time=slice(start, end)), **kwargs)
            
            kwargs = dict(fontsize=8, ha='left')
            ax.annotate(name, xy=ax.projection.transform_point(ds_gps.lon.sel(time=start, method='nearest'), ds_gps.lat.sel(time=start, method='nearest'), data_crs), va='top', color='k', **kwargs)
            ax.annotate(name, xy=ax.projection.transform_point(ds_gps.lon.sel(time=end, method='nearest'), ds_gps.lat.sel(time=end, method='nearest'), data_crs), va='bottom', color='gray', **kwargs)
        tellme('Segment: '+flight_segment['name']+'\nnext segment: right click')
    
        # add parts, if they exist for this flight segment
        if 'parts' in list(flight_segment.keys()):
            
            # make cmap for parts
            n = len(flight_segment['parts'])
            rnd = np.random.uniform(low=0, high=1, size=n)
            colors2 = cmap(rnd)
                        
            for j, part in enumerate(flight_segment['parts']):
                
                pts = plt.ginput(n=1, timeout=-1, show_clicks=False, mouse_add=MouseButton.RIGHT, mouse_stop=MouseButton.MIDDLE, mouse_pop=MouseButton.LEFT)
        
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
                
                    kwargs = dict(s=2, color=colors2[j], linewidths=0.25, transform=data_crs, marker='+', zorder=2)
                    ax.scatter(ds_gps.lon.sel(time=slice(start, end)), ds_gps.lat.sel(time=slice(start, end)), **kwargs)
                    
                    kwargs = dict(fontsize=6, ha='right')
                    ax.annotate(name, xy=ax.projection.transform_point(ds_gps.lon.sel(time=start, method='nearest'), ds_gps.lat.sel(time=start, method='nearest'), data_crs), va='top', color='k', **kwargs)
                    ax.annotate(name, xy=ax.projection.transform_point(ds_gps.lon.sel(time=end, method='nearest'), ds_gps.lat.sel(time=end, method='nearest'), data_crs), va='bottom', color='gray', **kwargs)
                tellme('Segment: '+part['name']+'\nnext segment: right click')
    
    tellme('All segments are drawn')
    plt.show()

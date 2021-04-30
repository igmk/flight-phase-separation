

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
    
    # read flight segments of flight
    file = '../../flight_phase_files/'+flight['campaign']+'/'+flight['aircraft']+'/'+flight['campaign']+'_'+flight['aircraft']+'_Flight-Segments_'+flight['date']+'_'+flight['number']+'.yaml'
    with open(file, 'r') as f:
        flight_segments = yaml.safe_load(f)
    
    #%% plot track on map to get an overview        
    for i, flight_segment in enumerate(flight_segments['segments']):

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
            
            fig, ax = plt.subplots(1, 1, figsize=(10, 4), constrained_layout=True)
            
            steps = 100
            bins = np.arange(0, 20000+steps, steps)
            ax.hist(ds_gps.alt.sel(time=slice(start, end))*3.28, color='k', bins=bins)
            
            # annotate min max median
            kwargs = dict(ha='left', va='top', xycoords='axes fraction')
            ax.annotate('min:\n{:,} ft'.format(int(np.round(ds_gps.alt.sel(time=slice(start, end)).min('time').values.item()*3.28)), 0),
                        xy=(1.05, 0.3), **kwargs)
            ax.annotate('max:\n{:,} ft'.format(int(np.round(ds_gps.alt.sel(time=slice(start, end)).max('time').values.item()*3.28)), 0),
                        xy=(1.05, 0.1), **kwargs)
            ax.annotate('median:\n{:,} ft'.format(int(np.round(ds_gps.alt.sel(time=slice(start, end)).median('time').values.item()*3.28)), 0),
                        xy=(1.05, 1), **kwargs)
            ax.annotate('mean:\n{:,} ft'.format(int(np.round(ds_gps.alt.sel(time=slice(start, end)).mean('time').values.item()*3.28)), 0),
                        xy=(1.05, 0.8), **kwargs)
            
            ax.set_xlabel('Altitude, {} steps [ft]'.format(steps))
            ax.set_ylabel('Count')
            
            tellme('Segment: '+name+'\nNext: right mouse')
            pts = plt.ginput(n=1, timeout=-1, show_clicks=False, mouse_add=MouseButton.RIGHT, mouse_stop=MouseButton.MIDDLE, mouse_pop=MouseButton.LEFT)
            
            plt.close()
            
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
                    
                    fig, ax = plt.subplots(1, 1, figsize=(7, 4), constrained_layout=True)
                    
                    bins = np.arange(0, 20000, 100)
                    ax.hist(ds_gps.alt.sel(time=slice(start, end))*3.28, color='k', bins=bins)
                    
                    # annotate min max median
                    kwargs = dict(ha='left', va='top', xycoords='axes fraction')
                    ax.annotate('min:\n{:,} ft'.format(int(np.round(ds_gps.alt.sel(time=slice(start, end)).min('time').values.item()*3.28)), 0),
                                xy=(1.05, 0.3), **kwargs)
                    ax.annotate('max:\n{:,} ft'.format(int(np.round(ds_gps.alt.sel(time=slice(start, end)).max('time').values.item()*3.28)), 0),
                                xy=(1.05, 0.1), **kwargs)
                    ax.annotate('median:\n{:,} ft'.format(int(np.round(ds_gps.alt.sel(time=slice(start, end)).median('time').values.item()*3.28)), 0),
                                xy=(1.05, 1), **kwargs)
                    ax.annotate('mean:\n{:,} ft'.format(int(np.round(ds_gps.alt.sel(time=slice(start, end)).mean('time').values.item()*3.28)), 0),
                                xy=(1.05, 0.8), **kwargs)
                    
                    ax.set_xlabel('Altitude, {} steps [ft]'.format(steps))
                    ax.set_ylabel('Count')
            
                    tellme('Segment: '+name+'\nNext: right mouse')
                    pts = plt.ginput(n=1, timeout=-1, show_clicks=False, mouse_add=MouseButton.RIGHT, mouse_stop=MouseButton.MIDDLE, mouse_pop=MouseButton.LEFT)
            
                    plt.close()

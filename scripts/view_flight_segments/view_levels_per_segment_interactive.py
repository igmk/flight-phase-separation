

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


def plot_histograms(ds_gps, start, end):
    """Plot histograms of variables"""

    fig, [ax1, ax2, ax3] = plt.subplots(3, 1, figsize=(13, 9), constrained_layout=True)
    
    # define steps/nbins of histograms
    steps_ft = 100
    min_ft, max_ft = [0, 20000]
    bins_alt = np.arange(min_ft, max_ft+steps_ft, steps_ft)
    nbins_alt = 100
    steps_deg = 1
    bins_head = np.arange(-180, 180+steps_deg, steps_deg)

    # flight altitude
    ax1.hist(ds_gps.alt.sel(time=slice(start, end))*3.28, color='k', bins=bins_alt)
    ax1.set_xlim([min_ft, max_ft])
    ax1.set_xlabel('Altitude [ft], step width: {} ft'.format(steps_ft))
    ax1.set_ylabel('Count')
    
    # annotate flight levels
    lvls = [1000, 2000, 4000]  # in m
    for lvl in lvls:
        ax1.axvline(x=lvl*3.28, color='blue')
        ax1.annotate(str(lvl)+' m', xy=(lvl*3.28, 1.01), xycoords=('data', 'axes fraction'), ha='center', va='bottom', color='blue')
    ax1.annotate('low_level', xy=(500*3.28, 1.01), xycoords=('data', 'axes fraction'), ha='center', va='bottom', color='gray')
    ax1.annotate('mid_level', xy=(1500*3.28, 1.01), xycoords=('data', 'axes fraction'), ha='center', va='bottom', color='gray')
    ax1.annotate('high_level', xy=(3000*3.28, 1.01), xycoords=('data', 'axes fraction'), ha='center', va='bottom', color='gray')

    ax2.hist(ds_gps.alt.sel(time=slice(start, end))*3.28, color='k', bins=nbins_alt)
    ax2.set_xlabel('Altitude [ft], number of bins: {}'.format(nbins_alt))
    ax2.set_ylabel('Count')
    
    # annotate min max median of altitude
    kwargs = dict(ha='right', va='top', xycoords='axes fraction')
    ax1.annotate('min: {:,} ft'.format(int(np.round(ds_gps.alt.sel(time=slice(start, end)).min('time').values.item()*3.28)), 0),
                xy=(1, 0.75), **kwargs)
    ax1.annotate('max: {:,} ft'.format(int(np.round(ds_gps.alt.sel(time=slice(start, end)).max('time').values.item()*3.28)), 0),
                xy=(1, 0.5), **kwargs)
    ax1.annotate('median: {:,} ft'.format(int(np.round(ds_gps.alt.sel(time=slice(start, end)).median('time').values.item()*3.28)), 0),
                xy=(1, 1), **kwargs)
    
    # heading
    ax3.hist(ds_gps.heading.sel(time=slice(start, end)), color='gray', bins=bins_head)
    ax3.set_xlim([-180, 180])
    ax3.set_xticks(np.arange(-180, 180+45, 45))
    ax3.set_xlabel('Heading [°], bin width: {}°'.format(steps_deg))
    ax3.set_ylabel('Count')
    
    for ax in fig.axes:      
        
        ax.spines["top"].set_visible(False)  
        ax.spines["right"].set_visible(False)  
        ax.get_xaxis().tick_bottom()  
        ax.get_yaxis().tick_left()
    
    return fig


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
    
    #%% plot histograms  
      
    for i, flight_segment in enumerate(flight_segments['segments']):
        
        name = flight_segment['name']
        start = flight_segment['start']
        end = flight_segment['end']
        
        if start and end:
            
            fig = plot_histograms(ds_gps, start, end)
            fig.suptitle('segment: '+name+'\ndraw next segment: any key or right mouse')
            plt.draw()
            pts = plt.ginput(n=1, timeout=-1, show_clicks=False, mouse_add=MouseButton.RIGHT, mouse_stop=MouseButton.MIDDLE, mouse_pop=MouseButton.LEFT)
            plt.close()
        
        if 'parts' in list(flight_segment.keys()):  # add parts, if they exist for this flight segment
                        
            for j, part in enumerate(flight_segment['parts']):

                name = part['name']
                start = part['start']
                end = part['end']
                
                if start and end:
                    
                    fig = plot_histograms(ds_gps, start, end)
                    fig.suptitle('segment: '+name+'\ndraw next segment: any key or right mouse')
                    plt.draw()
                    pts = plt.ginput(n=1, timeout=-1, show_clicks=False, mouse_add=MouseButton.RIGHT, mouse_stop=MouseButton.MIDDLE, mouse_pop=MouseButton.LEFT)
                    plt.close()

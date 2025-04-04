

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backend_bases import MouseButton
import yaml
import ac3airborne
import os

#ac3cloud_username = os.environ['AC3_USER']
#ac3cloud_password = os.environ['AC3_PASSWORD']


def plot_histograms(ds_gps, start, end):
    """Plot histograms of variables"""

    fig, [ax1, ax2, ax3] = plt.subplots(3, 1, figsize=(13, 9), constrained_layout=True)

    # define steps/nbins of histograms
    steps_ft = 100
    min_ft, max_ft = [0, 45000]
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
    ax1.annotate('min/max: {:,} - {:,} ft'.format(int(np.around(ds_gps.alt.sel(time=slice(start, end)).min('time').values.item()*3.28, -2)),
                                                  int(np.around(ds_gps.alt.sel(time=slice(start, end)).max('time').values.item()*3.28, -2))),
                 xy=(1, 0.85), color='gray', **kwargs)
    ax1.annotate('median: {:,} ft'.format(int(np.around(ds_gps.alt.sel(time=slice(start, end)).median('time').values.item()*3.28, -2))),
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


def print_heights(ds_gps, start, end):
    """Print heights of flight leg"""

    z_min = int(np.around(ds_gps.alt.sel(time=slice(start, end)).min('time').values.item()*3.28, -2))
    z_max = int(np.around(ds_gps.alt.sel(time=slice(start, end)).max('time').values.item()*3.28, -2))
    z_med = int(np.around(ds_gps.alt.sel(time=slice(start, end)).median('time').values.item()*3.28, -2))
        
    print(f'median: {z_med} ft, min: {z_min} ft, max: {z_max} ft')


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
    
    #%% unify data
    if 'yaw' in list(ds_gps):
        ds_gps = ds_gps.rename({'yaw': 'heading'})
    
    #%% print levels
    for i, flight_segment in enumerate(flight_segments['segments']):
        
        print('\n')

        name = flight_segment['name']
        start = flight_segment['start']
        end = flight_segment['end']

        if start and end:
            
            print(name)
            print_heights(ds_gps, start, end)

        if 'parts' in list(flight_segment.keys()):  # add parts, if they exist for this flight segment

            for j, part in enumerate(flight_segment['parts']):

                name = part['name']
                start = part['start']
                end = part['end']

                if start and end:
                    
                    print(name)
                    print_heights(ds_gps, start, end)

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

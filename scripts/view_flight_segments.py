

import numpy as np
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from glob import glob
from matplotlib import cm
import xarray as xr
import yaml
import ac3airborne
import os

ac3cloud_username = os.environ['AC3_USER']
ac3cloud_password = os.environ['AC3_PASSWORD']


def distance(lat1, lon1, lat2, lon2):
    """
    Calculate distance in km between two geographic locations
    """
    
    R = 6371  # Earth's radius
    
    dlat = np.deg2rad(lat2-lat1)
    dlon = np.deg2rad(lon2-lon1)
    
    rlat1 = np.deg2rad(lat1)
    rlat2 = np.deg2rad(lat2)
    
    # distance
    a = np.sin(dlat/2) * np.sin(dlat/2) + np.cos(rlat1) * np.cos(rlat2) * np.sin(dlon/2) * np.sin(dlon/2) 
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    d = R * c
    
    return d


if __name__ == '__main__':

    # read file with flight settings
    with open('flight_settings.yaml') as f:
        flight = yaml.safe_load(f)

    with open('paths.yaml') as f:
        paths = yaml.safe_load(f)
    
    flight_id = flight['mission']+'_'+flight['platform']+'_'+flight['name']
    
    # read data
    cat = ac3airborne.get_intake_catalog()
    ds_gps = cat[flight['mission']][flight['platform']]['GPS_INS'][flight_id](user=ac3cloud_username,password=ac3cloud_password).to_dask()
    
    # read flight segments of flight
    file = '../flight_phase_files/'+flight['mission']+'/'+flight['platform']+'/'+flight['mission']+'_'+flight['platform']+'_Flight-Segments_'+flight['date']+'_'+flight['name']+'.yaml'
    with open(file, 'r') as f:
        flight_segments = yaml.safe_load(f)
    
    # read dropsondes of flight
    #files = glob(paths['path_dropsonde']+flight['mission'].lower()+'/dropsondes/'+flight['date'][:4]+'/'+flight['date'][4:6]+'/'+flight['date'][6:8]+'/*PQC.nc')
    files = glob(paths['path_dropsonde']+'HALO-AC3_HALO_Dropsondes_'+flight['date']+'_RF02/Level_1/D'+flight['date']+'_*QC.nc')
    dict_ds_dsd = {}  # dictionary of dropsondes
    for file in files:
        filename = file.split('/')[-1].split('QC')[0]
        dict_ds_dsd[filename] = xr.open_dataset(file)
    
    #%% unify data
    # yaw angle names from -180 to 180 in 45 deg steps
    if flight['platform'] == 'HALO':
        yaw_names = ['W', 'SW', 'S', 'SE', 'E', 'NE', 'N', 'NW', 'W']
        
    else:
        yaw_names = ['S', 'SW', 'W', 'NW', 'N', 'NE', 'E', 'SE', 'S']
        
    if 'yaw' in list(ds_gps):
        ds_gps = ds_gps.rename({'yaw': 'heading'})
    
    # create variable for speed and set values to nan, if they do not exist
    if 'gs' not in list(ds_gps):
        d = distance(ds_gps.lat.values[1:], ds_gps.lon.values[1:], ds_gps.lat.values[:-1], ds_gps.lon.values[:-1])*1e3  # m
        gs = d/((ds_gps.time.values[1:] - ds_gps.time.values[:-1])/np.timedelta64(1, 's'))
        gs = np.append(gs, 0)
        gs *= 1.94384  # m/s --> kn
        ds_gps['gs'] = (('time'), gs)
    
    # calculate vertical speed from altitude
    if 'vs' not in list(ds_gps):
        vs = (ds_gps.alt.values[1:] - ds_gps.alt.values[:-1])/((ds_gps.time.values[1:] - ds_gps.time.values[:-1])/np.timedelta64(1, 's'))
        vs = np.append(vs, 0)
        ds_gps['vs'] = (('time'), vs)
    
    #%% plot track on map to get an overview
    print('plot track on map')
    
    data_crs = ccrs.PlateCarree()
    map_crs = ccrs.NorthPolarStereo()
        
    fig, ax = plt.subplots(1, 1, figsize=(5, 5), subplot_kw=dict(projection=map_crs))
    ax.coastlines()
    
    # add places
    lon_n, lat_n = (11.922222, 78.925)     # coordinates Ny Alesund
    lon_l, lat_l = (15.633333, 78.216667)  # coordinates Longyearbyen
    lon_k, lat_k = (20.326667, 67.822222)  # coordinates Kiruna
    
    ax.scatter(lon_n, lat_n, marker='o', c='r', s=10, zorder=3, transform=data_crs, edgecolors='none')
    ax.annotate(text='NYA', xy=ax.projection.transform_point(lon_n, lat_n, data_crs))
    ax.scatter(lon_l, lat_l, marker='o', c='r', s=10, zorder=3, transform=data_crs, edgecolors='none')
    ax.annotate(text='LYR', xy=ax.projection.transform_point(lon_l, lat_l, data_crs), va='top', ha='center')
    ax.scatter(lon_k, lat_k, marker='o', c='r', s=10, zorder=3, transform=data_crs, edgecolors='none')
    ax.annotate(text='KIR', xy=ax.projection.transform_point(lon_k, lat_k, data_crs), va='top', ha='center')
    
    # plot flight in black
    kwargs = dict(s=4, color='k', linewidths=0, transform=data_crs, zorder=0)
    ax.scatter(ds_gps.lon, ds_gps.lat, **kwargs)
    
    # plot flight segments as colored points
    cmap = cm.get_cmap('gist_rainbow')
    n = len(flight_segments['segments'])
    rnd = np.random.uniform(low=0, high=1, size=n)
    colors1 = cmap(rnd)
    
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
        
            kwargs = dict(s=10, color=colors1[i], linewidths=0, transform=data_crs, zorder=1)
            ax.scatter(ds_gps.lon.sel(time=slice(start, end)), ds_gps.lat.sel(time=slice(start, end)), **kwargs)
            
            kwargs = dict(fontsize=8, ha='left')
            ax.annotate(name, xy=ax.projection.transform_point(ds_gps.lon.sel(time=start, method='nearest'), ds_gps.lat.sel(time=start, method='nearest'), data_crs), va='top', color='k', **kwargs)
            ax.annotate(name, xy=ax.projection.transform_point(ds_gps.lon.sel(time=end, method='nearest'), ds_gps.lat.sel(time=end, method='nearest'), data_crs), va='bottom', color='gray', **kwargs)
    
        # add parts, if they exist for this flight segment
        if 'parts' in list(flight_segment.keys()):
            
            # make cmap for parts
            n = len(flight_segment['parts'])
            rnd = np.random.uniform(low=0, high=1, size=n)
            colors2 = cmap(rnd)

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
                
                    kwargs = dict(s=2, color=colors2[j], linewidths=0.25, transform=data_crs, marker='+', zorder=2)

                    ax.scatter(ds_gps.lon.sel(time=slice(start, end)), ds_gps.lat.sel(time=slice(start, end)), **kwargs)
                    
                    kwargs = dict(fontsize=6, ha='right')
                    ax.annotate(name, xy=ax.projection.transform_point(ds_gps.lon.sel(time=start, method='nearest'), ds_gps.lat.sel(time=start, method='nearest'), data_crs), va='top', color='k', **kwargs)
                    ax.annotate(name, xy=ax.projection.transform_point(ds_gps.lon.sel(time=end, method='nearest'), ds_gps.lat.sel(time=end, method='nearest'), data_crs), va='bottom', color='gray', **kwargs)
            
    #%% plot time series
    print('plot time series')
    
    fig, axes = plt.subplots(8, 1, figsize=(9, 9), sharex=True, constrained_layout=True)
    
    fig.suptitle(flight['mission']+', '+flight['name']+', '+flight['platform']+', '+flight['date'])
    
    kwargs = dict(linewidths=0, c='k', s=1)
    ds_kwargs = dict(linewidths=0, c='r', s=1)
    
    # latitude and longitude
    axes[0].scatter(ds_gps.time, ds_gps.lat, **kwargs)
    axes[0].set_ylabel('lat [°N]')
        
    axes[1].scatter(ds_gps.time, ds_gps.lon, **kwargs)
    axes[1].set_ylabel('lon [°E]')

    # add line for ny-alesund
    axes[0].axhline(78.923538, color='green', linestyle=':')
    axes[1].axhline(11.909895, color='green', linestyle=':')
    
    # flight altitude
    axes[2].scatter(ds_gps.time, ds_gps.alt*3.28, **kwargs)
    axes[2].set_ylabel('alt [ft]')
    
    # vertical speed
    axes[3].scatter(ds_gps.time, ds_gps.vs, **kwargs)
    axes[3].set_ylabel('vs [m/s]')
    axes[3].set_ylim([-20, 20])
    axes[3].fill_between(x=ds_gps.time, y1=0, y2=ds_gps.vs, color='#9087ea', alpha=0.5, linewidth=0)

    # ground speed
    axes[4].scatter(ds_gps.time, ds_gps.gs, **kwargs)
    axes[4].set_ylabel('gs [kn]')
    axes[4].set_ylim([0, 500])
    
    # roll angle
    axes[5].scatter(ds_gps.time, ds_gps['roll'], **kwargs)
    axes[5].fill_between(x=ds_gps.time, y1=0, y2=ds_gps['roll'], color='red', alpha=0.5, linewidth=0)
    axes[5].set_ylabel('roll [°]')

    # add pitch angle
    axes[6].scatter(ds_gps.time, ds_gps.pitch, **kwargs)
    axes[6].fill_between(x=ds_gps.time, y1=3, y2=ds_gps['pitch'], color='red', alpha=0.5, linewidth=0)
    axes[6].set_ylabel('pitch [°]')
    
    # add heading
    axes[7].scatter(ds_gps.time, ds_gps.heading, **kwargs)
    axes[7].set_ylabel('head [dir]')
    axes[7].set_ylim([-180, 180])
    axes[7].set_yticks(np.arange(-180, 180+45, 45))
    axes[7].set_yticklabels(yaw_names, fontsize=7)
    
    # add dropsondes
    for ds_name, ds_dsd in dict_ds_dsd.items():
        if 'launch_time' in list(ds_dsd.keys()) and not 'base_time' in list(ds_dsd.keys()):
            ds_dsd = ds_dsd.rename({'launch_time': 'base_time'})
            
        # latitude plot
        axes[0].scatter(ds_dsd.time, ds_dsd.lat, **ds_kwargs)
        axes[0].annotate(ds_name, xy=(ds_dsd.base_time, 0), xycoords=('data', 'axes fraction'), color='k', fontsize=7)
        
        # longitude plot
        axes[1].scatter(ds_dsd.time, ds_dsd.lon, **ds_kwargs)
        axes[1].annotate(ds_name, xy=(ds_dsd.base_time, 0), xycoords=('data', 'axes fraction'), color='k', fontsize=7)

        # altitude plot
        axes[2].scatter(ds_dsd.time, ds_dsd.alt*3.28, **ds_kwargs)
        axes[2].annotate(ds_name, xy=(ds_dsd.base_time, 0), xycoords=('data', 'axes fraction'), color='k', fontsize=7)

    # date axis settings
    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    plt.setp(axes[-1].xaxis.get_majorticklabels(), rotation=30)
    axes[-1].set_xlabel('Time (hh:mm:ss) [UTC]')
    
    # add flight segments as vertical line
    for i_ax, ax in enumerate(axes):
        for flight_segment in flight_segments['segments']:
            
            start = flight_segment['start']
            end = flight_segment['end']

            # workaround for flight segments without a name
            try:
                name = flight_segment['name']
            
            except KeyError:
                name = ', '.join(flight_segment['kinds'])
            
            if start and end:
            
                ax.axvline(start, color='blue', alpha=0.5)
                ax.axvline(end, color='green', alpha=0.5, linestyle='--')
                
                if i_ax == 0:
                    
                    if 'segment_id' in flight_segment.keys():
                        print('plot segment id %s'%flight_segment['segment_id'])
                    else:
                        print('plot segment id ???')
                    
                    ax.annotate('start: '+name, xy=(start, 1), va='bottom', ha='left', xycoords=('data', 'axes fraction'), fontsize=8, rotation=90, color='blue')
                    ax.annotate('end: '+name, xy=(end, 1), va='bottom', ha='right', xycoords=('data', 'axes fraction'), fontsize=8, rotation=90, color='green')
    
            # add parts, if they exist for this flight segment
            if 'parts' in list(flight_segment.keys()):
                            
                for j, part in enumerate(flight_segment['parts']):
                    
                    start = part['start']
                    end = part['end']
                    
                    # workaround for flight segments without a name
                    try:
                        name = part['name']
                    
                    except KeyError:
                        name = ', '.join(part['kinds'])
                    
                    if start and end:
                    
                        ax.axvline(start, color='blue', alpha=0.5)
                        ax.axvline(end, color='green', alpha=0.5, linestyle='--')
                        
                        if i_ax == 0:
                            
                            if 'segment_id' in part.keys():
                                print('plot segment id %s'%part['segment_id'])
                            else:
                                print('plot segment id ???')    
                        
                            ax.annotate('start: '+name, xy=(start, 1), va='bottom', ha='left', xycoords=('data', 'axes fraction'), fontsize=6, rotation=90, color='blue')
                            ax.annotate('end: '+name, xy=(end, 1), va='bottom', ha='right', xycoords=('data', 'axes fraction'), fontsize=6, rotation=90, color='green')
    
    plt.show()

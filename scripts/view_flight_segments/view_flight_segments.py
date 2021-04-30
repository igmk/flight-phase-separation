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
    
    # add places
    lon_n, lat_n = (11.922222, 78.925)     # coordinates Ny Alesund
    lon_l, lat_l = (15.633333, 78.216667)  # coordinates Longyearbyen

    ax.scatter(lon_n, lat_n, marker='o', c='r', s=10, zorder=3, transform=data_crs, edgecolors='none')
    ax.annotate(text='NYA', xy=ax.projection.transform_point(lon_n, lat_n, data_crs))
    ax.scatter(lon_l, lat_l, marker='o', c='r', s=10, zorder=3, transform=data_crs, edgecolors='none')
    ax.annotate(text='LYR', xy=ax.projection.transform_point(lon_l, lat_l, data_crs), va='top', ha='center')
    
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
            ax.annotate(name, xy=ax.projection.transform_point(ds_gps.lon.sel(time=start), ds_gps.lat.sel(time=start), data_crs), va='top', color='k', **kwargs)
            ax.annotate(name, xy=ax.projection.transform_point(ds_gps.lon.sel(time=end), ds_gps.lat.sel(time=end), data_crs), va='bottom', color='gray', **kwargs)
    
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
                    ax.annotate(name, xy=ax.projection.transform_point(ds_gps.lon.sel(time=start), ds_gps.lat.sel(time=start), data_crs), va='top', color='k', **kwargs)
                    ax.annotate(name, xy=ax.projection.transform_point(ds_gps.lon.sel(time=end), ds_gps.lat.sel(time=end), data_crs), va='bottom', color='gray', **kwargs)
            
    #%% plot time series
    print('plot time series')
    
    fig, axes = plt.subplots(8, 1, figsize=(9, 9), sharex=True, constrained_layout=True)
    
    fig.suptitle(flight['campaign']+', '+flight['number']+', '+flight['aircraft']+', '+flight['date'])
    
    kwargs = dict(linewidths=0, c='k', s=1)
    ds_kwargs = dict(linewidths=0, c='r', s=1)
    
    # latitude and longitude
    axes[0].scatter(ds_gps.time, ds_gps.lat, **kwargs)
    axes[0].set_ylabel('lat [°N]')
        
    axes[1].scatter(ds_gps.time, ds_gps.lon, **kwargs)
    axes[1].set_ylabel('lon [°E]')
    
    # flight altitude
    axes[2].scatter(ds_gps.time, ds_gps.alt*3.28, **kwargs)
    axes[2].set_ylabel('alt [ft]')
    
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
    axes[6].set_ylabel('head [dir]')
    axes[6].set_ylim([-180, 180])
    axes[6].set_yticks(np.arange(-180, 180+45, 45))
    axes[6].set_yticklabels(['S', 'SW', 'W', 'NW', 'N', 'NE', 'E', 'SE', 'S'], fontsize=7)
    
    # add sea ice along track
    axes[7].scatter(ds_sic.time, ds_sic.sic, zorder=1, **kwargs)
    axes[7].axhline(y=90, color='gray', zorder=0)
    axes[7].set_ylabel('sea ice [%]')
    axes[7].set_ylim([0, 100])
    
    # add dropsondes
    for ds_name, ds_dsd in dict_ds_dsd.items():
        if flight['campaign'] == 'MOSAiC-ACA':
            ds_dsd = ds_dsd.rename({'launch_time':'base_time'})
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
    
    # %% plot dropsonde profiles
    # fig, ax = plt.subplots(1, 3, figsize=(4, 4), constrained_layout=True, sharey=True)
    
    # for ds_name, ds_dsd in dict_ds_dsd.items():
        
    #     # prepare for plot
    #     ds_dsd_p = xr.Dataset()
    #     ds_dsd_p.coords['pres'] = ds_dsd.pres.values
    #     ds_dsd_p['tdry'] = (('pres'), ds_dsd.tdry.values)
    #     ds_dsd_p['rh'] = (('pres'), ds_dsd.rh.values)
    #     ds_dsd_p['u_wind'] = (('pres'), ds_dsd.u_wind.values)
    #     ds_dsd_p['v_wind'] = (('pres'), ds_dsd.v_wind.values)
        
    #     ds_dsd_p = ds_dsd_p.isel(pres=~np.isnan(ds_dsd_p.pres))
        
    #     if len(ds_dsd_p.pres) > 0:  # plot only if pressure available
            
    #         kwargs = dict(s=3, linewidths=0, label=ds_name)
    #         ax[0].scatter(ds_dsd_p.tdry, ds_dsd_p.pres, **kwargs)
    #         ax[1].scatter(ds_dsd_p.rh, ds_dsd_p.pres, **kwargs)
            
    #         # plot line for windspeed
    #         U = np.sqrt(ds_dsd_p.u_wind.values**2 + ds_dsd_p.v_wind**2)
    #         ax[2].scatter(U, ds_dsd_p.pres, **kwargs)
            
    #         # plot arrow for wind
    #         bins = np.arange(750, 1000, 10)
    #         u = ds_dsd_p.u_wind.sel(pres=bins, method='nearest').values
    #         v = ds_dsd_p.v_wind.sel(pres=bins, method='nearest').values
    #         x = np.sqrt(u**2 + v**2)  #np.ones(len(u))
    #         y = ds_dsd_p.pres.sel(pres=bins, method='nearest').values
    #         ax[2].quiver(x, y, u, v, units='width', scale=100, width=0.005, alpha=0.25) 
    
    # ax[0].set_ylabel('$p$ [hPa]')
    # ax[0].set_ylim([1013.15, 650])
    # ax[0].set_xlabel('$T_{dry}$ [K]')
    # ax[1].set_xlabel('$RH$ [%]')
    # ax[1].set_xlim([0, 100])
    # ax[2].set_xlabel('$U$ [m s$^{-1}$]')
    # ax[2].set_xlim([0, 25])
    
    # lgnd = ax[-1].legend(frameon=False, ncol=1, bbox_to_anchor=(1.1, 0.5), loc='center left')
    # for path in lgnd.legendHandles:
    #     path._sizes = [50]
        
    # %%
    plt.show()

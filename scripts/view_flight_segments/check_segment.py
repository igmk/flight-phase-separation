

import numpy as np
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
from glob import glob
from matplotlib import cm
import xarray as xr
import yaml
import sys


"""
Script to check flight segment

Things that are considered already:
    
    - to be filled out...
"""


class SegmentCatalog:

    # kinds    
    regular = ['high_level', 'large_ascend', 'large_descend', 'low_level',
               'major_ascend', 'major_descend',
               'small_ascend', 'small_descend']
    pattern = ['racetrack_pattern']
    curves = ['short_turn', 'long_turn', 'procedure_turn']

    # names
    no_numbering = ['major ascend', 'major descend', 'short turn', 'long turn', 'procedure turn']
    
    # events
    events = ['joint flight with P6',]  # TODO
    

if __name__ == '__main__':
    
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
    
    # read dropsondes of flight
    files = glob(paths['path_dropsonde']+flight['campaign'].lower()+'/dropsondes/'+flight['date'][:4]+'/'+flight['date'][4:6]+'/'+flight['date'][6:8]+'/*PQC.nc')
    dict_ds_dsd = {}  # dictionary of dropsondes
    for file in files:
        filename = file.split('/')[-1].split('_PQC')[0]
        dict_ds_dsd[filename] = xr.open_dataset(file)
        
    #%% check flight phase separation
    # meta data
    assert flight['number'] == flight_segments['name']
    assert flight['campaign'] == flight_segments['mission']
    assert flight['aircraft'] == flight_segments['platform']
    assert flight_segments['mission']+'_'+flight_segments['platform']+'_'+flight_segments['name'] == flight_segments['flight_id']
    assert type(flight_segments['contacts']) == list
    assert type(flight_segments['date']) == datetime.date
    assert flight_segments['flight_report'] != None
    assert type(flight_segments['takeoff']) == datetime.datetime
    assert type(flight_segments['landing']) == datetime.datetime
    assert type(flight_segments['events']) == list
    assert type(flight_segments['remarks']) == list
    
    # make sure, that events is standardized
    # make sure that remarks is standardized
    
    # flight segments
    segments = flight_segments['segments']
    
    # check if all the required attributes exist
    for segment in segments:

        segment_keys = segment.keys()
        
        # for all segments
        assert 'kinds' in segment_keys
        assert 'name' in segment_keys
        assert 'start' in segment_keys
        assert 'end' in segment_keys
        
        is_turn = np.any([kind in SegmentCatalog.curves for kind in segment['kinds']])
        
        if not is_turn:
            
            assert 'irregularities' in segment_keys
            assert 'segment_id' in segment_keys
            assert 'levels' in segment_keys
            assert 'dropsondes' in segment_keys
            
            if 'parts' in segment_keys:
                assert len(segment_keys) == 9
            else:
                assert len(segment_keys) == 8
            
        else:
            
            assert len(segment_keys) == 4
    
    # check if underscore is in name
    name_lst = np.sort([segment['name'] for segment in segments])
    for name in name_lst:
        assert '_' not in name
        
    # check if numbering is correct: consecutive for same segment, starting from 1 for new segment name
    name_before = ''
    number_before = 0
    for name in name_lst:
        
        if name[-1].isdigit():
            
            number = int(name.split(' ')[-1])
            name = ' '.join(name.split(' ')[:-1])
            
            if name == name_before:
                assert number == number_before + 1
            
            else:
                assert number == 1
                
            number_before = number
            name_before = name
        
        else:
            assert name in SegmentCatalog.no_numbering
    
    # check if kinds are available ones
    kinds_lst = [segment['kinds'] for segment in segments]
    for kinds in kinds_lst:
        for kind in kinds:
            assert ' ' not in kind
        
    assert 'major_ascend' in kinds_lst[0]
    assert 'major_descend' in kinds_lst[-1]
    
    # consistency of times    
    start_lst = [segment['start'] for segment in segments]
    end_lst = [segment['end'] for segment in segments]
    
    # landing and takeoff
    assert start_lst[0] == flight_segments['takeoff']
    assert end_lst[-1] == flight_segments['landing']

    # consecutive start and end times
    for t_start, t_end in zip(start_lst[1:], end_lst[:-1]):
        if t_start != t_end:
            print(t0, t1)
            assert t_start == t_end
    
    # consecutive start and end times within parts
    # TODO



import numpy as np
import datetime
from glob import glob
import xarray as xr
import re
import yaml


"""
Script to check flight segment

Things that are considered already:
    
    - to be filled out...
"""


def name_numbering(name_lst):
    """
    Checks the name attributes of a flight
    
    name_lst: list of all the names within one flight, does not have to be sorted
    """
    
    # check if underscore is in name
    convert = lambda text: int(text) if text.isdigit() else text.lower() 
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    name_lst = sorted(name_lst, key=alphanum_key)

    for name in name_lst:
        assert '_' not in name, 'found _ in name attribute "{}"'.format(name)
        
    # check if numbering is correct: consecutive for same segment, starting from 1 for new segment name
    name_before = ''
    number_before = 0
    for name in name_lst:
        
        if name[-1].isdigit():
            
            number = int(name.split(' ')[-1])
            name_no_number = ' '.join(name.split(' ')[:-1])
            
            if name_no_number == name_before:
                assert number == number_before + 1, 'number in name attribute "{}" should be {}'.format(name, number_before + 1)
            
            else:
                assert number == 1, 'number in name attribute "{}" should be {}'.format(name, 1)
                
            number_before = number
            name_before = name_no_number
        
        else:
            assert name in SegmentCatalog.no_numbering, 'attribute "name" should have a number: "{}"'.format(name)


class SegmentCatalog:

    # kinds
    regular = ['high_level',
               'mid_level',
               'low_level',
               'large_ascend',
               'large_descend',
               'major_ascend',
               'major_descend',
               'small_ascend',
               'small_descend',
               'medium_ascend',
               'medium_descend',
               'profiling',
               'noseboom_pattern',
               'holding_pattern',
               'p6_co-location',
               'nya_overflight',
               'sveabreen_glacier_overflight',
               'a-train_underflight',
               'polarstern_overflight',
               'cloudsat_calipso_underflight',
               ]
    
    curves = ['short_turn',
              'long_turn',
              'procedure_turn',
              'waiting_pattern',
              'deicing_leg',
              'cross_pattern_turn',
              'long_legs_pattern_turn',
              'circle',
              ]
    
    pattern = ['racetrack_pattern',
               'stairstep_pattern',
               'cross_pattern',
               'sawtooth_pattern',
               'radiation_square',
               'holding_pattern',
               ]
    
    # parts
    # the kinds should also be from the above's kinds
    # the name and segment_id then indicate that it belongs to a pattern
    # TODO: also, check if we need mid_ascend, when levels[1]-levels[0] between 1000 and 2000 m? same for descend?
    # TODO: then a routine that systematically checks the ascend and descend kinds and also adds it to turns, if they are also ascend or descend
    parts = {'racetrack_pattern': ['low_level',
                                   'mid_level',
                                   'high_level',
                                   'procedure_turn',
                                   ], 
             
             'stairstep_pattern': ['small_ascend',
                                   'medium_ascend',
                                   'large_ascend',
                                   'small_descend',
                                   'medium_descend',
                                   'large_descend',
                                   'low_level',
                                   'mid_level',
                                   'high_level',
                                   ],
             
             'cross_pattern': ['high_level',
                               'cross_pattern_turn'
                               ],
             
             'sawtooth_pattern': ['small_ascend',
                                  'medium_ascend',
                                  'large_ascend',
                                  'small_descend',
                                  'medium_descend',
                                  'large_descend',
                                  'low_level',
                                  'mid_level',
                                  'high_level'
                                  ],
             
             'radiation_square': ['short_turn',
                                  'high_level', 
                                  ],
             
             'holding_pattern': ['high_level',
                                 'short_turn',
                                 'circle'],
             }
    
    # name examle for racetrack low_level: racetrack 1 leg 1 
    
    # names
    no_numbering = ['major ascend',
                    'major descend',
                    'short turn',
                    'long turn',
                    'procedure turn',
                    'waiting pattern',
                    'deicing leg',  # nicht als eigenes leg, aber irregularities und dann mid_level ode rhigh_level
                    'cross pattern turn',
                    'long legs pattern turn',
                    'circle',
                    ]
    
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
    for i, segment in enumerate(segments):

        segment_keys = segment.keys()
        
        # for all segments
        assert 'kinds' in segment_keys, 'attribute "kinds" is missing in segment {}'.format(segments[i])
        assert 'name' in segment_keys, 'attribute "name" is missing in segment {}'.format(segments[i])
        assert 'start' in segment_keys, 'attribute "start" is missing in segment {}'.format(segments[i])
        assert 'end' in segment_keys, 'attribute "end" is missing in segment {}'.format(segments[i])
        
        is_turn = np.all([kind in SegmentCatalog.curves for kind in segment['kinds']])
        
        if not is_turn:
            
            assert 'irregularities' in segment_keys, 'attribute "irregularities" is missing in segment {}'.format(segments[i])
            assert 'segment_id' in segment_keys, 'attribute "segment_id" is missing in segment {}'.format(segments[i])
            assert 'levels' in segment_keys, 'attribute "levels" is missing in segment {}'.format(segments[i])
            assert 'dropsondes' in segment_keys, 'attribute "dropsondes" is missing in segment {}'.format(segments[i])
            
            if segment['kinds'][0] in SegmentCatalog.pattern:
                
                assert 'parts' in segment_keys, 'attribute "parts" is missing in segment {}'.format(segments[i])
                assert len(segment_keys) == 9, 'number of attributes should be 9 in segment {}'.format(segments[i])
                
            else:
                
                assert len(segment_keys) == 8, 'number of attributes should be 8 in segment {}'.format(segments[i])
            
        else:
            
            assert len(segment_keys) == 4, 'number of attributes should be 4 in segment {}'.format(segments[i])
    
    #%% kinds labels 
    kinds_lst = [segment['kinds'] for segment in segments]
    for kinds in kinds_lst:
        for kind in kinds:
            assert ' ' not in kind, '" " found in attribute "kinds" {}'.format(kind)
            
            assert kind in SegmentCatalog.pattern or kind in SegmentCatalog.curves or kind in SegmentCatalog.regular, 'element "{}" in "kinds" list not available. Please correct it or add the kind to the SegmentCatalog class'.format(kind)
        
    assert 'major_ascend' in kinds_lst[0], '"major_ascend" is not the first segment'
    assert 'major_descend' in kinds_lst[-1], '"major_descend" is not the last segment'
    
    #%% name
    name_lst = [segment['name'] for segment in segments]
    parts_name_lst = [part['name'] for segment in segments for kind in segment['kinds'] if kind in SegmentCatalog.pattern for part in segment['parts']]
    
    name_lst = name_lst + parts_name_lst
    
    name_numbering(name_lst)
    name_numbering(name_lst)

    #%% levels
    levels_lst = [segment['levels'] for segment in segments for kind in segment['kinds'] if kind in SegmentCatalog.pattern or kind in SegmentCatalog.regular]
    
    for levels in levels_lst:
        assert type(levels) == list, '"levels" is not a list: {}'.format(levels)
        assert len(levels) > 0, 'one or more "levels" are empty: {}'.format(levels_lst)
    
    # check levels of high_level, mid_level and low_level
    test_kinds_h = ['high_level', 'mid_level', 'low_level']

    def segment_horizontal(level):
        if level / 3.821 > 2000: return 'high_level'
        elif level / 3.821 > 1000: return 'mid_level'
        elif level / 3.821 > 0: return 'low_level'
        else: return 'input level not a number greater than 0'
    
    for segment in segments:
        if len(set.intersection(set(segment['kinds']), set(test_kinds_h))):
            kind = list(set.intersection(set(test_kinds_h), set(segment['kinds'])))[0]
            assert len(segment['levels']) == 1, 'Number of levels of segment id "{}" should be 1'.format(segment['segment_id'])
            assert segment_horizontal(segment['levels'][0]) == kind, '{} segment segment id "{}" is actually "{}"'.format(kind, segment['segment_id'], segment_horizontal(segment['levels'][0]))
            
    # check levels of ascends and descends
    test_kinds_v = ['small_ascend', 'medium_ascend', 'large_ascend', 'small_descend', 'medium_descend', 'large_descend']
    
    def segment_vertical(level):
        if level[1]/3.821 - level[0]/3.821 > 2000: return 'large_ascend'
        elif level[1]/3.821 - level[0]/3.821 > 1000: return 'medium_ascend'
        elif level[1]/3.821 - level[0]/3.821 > 0: return 'small_ascend'
        elif level[1]/3.821 - level[0]/3.821 > -1000: return 'small_descend'
        elif level[1]/3.821 - level[0]/3.821 > -2000: return 'medium_descend'
        elif level[1]/3.821 - level[0]/3.821 <= -2000: return 'large_descend'
        else: return 'input level can not be classified as ascend or descend'
    
    for segment in segments:
        if len(set.intersection(set(segment['kinds']), set(test_kinds_v))):
            kind = list(set.intersection(set(test_kinds_v), set(segment['kinds'])))[0]
            assert len(segment['levels']) == 2, 'Number of levels of segment id "{}" should be 2'.format(segment['segment_id'])
            assert segment_vertical(segment['levels']) == kind, '{} segment segment id "{}" is actually "{}"'.format(kind, segment['segment_id'], segment_vertical(segment['levels']))
    
    #%% consistence of times    
    # 1: segments
    start_lst = [segment['start'] for segment in segments]
    end_lst = [segment['end'] for segment in segments]
    
    # landing and takeoff
    assert start_lst[0] == flight_segments['takeoff'], 'start time of first segment is not equal to takeoff time'
    assert end_lst[-1] == flight_segments['landing'], 'end time of last segment is not equal to landing time'

    # consecutive start and end times
    for t_start, t_end in zip(start_lst[1:], end_lst[:-1]):
        if t_start != t_end:
            assert t_start == t_end, 'start and end times are not matching: {}, {}'.format(t_start, t_end)
    
    # 2: parts
    for segment in segments:
        for kind in segment['kinds']:
            if kind in SegmentCatalog.pattern:
                
                start_lst = [part['start'] for part in segment['parts']]
                end_lst = [part['end'] for part in segment['parts']]
                
                # start and end of pattern
                assert start_lst[0] == segment['start'], 'start time of first part is not equal to start time of pattern: {}, {}'.format(t_start, t_end)
                assert end_lst[-1] == segment['end'], 'end time of last part is not equal to end time of pattern: {}, {}'.format(t_start, t_end)
            
                # consecutive start and end times
                for t_start, t_end in zip(start_lst[1:], end_lst[:-1]):
                    if t_start != t_end:
                        print(t_start, t_end)
                        assert t_start == t_end, 'start and end times are not matching: {}, {}'.format(t_start, t_end)

    # print irregularities of flight
    print('Irregularities of segments')
    for segment in segments:
        print(segment.get('irregularities'))
    

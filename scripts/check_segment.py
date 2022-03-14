

import numpy as np
import datetime
from glob import glob
import xarray as xr
import re
import yaml
from glob import glob


"""
Script to check flight segmentation
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
               'large_ascent',
               'large_descent',
               'major_ascent',
               'major_descent',
               'small_ascent',
               'small_descent',
               'medium_ascent',
               'medium_descent',
               'profiling',
               'p6_co-location',
               'p5_co-location',
               'nya_overflight',
               'sveabreen_glacier_overflight',
               'a-train_underflight',
               'polarstern_overflight',
               'noseboom_calibration',
               'radiometer_calibration',
               'instrument_testing',
               ]
    
    curves = ['short_turn',
              'long_turn',
              'procedure_turn',
              'cross_pattern_turn',
              'circle',
              ]
    
    pattern = ['racetrack_pattern',
               'stairstep_pattern',
               'cross_pattern',
               'sawtooth_pattern',
               'radiation_square',
               'holding_pattern',
               'noseboom_calibration_pattern',
               ]
    
    # parts
    parts = {'racetrack_pattern': ['low_level',
                                   'mid_level',
                                   'high_level',
                                   'procedure_turn',
                                   'short_turn',
                                   'small_ascent',
                                   'small_descent',
                                   'large_descent',
                                   'medium_descent',
                                   'medium_ascent',
                                   'profiling',
                                   'large_ascent'
                                   ], 
             
             'stairstep_pattern': ['small_ascent',
                                   'medium_ascent',
                                   'large_ascent',
                                   'small_descent',
                                   'medium_descent',
                                   'large_descent',
                                   'low_level',
                                   'mid_level',
                                   'high_level',
                                   ],
             
             'cross_pattern': ['high_level',
                               'low_level',
                               'cross_pattern_turn',
                               'procedure_turn',
                               ],
             
             'sawtooth_pattern': ['small_ascent',
                                  'medium_ascent',
                                  'large_ascent',
                                  'small_descent',
                                  'medium_descent',
                                  'large_descent',
                                  'low_level',
                                  'mid_level',
                                  'high_level'
                                  ],
             
             'radiation_square': ['short_turn',
                                  'high_level', 
                                  ],
             
             'holding_pattern': ['high_level',
                                 'short_turn',
                                 'long_turn',
                                 'circle',
                                 ],
             
             'noseboom_calibration_pattern': ['high_level', 
                                              'short_turn',
                                              ],
             }
    
    # names
    regular_name = ['high level',
                    'mid level',
                    'low level',
                    'large ascent',
                    'large descent',
                    'major ascent',
                    'major descent',
                    'small ascent',
                    'small descent',
                    'medium ascent',
                    'medium descent',
                    'instrument testing',
                    ]
    
    curves_name = ['short turn',
                   'long turn',
                   'procedure turn',
                   'waiting pattern',
                   'cross pattern turn',
                   'circle',
                   ]
    
    pattern_name = ['racetrack pattern',
                    'stairstep pattern',
                    'cross pattern',
                    'sawtooth pattern',
                    'radiation square',
                    'holding pattern',
                    'noseboom calibration pattern',
                    ]
    
    # parts names
    parts_name = {'racetrack_pattern': ['racetrack pattern {} leg {}',
                                        'procedure turn',
                                        'short turn',  
                                       ], 
                 
                 'stairstep_pattern': ['stairstep pattern {} ascent {}',
                                       'stairstep pattern {} descent {}',
                                       'stairstep pattern {} leg {}',
                                       ],
                 
                 'cross_pattern': ['cross pattern {} ascent {}',
                                   'cross pattern turn', 
                                   'procedure turn',
                                   ],
                 
                 'sawtooth_pattern': ['sawtooth pattern {} ascent {}',
                                      'sawtooth pattern {} descent {}',
                                      'sawtooth pattern {} high level {}',
                                      'sawtooth pattern {} mid level {}',
                                      'sawtooth pattern {} low level {}',
                                      ],
                 
                 'radiation_square': ['radiation square {} leg {}',
                                      'short turn'
                                      ],
                 
                 'holding_pattern': ['holding pattern {} leg {}',
                                     'short turn',
                                     'circle',
                                     ],
                 
                 'noseboom_calibration_pattern': ['noseboom calibration pattern {} leg {}', 
                                                  'short turn',
                                                  ],
                 }
    
    no_numbering = ['major ascent',
                    'major descent',
                    'short turn',
                    'long turn',
                    'procedure turn',
                    'waiting pattern',
                    'cross pattern turn',
                    'long legs pattern turn',
                    'circle',
                    'instrument testing',
                    ]
    
    # short names (used in segment_id)
    short_names = {'high level': 'hl',
                   'mid level': 'ml',
                   'low level': 'll',
                   'large ascent': 'la',
                   'large descent': 'ld',
                   'major ascent': 'ma',
                   'major descent': 'md',
                   'small ascent': 'sa',
                   'small descent': 'sd',
                   'medium ascent': 'ma',
                   'medium descent': 'md',
                   'noseboom calibration': 'nc',
                   'instrument testing': 'it',
                   'racetrack pattern': 'rt',
                   'stairstep pattern': 'ss',
                   'cross pattern': 'cr',
                   'sawtooth pattern': 'st',
                   'radiation square': 'rs',
                   'holding pattern': 'ho',
                   'noseboom calibration pattern': 'np',
                   
                   # only used in parts
                   'ascent': 'a',
                   'descent': 'd',
                   'leg': 'l'
                   }
    
    # events
    events = ['A-train underflight',
              'Certification flight (PMS instruments)',
              'Test flight',
              #'Test of instrumentation',  # Test flight in LYR
              #'Joint test flight with P6',
              'Instrument intercomparison between P5 and P6',

              'Colocation with P6 at Polarstern',
              'Joint flight between P5 and P6',
              
              'Ny-Alesund overflight',
              'Ny-Alesund overflight with cross pattern',
              
              'Polarstern overflight',
              'Polarstern overflight with racetrack pattern',
              'Polarstern overflight with cross pattern',
              
              'Racetrack pattern over open ocean',
              'Racetrack pattern over sea ice',
              
              'Stairstep pattern over sea ice',
              'Stairstep pattern over sea ice and open ocean',
              'Stairstep pattern over open ocean',
              
              'Sawtooth pattern with low-level legs',

              'Radiation square pattern',
              
              'Radiometer calibration',
              'Noseboom calibration',  # == Calibration of 5-hole probe
              'EAGLE/HAWK calibration',
              'AIMMS-20 calibration',
              ]
    
    # remarks
    remarks = [
               # on instruments
               'AMALi pointing zenith', 
               'Dropsonde system was not working',
               'EAGLE/HAWK showed some problems due to a broken cable',
               'MiRAC not working',
               'SMART connection was sometimes interrupted', 
               'SMART not working',
               'Heading in GPS/INS dataset missing',
               'Two power outages of 230 V in beginning during transfer to first satellite meeting',

               # on the segmentation
               'No segmentation apart from instrument_testing segment performed',
               
               # on atmopsheric situation
               'Cloud field spreading into the MIZ and migrating into surface based fog over closed sea ice',
               'Clouds above open water and sea ice',
               'Clouds along wind over ice and over sea', 
               'Low clouds in warm air over sea ice',
               'Low-level clouds over sea ice weak cold air', 
               'Cold air outbreak over sea ice and at the MIZ',
               'Cold air outbreak with thin clouds over sea ice',
               'Mid-Level stratocumulus over sea ice',
               'Sharp cloud edge over homogeneous sea ice', 
               'Thin low level clouds over sea ice',
               'Warm front pushing clouds in the MIZ along steady increasing sea ice concentration',
               'Cloud-free areas over closed sea ice',
               'Low- and mid-level clouds of a cold air outbreak',
               'Mostly clear-sky with some thin cirrus clouds',
               'Thin broken clouds over sea ice', 
               'Thin low- and mid-level clouds',
               'Thin low clouds over sea ice',
               'Cloud-free area north of Svalbard',

               # icing conditions
               'Icing problems',
               
               # dropsondes (find better solution)
               'Dropsondes failed at 16:18 UTC, 16:24 UTC',
               'Dropsonde failed at 09:34 UTC',
               ]


def main(flight, meta):
    """Main routine"""
    
    print('Checking flight', flight)
    
    # meta data
    assert flight['name'] == meta['name']
    assert flight['mission'] == meta['mission']
    assert flight['platform'] == meta['platform']
    assert meta['mission']+'_'+meta['platform']+'_'+meta['name'] == meta['flight_id']
    assert type(meta['contacts']) == list
    assert type(meta['date']) == datetime.date
    assert meta['flight_report'] != None
    assert type(meta['takeoff']) == datetime.datetime
    assert type(meta['landing']) == datetime.datetime
    assert type(meta['events']) == list
    assert type(meta['remarks']) == list
    
    # make sure, that events is standardized
    for event in meta['events']:
        assert event in SegmentCatalog.events, 'Event "{}" not from list of possible events: {}'.format(event, SegmentCatalog.events)
    
    # make sure that remarks is standardized
    for remark in meta['remarks']:
        assert remark in SegmentCatalog.remarks, 'Remark "{}" not from list of possible remarks: {}'.format(remark, SegmentCatalog.remarks)
        
    # flight segments
    segments = meta['segments']
    
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
    
    # kinds labels 
    kinds_lst = [segment['kinds'] for segment in segments]
    for kinds in kinds_lst:
        for kind in kinds:
            assert ' ' not in kind, '" " found in attribute "kinds" {}'.format(kind)
            
            assert kind in SegmentCatalog.pattern or kind in SegmentCatalog.curves or kind in SegmentCatalog.regular, 'element "{}" in "kinds" list not available. Please correct it or add the kind to the SegmentCatalog class'.format(kind)
        
    assert 'major_ascent' in kinds_lst[0], '"major_ascent" is not the first segment'
    assert 'major_descent' in kinds_lst[-1], '"major_descent" is not the last segment'
    
    # kinds labels of parts
    for segment in segments:
        for kind in segment['kinds']:
            if kind in SegmentCatalog.pattern:
                for part in segment['parts']:
                    for part_kind in part['kinds']:
                        assert part_kind in SegmentCatalog.parts[kind], 'part of kind "{}" from pattern of kind "{}" not from list: {}'.format(part_kind, kind, SegmentCatalog.parts[kind])
    
    # name
    name_lst = [segment['name'] for segment in segments]
    parts_name_lst = [part['name'] for segment in segments for kind in segment['kinds'] if kind in SegmentCatalog.pattern for part in segment['parts']]
    
    # check numbering
    name_numbering(name_lst)
    name_numbering(parts_name_lst)
    
    # check names of parts
    for segment in segments:
        if segment.get('parts') is not None:
                        
            for part in segment['parts']:
                
                is_turn = np.all([kind in SegmentCatalog.curves for kind in part['kinds']])
                if not is_turn:
                    
                    assert segment['name'] in part['name'], 'name of part with name "{}" should be similar to one of these: {}'.format(part['name'], SegmentCatalog.parts_name[segment['kinds'][0]])
                    
                    if 'sawtooth pattern' in segment['name'] or 'stairstep pattern' in segment['name']:
                        
                        end_name = ' '.join(part['name'].split(segment['name'])[-1].split(' ')[1:-1])
                        true_name = ['ascent', 'descent', 'low level', 'mid level', 'high level']
                        assert end_name in true_name, 'part with segment_id "{}" with name "{}" is not equal to one of these possible names {}'.format(part['segment_id'], end_name, true_name)
                    
    # check segment id's
    for segment in segments:
        
        is_turn = np.all([kind in SegmentCatalog.curves for kind in segment['kinds']])
        
        segment_name_no_number = ' '.join([i for i in segment['name'].split(' ') if not i.isdigit()])
        
        if not is_turn and segment_name_no_number not in SegmentCatalog.no_numbering:
            
            for s in segment['name'].split():
                if s.isdigit():
                    n = int(s)
            
            # get short name
            short_name = SegmentCatalog.short_names[segment_name_no_number]
                        
            segment_id_true = meta['mission'] + '_' + meta['platform'] + '_' + meta['name'] + '_' + short_name + str(n).zfill(2)
            
            assert segment['segment_id'] == segment_id_true, 'segment_id "{}" should be "{}"'.format(segment['segment_id'], segment_id_true)
            
        elif not is_turn and segment_name_no_number in SegmentCatalog.no_numbering:
            
            # get short name
            short_name = SegmentCatalog.short_names[segment['name']]
                        
            segment_id_true = meta['mission'] + '_' + meta['platform'] + '_' + meta['name'] + '_' + short_name
            
            assert segment['segment_id'] == segment_id_true, 'segment_id "{}" should be "{}"'.format(segment['segment_id'], segment_id_true)
    
        # for parts
        if segment.get('parts') is not None:
            
            for part in segment['parts']:
                
                is_turn = np.all([kind in SegmentCatalog.curves for kind in part['kinds']])
            
                if not is_turn:
                    
                    # get name of part without the pattern name in from
                    part_name = part['name'].split(segment['name']+' ')[-1]
                    part_name_no_number = ' '.join([i for i in part_name.split(' ') if not i.isdigit()])
                    short_name = SegmentCatalog.short_names[part_name_no_number]
                    
                    if part_name_no_number not in SegmentCatalog.no_numbering:
                        
                        for s in part_name.split():
                            if s.isdigit():
                                n = int(s)
    
                        part_id_true = segment_id_true + '_' + short_name + str(n).zfill(2)
                            
                    elif part_name_no_number in SegmentCatalog.no_numbering:
                        
                        part_id_true = segment_id_true + '_' + short_name
                        
                    assert part['segment_id'] == part_id_true, 'segment_id "{}" should be "{}"'.format(part['segment_id'], part_id_true)
        
    # consistence of times    
    # 1: segments
    start_lst = [segment['start'] for segment in segments]
    end_lst = [segment['end'] for segment in segments]
    
    # landing and takeoff
    assert start_lst[0] == meta['takeoff'], 'start time of first segment is not equal to takeoff time'
    assert end_lst[-1] == meta['landing'], 'end time of last segment is not equal to landing time'

    # consecutive start and end times
    for t_start, t_end in zip(start_lst[1:], end_lst[:-1]):
        assert t_start == (t_end + datetime.timedelta(seconds=1)), 'start and end times are not matching: {}, {}'.format(
            t_start, t_end + datetime.timedelta(seconds=1))
    
    # 2: parts
    for segment in segments:
        for kind in segment['kinds']:
            if kind in SegmentCatalog.pattern:
                
                start_lst = [part['start'] for part in segment['parts']]
                end_lst = [part['end'] for part in segment['parts']]
                
                # start and end of pattern
                assert start_lst[0] == segment['start'], 'start time of first part is not equal to start time of pattern: {}, {}'.format(start_lst[0], segment['start'])
                assert end_lst[-1] == segment['end'], 'end time of last part is not equal to end time of pattern: {}, {}'.format(end_lst[-1], segment['end'])
            
                # consecutive start and end times
                for t_start, t_end in zip(start_lst[1:], end_lst[:-1]):
                    assert t_start == (t_end+ datetime.timedelta(seconds=1)), 'start and end times are not matching: {}, {}'.format(
                        t_start, t_end + datetime.timedelta(seconds=1))

    # levels
    levels_lst = [segment['levels'] for segment in segments for kind in segment['kinds'] if kind in SegmentCatalog.pattern or kind in SegmentCatalog.regular]
    
    # append levels from parts which are not only curves
    for segment in segments:
        for kind in segment['kinds']:
            if kind in SegmentCatalog.pattern:
                for part in segment['parts']:
                    for kind_part in part['kinds']:
                        if kind_part in SegmentCatalog.regular:
                            assert part.get('levels') is not None, 'Part {} should contain key word "levels"'.format(part['segment_id'])
                            levels_lst.append(part['levels'])
    
    for levels in levels_lst:
        assert type(levels) == list, '"levels" is not a list: {}'.format(levels)
        assert len(levels) > 0, 'one or more "levels" are empty: {}'.format(levels_lst)
    
    # check levels of high_level, mid_level and low_level
    test_kinds_h = ['high_level', 'mid_level', 'low_level']

    def segment_horizontal(level):
        if level / 3.281 > 2000: return 'high_level'
        elif level / 3.281 > 1000: return 'mid_level'
        elif level / 3.281 > 0: return 'low_level'
        else: return 'input level not a number greater than 0'
    
    for segment in segments:
        if len(set.intersection(set(segment['kinds']), set(test_kinds_h))):
            kind = list(set.intersection(set(test_kinds_h), set(segment['kinds'])))[0]
            assert len(segment['levels']) == 1, 'Number of levels of segment id "{}" should be 1'.format(segment['segment_id'])
            assert segment_horizontal(segment['levels'][0]) == kind, '{} kind with segment id "{}" is actually "{}"'.format(kind, segment['segment_id'], segment_horizontal(segment['levels'][0]))
            
        if segment.get('parts') is not None:
            for part in segment['parts']:
                if len(set.intersection(set(part['kinds']), set(test_kinds_h))):
                    kind = list(set.intersection(set(test_kinds_h), set(part['kinds'])))[0]
                    assert len(part['levels']) == 1, 'Number of levels of segment id "{}" should be 1'.format(part['segment_id'])
                    assert segment_horizontal(part['levels'][0]) == kind, '{} kind with segment id "{}" is actually "{}"'.format(kind, part['segment_id'], segment_horizontal(part['levels'][0]))
    
    # check levels of ascents and descents
    test_kinds_v = ['small_ascent', 'medium_ascent', 'large_ascent', 'small_descent', 'medium_descent', 'large_descent']
    
    def segment_vertical(level):
        if level[1]/3.281 - level[0]/3.281 > 2000: return 'large_ascent'
        elif level[1]/3.281 - level[0]/3.281 > 1000: return 'medium_ascent'
        elif level[1]/3.281 - level[0]/3.281 > 0: return 'small_ascent'
        elif level[1]/3.281 - level[0]/3.281 > -1000: return 'small_descent'
        elif level[1]/3.281 - level[0]/3.281 > -2000: return 'medium_descent'
        elif level[1]/3.281 - level[0]/3.281 <= -2000: return 'large_descent'
        else: return 'input level can not be classified as ascent or descent'
    
    for segment in segments:
        if len(set.intersection(set(segment['kinds']), set(test_kinds_v))):
            kind = list(set.intersection(set(test_kinds_v), set(segment['kinds'])))[0]
            assert len(segment['levels']) == 2, 'Number of levels of segment id "{}" should be 2'.format(segment['segment_id'])
            assert segment_vertical(segment['levels']) == kind, '{} kind with segment id "{}" is actually "{}"'.format(kind, segment['segment_id'], segment_vertical(segment['levels']))
        
        if segment.get('parts') is not None:
            for part in segment['parts']:
                if len(set.intersection(set(part['kinds']), set(test_kinds_v))):
                    kind = list(set.intersection(set(test_kinds_v), set(part['kinds'])))[0]
                    assert len(part['levels']) == 2, 'Number of levels of segment id "{}" should be 2'.format(part['segment_id'])
                    assert segment_vertical(part['levels']) == kind, '{} kind with segment id "{}" is actually "{}"'.format(kind, part['segment_id'], segment_vertical(part['levels']))
            
    print('No errors found in yaml file')


if __name__ == '__main__':
    
    check_single = True
    
    # read file with paths (set wdir to the current script location)
    with open('paths.yaml') as f:
        paths = yaml.safe_load(f)
    
    if check_single:
    
        # read file with flight settings
        with open('flight_settings.yaml') as f:
            flight = yaml.safe_load(f)

        # read flight segments of flight
        file = '../flight_phase_files/'+flight['mission']+'/'+flight['platform']+'/'+flight['mission']+'_'+flight['platform']+'_Flight-Segments_'+flight['date']+'_'+flight['name']+'.yaml'
        with open(file, 'r') as f:
            meta = yaml.safe_load(f)
        
        main(flight, meta)

    else:
        
        files = glob('../../flight_phase_files/*/*/*.yaml')
        
        for file in files:
            
            with open(file, 'r') as f:
                meta = yaml.safe_load(f)
                
            # extract flight info from filename
            info = file.split('/')[-1].split('.yaml')[0].split('_')
            flight = {'campaign': info[0], 
                      'number': info[4], 
                      'aircraft': info[1], 
                      'date': info[3]}
            
            main(flight, meta)
            

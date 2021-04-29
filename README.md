# flight-phase-separation

The idea behind floght phase separation is to be able to select segments of flights according to their properties. The selection can be done by attributes like names and further on levels and is applied to the platform and instrument data by using start and end datetime objects belonging to the segment.

## Flight segments
### Keyword: kinds
This table provides an overview of the keywords used to describe the flight segments. Multiple keywords can be used for one flight segment.

#### ascends and descends
| kinds           | description                                                              |
| --------------- | ------------------------------------------------------------------------ |
| major_ascend    | takeoff from the airport until a constant flight level is reached        |
| major_descend   | last descend from a constant flight level befor landing at the airport   |
| small_ascend    | ascend of less than 1 km height difference between start and end times   |
| small_descend   | descend of less than 1 km height difference between start and end times  |
| large_ascend    | ascend of more than 1 km height difference between start and end times   |
| large_descend   | descend of more than 1 km height difference between start and end times  |
| profiling       | ascend or descend with vertical speed mostly between 5-10 m/s            |

#### flight altitude
| kinds         | description                                     |
| ------------- | ----------------------------------------------- |
| low_level     | constant flight level at < 1 km altitude        |
| mid_level     | constant flight level at 1-2 km altitude        |
| high_level    | constant flight level at > 2 km altitude        |

#### overflights and underflights
| kinds               | description                                                                                         |
| ------------------- | --------------------------------------------------------------------------------------------------- |
| nya_overflight      | Overflight over the Ny-Alesund research station. Might be combined or together with *cross_pattern* |
| ps_overflight       | Overflight over the Ny-Alesund research station. Might be combined or together with *cross_pattern* |
| a-train_underflight | test        |

#### pattern

Pattern usually consist of parts like legs and turns named accordingly. 
| kinds                 |                                                                                                                                  |
| ----------------------|----------------------------------------------------------------------------------------------------------------------------------|
| cross_pattern         | rectangular crosses with transfer legs in between. Usually flown over Ny-Alesund, Polarstern, or once over Longyearbyen airport. | 
| racetrack_pattern     | |
| holding_pattern       | |
| staircase_pattern     | |
| sawtooth_pattern      | |

#### turn
| kinds          |             |
|----------------|-------------|
| short_turn     |             |
| long_turn      |             |
| procedure_turn |             |

This table is just a template!

## Updating *all_flights.yaml*
When creating new or updated flight segment files, a new tag with a new veriosn number needs to be created and pushed to kick of the generation of the *all_flights.yaml*.

```
git add .
git commmit
git tag v0.1.2
git push --tags
```

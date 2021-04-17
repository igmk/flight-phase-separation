# flight-phase-separation

We still try to include a github action to compile all yamls into one single file.

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

#### overflights


# flight-phase-separation

The idea behind flight phase separation is to be able to select segments of flights according to their properties. The selection can be done by attributes like names and further on levels and is applied to the platform and instrument data by using start and end datetime objects belonging to the segment.


A description of the flight segments together with illustrations and code examples can be found in the [pyac3airborne book](https://igmk.github.io/pyac3airborne_book/flight_tracks.html).

## Updating *all_flights.yaml*
When creating new or updated flight segment files, a new tag with a new version number needs to be created and pushed to kick off the generation of the *all_flights.yaml*.

```
git add .
git commmit
git tag v0.1.2
git push --tags
```

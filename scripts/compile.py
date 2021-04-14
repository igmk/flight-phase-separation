import sys
import yaml
from collections import defaultdict


def _main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("infiles", type=str, nargs="+")
    parser.add_argument("-o", "--outfile", type=str)

    args = parser.parse_args()

    all_flights = defaultdict(dict)

    for filename in args.infiles:
        with open(filename) as f:
            flight = yaml.load(f, Loader=yaml.SafeLoader)
        all_flights[flight["platform"]][flight["flight_id"]] = flight

    if args.outfile:
        outfile = open(args.outfile, "w")
    else:
        outfile = sys.stdout

    yaml.dump(dict(all_flights.items()), outfile)

    return 0


if __name__ == "__main__":
    exit(_main())

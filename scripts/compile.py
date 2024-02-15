import sys
import yaml
from collections import defaultdict
import re


campaigns = ['ACLOUD','PAMARCMiP','AFLUX','MOSAiC-ACA','HALO-AC3','HAMAG']

def _main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("infiles", type=str, nargs="+")
    parser.add_argument("-o", "--outfile", type=str)

    args = parser.parse_args()


    all_campaigns = dict()

    for campaign in campaigns:
        all_flights = defaultdict(dict)
        print(campaign)
        r = re.compile(campaign)
        for filename in [fl for fl in args.infiles if r.search(fl)]:
            print(filename)
            with open(filename) as f:
                flight = yaml.load(f, Loader=yaml.SafeLoader)
            all_flights[flight["platform"]][flight["flight_id"]] = flight

        if args.outfile:
            outfile = open(args.outfile, "w")
        else:
            outfile = sys.stdout

        all_campaigns[campaign] = dict(all_flights.items())

    yaml.dump(all_campaigns, outfile)

    return 0


if __name__ == "__main__":
    exit(_main())

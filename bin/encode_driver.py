#!/usr/bin/env python
"""Encode a cprofile as json."""

import optparse
import pstats

from psi import proftojson

def get_opts():
    parser = optparse.OptionParser()
    parser.add_option('-o', '--output', help='Filename of output file.')
    parser.add_option('-p', '--profile', help='Filename of input profile.')
    opts, _ = parser.parse_args()

    if not opts.output or not opts.profile:
        parser.perror("Profile and outfile filename required.")
    return opts
 

if __name__ == "__main__":
    opts = get_opts()
    with open(opts.output, 'w') as f:
        f.write(proftojson.encode_stats(pstats.Stats(opts.profile)))

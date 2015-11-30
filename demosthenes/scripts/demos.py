#!/usr/bin/env python
import os
import argparse
from ConfigParser import ConfigParser

import ansible

from demosthenes import INVENTORY, DEMOSTHENES_CONFIG

CONFIG_FILE_HEADER = """\
# This ansible config file automatically generated.
# Please don't edit this file, but edit .demosthenes.cfg
"""
    
def write_config(filename, data):
    cparser = ConfigParser()
    for section, options in data.items():
        cparser.add_section(section)
        for opt, val in options:
            cparser.set(section, opt, val)
    with file(filename, 'w') as outfile:
        outfile.write(CONFIG_FILE_HEADER)
        cparser.write(outfile)
        

parser = argparse.ArgumentParser()
parser.add_argument('project_dir', default=os.curdir)
args = parser.parse_args()

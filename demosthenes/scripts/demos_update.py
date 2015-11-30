#!/usr/bin/env python
import os
import argparse
import subprocess

from demosthenes import INVENTORY, DEMOSTHENES_CONFIG


GIT_URI_PREFIX = 'git@github.com'

DEBOPS_GIT_URI = '%s:debops' % GIT_URI_PREFIX
DEMOS_GIT_URI = '%s:umeboshi2' % GIT_URI_PREFIX

GALAXY_REQS = 'galaxy/requirements.txt'

GALAXY_ACCOUNT_DEBOPS = 'debops'
GALAXY_ACCOUNT_DEMOS = 'umeboshi2'

def fetch_or_clone_role(roles_path, role_name, count):
    role_name_parts = role_name.strip().split()
    if len(role_name_parts) == 1:
        role_name = role_name_parts[0]
        role_version = 'master'
    elif len(role_name_parts) > 1:
        role_name, role_version = role_name_parts[:2]
    else:
        msg = "Problem parsing galaxy requirement %s" % role_name
        raise RuntimeError, msg
    

def main():
    orig_project_root = args.project_dir
    project_root = os.path.abspath(args.project_dir)
    config_path = os.path.join(project_root, DEMOSTHENES_CONFIG)
    if os.path.exists(config_path):
        raise RuntimeError, "%s exists." % config_path

    for skel_path in SKEL_PATHS:
        abspath = os.path.join(project_root, skel_path)
        if not os.path.isdir(abspath):
            os.makedirs(abspath)

    write_config_files(project_root)
    return 0

    
parser = argparse.ArgumentParser()
parser.add_argument('project_dir', default=os.curdir)
args = parser.parse_args()

#!/usr/bin/env python
import os
import argparse
import subprocess

from demosthenes import INVENTORY, DEMOSTHENES_CONFIG

SKEL_PATHS = [
    os.path.join('ansible', INVENTORY, 'group_vars', 'all'),
    os.path.join('ansible', INVENTORY, 'host_vars'),
    os.path.join('ansible', 'playbooks'),
    os.path.join('ansible', 'roles'),
]

DEFAULT_CONFIG = """\
# -*- conf -*-
# FIXME, need better section name
[repos]
;playbooks_repo:  https://github.com/debops/debops-playbooks.git
;playbooks_dirname: debops-playbooks

[paths]
;data-home: /var/lib/demosthenes

[ansible defaults]
;callback_plugins = /path/to/plugins/callback
;roles_path = /path/to/roles

[ansible paramiko]
;record_host_keys = True

[ansible ssh_connection]
;ssh_args = -o ControlMaster=auto -o ControlPersist=60s
"""

# emacs, vim, $EDITOR ignores belong in
# global gitignore
DEFAULT_GITIGNORE = """\
ansible/{SECRET_NAME}
{SECRET_NAME}
{ENCFS_PREFIX}{SECRET_NAME}
ansible.cfg

#-- python
*.py[co]
"""

HOSTS_FILE_HEADER = """\
# This is an Ansible inventory file.

# List your hosts here.  Read about section headers here: #FIXME
"""

HOSTS_FILE_CONTENT = """\
# Uncomment below to use this machine as a controller.
[ansible_controllers]
#%s ansible_connection=local
"""

def write_file(filename, content):
    if not os.path.isfile(filename):
        with file(filename, 'w') as outfile:
            outfile.write(content)

def write_config_files(project_root):
    config_name = os.path.join(project_root, '.demosthenes.cfg')
    write_file(config_name, DEFAULT_CONFIG)
    ignore_name = os.path.join(project_root, '.gitignore')
    write_file(ignore_name, DEFAULT_GITIGNORE)
    hosts_name = os.path.join(project_root, 'ansible', INVENTORY, 'hosts')
    content = HOSTS_FILE_HEADER + HOSTS_FILE_CONTENT
    write_file(hosts_name, content)
    
    

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

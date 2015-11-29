#!/usr/bin/env python
import os
import subprocess

from demosthenes import INVENTORY

SKEL_PATHS = [
    os.path.join('ansible', INVENTORY, 'group_vars', 'all'),
    os.path.join('ansible', INVENTORY, 'host_vars'),
    os.path.join('ansible', 'playbooks'),
    os.path.join('ansible', 'roles'),
]

DEFAULT_CONFIG = """\
# -*- conf -*-
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
    

def main(project_root):
    print "Hello world"
    

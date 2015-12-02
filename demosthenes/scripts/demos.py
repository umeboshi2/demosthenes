#!/usr/bin/env python
import os, sys
import argparse
from ConfigParser import ConfigParser
import subprocess

import ansible

from demosthenes import INVENTORY, DEMOSTHENES_CONFIG, ANSIBLE_CONFIG_FILE
from demosthenes import INSECURE
from demosthenes import find_demosthenes_project, read_config
from demosthenes import find_playbook_path, find_inventory_path


pjoin = os.path.join

CONFIG_FILE_HEADER = """\
# This ansible config file automatically generated.
# Please don't edit this file, but edit .demosthenes.cfg
"""

PLUGIN_TYPES = ['action', 'callback', 'connection', 'filter',
                'lookup', 'vars']

PATHSEP = ':'


def write_config(filename, data):
    cparser = ConfigParser()
    for section, options in data.items():
        cparser.add_section(section)
        for opt, val in options.items():
            cparser.set(section, opt, val)
    with file(filename, 'w') as outfile:
        outfile.write(CONFIG_FILE_HEADER)
        cparser.write(outfile)


def generate_roles_paths(default_path, project_root, playbooks_path):
    paths = [default_path,
             pjoin(project_root, 'roles'),
             pjoin(project_root, 'ansible', 'roles'),
             pjoin(playbooks_path, '..', 'roles'),
             pjoin(playbooks_path, 'roles'),
             '/etc/ansible/roles',
             ]
    return PATHSEP.join(filter(None, paths))


# config is nested dictionary a'la ConfigParser
def generate_ansible_config(filename, config, project_root,
                            playbooks_path, inventory_path):
    # function to generate ansible cfg file
    def custom_ansible_paths(plugtype):
        if plugtype in defaults:
            # prepend value from .demosthenes.cfg
            yield defaults[plugtype]
        yield pjoin(project_root, 'ansible', plugtype)
        yield pjoin(playbooks_path, plugtype)
        yield pjoin('/usr/share/ansible', plugtype)
        

    # create custom config for ansible
    cfg = dict()
    # ansible sections are [ansible <section>]
    separator = None
    maxplit = 1
    for section, items in config.items():
        if section.startswith('ansible '):
            newsect = section.split(separator, maxplit)[1]
            cfg[newsect] = items

    # create default options
    defaults = cfg.setdefault('defaults', dict())
    defaults['hostfile'] = inventory_path
    default_path = defaults.get('roles_path')
    defaults['roles_path'] = generate_roles_paths(
        default_path, project_root, playbooks_path)

    for ptype in PLUGIN_TYPES:
        plugin_section = '%s_plugins' % ptype
        defaults[plugin_section] = PATHSEP.join(
            custom_ansible_paths(plugin_section))

    defaults['library'] = PATHSEP.join(custom_ansible_paths('library'))
    print "WRITE_CONFIG", filename
    write_config(filename, cfg)
    

def main():
    args = sys.argv[1:]
    #print "hello world", args
    project_root = find_demosthenes_project(required=True)
    #print "project_root", project_root
    config = read_config(project_root)
    #print "Config", config
    playbooks_path = find_playbook_path(config, project_root, required=True)
    #print "Playbooks_Path", playbooks_path

    # FIXME make sure ansible-playbook exists?

    inventory_path = find_inventory_path(project_root)
    print "INVENTORY_PATH", inventory_path
    os.environ['ANSIBLE_HOSTS'] = inventory_path

    ansible_config_file = pjoin(project_root, ANSIBLE_CONFIG_FILE)
    os.environ['ANSIBLE_CONFIG'] = os.path.abspath(ansible_config_file)

    # actually create the ansible_config_file
    generate_ansible_config(ansible_config_file, config,
                            project_root, playbooks_path, inventory_path)
    
    
    # make local find_playbook function
    def find_playbook(playbook):
        path_choices = [
            (project_root, 'playbooks', playbook),
            (project_root, 'ansible', 'playbooks', playbook),
            (playbooks_path, playbook),]
        for fragments in path_choices:
            filename = pjoin(*fragments)
            if os.path.isfile(filename):
                return filename
            
    
    # see if a playbook was specified as the
    # first argument.
    play = None
    if len(args) > 0:
        maybe_play = args[0]
        if os.path.isfile(maybe_play):
            play = maybe_play
        else:
            play = find_playbook('%s.yml' % maybe_play)
        if play is not None:
            args.pop(0)
    if play is None:
        play = find_playbook('site.yml')

    print "Running ansible plabybook from", play, '...'
    
    try:
        retcode = subprocess.call(['ansible-playbook', play] + args)
        sys.exit(retcode)
    except KeyboardInterrupt:
        raise KeyboardInterrupt
    
    
#parser = argparse.ArgumentParser()
#parser.add_argument('project_dir', default=os.curdir)
#args = parser.parse_args()

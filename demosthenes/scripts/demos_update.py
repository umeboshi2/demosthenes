#!/usr/bin/env python
import os
import argparse
import subprocess

from demosthenes import INVENTORY, DEMOSTHENES_CONFIG
from demosthenes import find_demosthenes_project, find_playbook_path
from demosthenes import read_config

pjoin = os.path.join


GIT_URI_PREFIX = 'git@github.com'

DEBOPS_GIT_URI = '%s:debops' % GIT_URI_PREFIX
DEMOS_GIT_URI = '%s:umeboshi2' % GIT_URI_PREFIX

GALAXY_REQS = 'galaxy/requirements.txt'

GALAXY_ACCOUNT_DEBOPS = 'debops'
GALAXY_ACCOUNT_DEMOS = 'umeboshi2'

SITE_PLAYBOOK = pjoin('playbooks', 'site.yml')


def clone_repo(uri, branch, dest):
    subprocess.check_call(['git', 'clone', '--quiet', '--branch',
                           branch, uri, dest])

def update_repo(path):
    prefix = ['git', '-C', path]
    current_sha_cmd = prefix + ['rev-parse', 'HEAD']
    current_sha = subprocess.check_output(current_sha_cmd).strip()
    subprocess.check_call(prefix + ['fetch', '--quiet'])
    upstream_sha_cmd = prefix + ['rev-parse', 'FETCH_HEAD']
    upstream_sha = subprocess.check_output(upstream_sha_cmd).strip()
    if current_sha != upstream_sha:
        subprocess.check_call(prefix + ['merge', upstream_sha])


def get_role_name_version(role_name):
    role_name_parts = role_name.strip().split()
    if len(role_name_parts) == 1:
        role_name = role_name_parts[0]
        role_version = 'master'
    elif len(role_name_parts) > 1:
        role_name, role_version = role_name_parts[:2]
    else:
        msg = "Problem parsing galaxy requirement %s" % role_name
        raise RuntimeError, msg
    return role_name, role_version

def fetch_or_clone_role(roles_path, role_name, count):
    role_name, role_version = get_role_name_version(role_name)
    print role_name, role_version
    if role_name.startswith('debops.'):
        galaxy_name = role_name
        role_name = role_name.split('.', 1)[1]
    else:
        galaxy_name = 'debops.%s' % role_name
    print "GALAXY_NAME, ROLE_NAME", galaxy_name, role_name
    remote_uri = 'foobar'
    
    

def setup_project(project_dir):
    if project_dir is None:
        return None, None
    if not os.path.isdir(project_dir):
        print "Creating project directory in", project_dir
        os.makedirs(project_dir)
    # if project_dir is specified, install
    # the playbooks in that directory
    install_path = pjoin(project_dir, 'demos-playbooks')
    install_playbooks = True
    if os.path.isfile(pjoin(install_path, SITE_PLAYBOOK)):
        install_playbooks = False
    return install_path, install_playbooks

            
def setup_playbooks(install_path, playbooks_path, install_playbooks):
    uri = pjoin(DEMOS_GIT_URI, 'debops-playbooks.git')
    if not playbooks_path:
        print "Standard playbooks not there.  Installing to", install_path
        clone_repo(uri, 'master', install_path)
    else:
        print "Standard playbooks found here", install_path
        if install_playbooks:
            print "Install_Playbooks here", install_path
            clone_repo(uri, 'master', install_path)
        else:
            update_repo(install_path)
    return pjoin(install_path, 'demos-playbooks')

        
def setup_roles_orig(roles_path, requirements_file):
    with file(requirements_file) as infile:
        reqs = [line.strip() for line in infile]
    total_roles = len(reqs)
    for count, role_name in enumerate(reqs, 1):
        fetch_or_clone_role(roles_path, role_name, count)

def setup_roles(roles_path, requirements_file):
    print "REQUIREMENTS_FILE", requirements_file
    print "ISFILE", os.path.isfile(requirements_file)
    cmd = ['ansible-galaxy', 'install', '-r', requirements_file,
           '-p', roles_path]
    # FIXME ansible-galaxy needs to be smarter
    if True:
        cmd += ['--force']
    print "CMD", ' '.join(cmd)
    subprocess.check_call(cmd)
    

    
def main():
    print "Hello there"
    parser = argparse.ArgumentParser()
    parser.add_argument('project_dir', default=None, nargs='?')
    args = parser.parse_args()
    install_path, install_playbooks = setup_project(args.project_dir)
    print "install_path, install_playbooks", install_path, install_playbooks
    playbooks_path = install_playbooks or install_path
    print "playbooks_path", playbooks_path
    if install_path is None:
        project_root = find_demosthenes_project(required=False)
        config = read_config(project_root)
        playbooks_path = find_playbook_path(config,
                                            project_root, required=False)
        if playbooks_path:
            install_path = os.path.dirname(playbooks_path)
        else:
            install_path = config['paths']['install-path']
    setup_playbooks(install_path,
                    playbooks_path, install_playbooks)
    roles_path = pjoin(install_path, 'roles')
    setup_roles(roles_path, pjoin(install_path, 'galaxy/requirements.yml'))
        
    return 0

    
